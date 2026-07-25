"""Safe loaders and fail-closed validation for AGM vNext policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import RISK_RANK, VNextError, fingerprint


KNOWN_NON_TRANSITION_ACTIONS = {
    "open_case",
    "prepare_evidence",
    "ask_clarification",
    "invalidate_attestation",
    "record_policy_conflict",
    "resolve_policy_conflict",
    "record_closure",
}
SELECTOR_KEYS = {"paths", "change_types", "semantic_targets", "governance_entrypoint"}


@dataclass(frozen=True)
class VNextConfig:
    root: Path
    manifest: dict[str, Any]
    documents: dict[str, dict[str, Any]]
    risk_rules: list[dict[str, Any]]
    fallback_rule: dict[str, Any]
    obligations: dict[str, dict[str, Any]]
    interaction_rules: list[dict[str, Any]]
    autonomy_profiles: dict[str, dict[str, Any]]
    assurance_profiles: dict[str, dict[str, Any]]
    roles: dict[str, dict[str, Any]]
    permissions: dict[str, set[str]]
    state_machine: dict[str, Any]
    interfaces: dict[str, dict[str, Any]]
    policy_fingerprint: str
    source_paths: list[str]


def normalize_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def safe_project_path(root: Path, relative: str | Path) -> Path:
    normalized = normalize_path(relative)
    candidate = (root / normalized).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise VNextError(f"Policy reference escapes project root: {relative}")
    return candidate


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise VNextError(f"Required vNext policy file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise VNextError(f"Malformed YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise VNextError(f"Expected YAML mapping in {path}")
    schema = data.get("schema_version")
    if not isinstance(schema, str) or not schema.endswith("/v0.2-dev"):
        raise VNextError(f"Development policy file has invalid schema_version: {path}")
    return data


def index_by_id(items: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        raise VNextError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise VNextError(f"{label} entry must have a non-empty string id")
        item_id = item["id"]
        if item_id in result:
            raise VNextError(f"Duplicate {label} id: {item_id}")
        result[item_id] = item
    return result


def _validate_obligations(
    obligations: dict[str, dict[str, Any]],
    roles: dict[str, dict[str, Any]],
) -> None:
    valid_types = {"evidence", "human_attestation", "maintainer_verification"}
    for obligation_id, item in obligations.items():
        if item.get("type") not in valid_types:
            raise VNextError(f"Obligation {obligation_id} has unknown type")
        if item.get("severity") not in RISK_RANK:
            raise VNextError(f"Obligation {obligation_id} has unknown severity")
        if not isinstance(item.get("blocking"), bool):
            raise VNextError(f"Obligation {obligation_id} blocking must be boolean")
        if not isinstance(item.get("evidence_type"), str) or not item["evidence_type"]:
            raise VNextError(f"Obligation {obligation_id} requires evidence_type")
        verifier_roles = item.get("verifier_roles")
        if not isinstance(verifier_roles, list) or not verifier_roles:
            raise VNextError(f"Obligation {obligation_id} requires verifier_roles")
        unknown = sorted(set(verifier_roles) - set(roles))
        if unknown:
            raise VNextError(
                f"Obligation {obligation_id} references unknown verifier roles: {', '.join(unknown)}"
            )


def _validate_obligation_references(
    owner: str,
    obligation_ids: Any,
    obligations: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(obligation_ids, list):
        raise VNextError(f"{owner} obligation_ids must be a list")
    unknown = sorted(set(obligation_ids) - set(obligations))
    if unknown:
        raise VNextError(f"{owner} references unknown obligations: {', '.join(unknown)}")


def _validate_risk_rules(
    rules: dict[str, dict[str, Any]],
    obligations: dict[str, dict[str, Any]],
) -> None:
    for rule_id, item in rules.items():
        if item.get("risk_level") not in RISK_RANK:
            raise VNextError(f"Risk rule {rule_id} has unknown risk level")
        if not isinstance(item.get("zone"), str) or not item["zone"]:
            raise VNextError(f"Risk rule {rule_id} requires zone")
        selectors = item.get("selectors")
        if not isinstance(selectors, dict) or not selectors:
            raise VNextError(f"Risk rule {rule_id} requires selectors")
        unknown_selector_keys = set(selectors) - SELECTOR_KEYS
        if unknown_selector_keys:
            raise VNextError(
                f"Risk rule {rule_id} has unknown selectors: {', '.join(sorted(unknown_selector_keys))}"
            )
        if not any(
            value is True or (isinstance(value, list) and value)
            for value in selectors.values()
        ):
            raise VNextError(f"Risk rule {rule_id} has no active selector")
        for key in {"paths", "change_types", "semantic_targets"} & set(selectors):
            if not isinstance(selectors[key], list) or not all(
                isinstance(value, str) and value for value in selectors[key]
            ):
                raise VNextError(f"Risk rule {rule_id} selector {key} must be a string list")
        if "governance_entrypoint" in selectors and not isinstance(
            selectors["governance_entrypoint"], bool
        ):
            raise VNextError(
                f"Risk rule {rule_id} governance_entrypoint selector must be boolean"
            )
        _validate_obligation_references(
            f"Risk rule {rule_id}", item.get("obligation_ids", []), obligations
        )
        overrides = item.get("obligation_overrides", {})
        if not isinstance(overrides, dict):
            raise VNextError(f"Risk rule {rule_id} obligation_overrides must be a mapping")
        unknown_override_ids = sorted(set(overrides) - set(item.get("obligation_ids", [])))
        if unknown_override_ids:
            raise VNextError(
                f"Risk rule {rule_id} overrides unreferenced obligations: "
                f"{', '.join(unknown_override_ids)}"
            )


def _validate_profiles(
    profiles: dict[str, dict[str, Any]],
    label: str,
    obligations: dict[str, dict[str, Any]],
) -> None:
    for profile_id, item in profiles.items():
        _validate_obligation_references(
            f"{label} {profile_id}", item.get("obligation_ids", []), obligations
        )
        parent = item.get("extends")
        if parent is not None and parent not in profiles:
            raise VNextError(f"{label} {profile_id} extends unknown profile {parent}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(profile_id: str) -> None:
        if profile_id in visiting:
            raise VNextError(f"Cyclic {label} inheritance involving {profile_id}")
        if profile_id in visited:
            return
        visiting.add(profile_id)
        parent = profiles[profile_id].get("extends")
        if parent:
            visit(parent)
        visiting.remove(profile_id)
        visited.add(profile_id)

    for profile_id in profiles:
        visit(profile_id)


def expanded_profile(
    profiles: dict[str, dict[str, Any]],
    profile_id: str,
) -> dict[str, Any]:
    if profile_id not in profiles:
        raise VNextError(f"Unknown profile: {profile_id}")
    item = dict(profiles[profile_id])
    parent = item.get("extends")
    if not parent:
        item["obligation_ids"] = list(dict.fromkeys(item.get("obligation_ids", [])))
        return item
    inherited = expanded_profile(profiles, parent)
    merged = {**inherited, **item}
    merged["obligation_ids"] = list(
        dict.fromkeys(inherited.get("obligation_ids", []) + item.get("obligation_ids", []))
    )
    return merged


def _validate_state_machine(
    state_machine: dict[str, Any],
    roles: dict[str, dict[str, Any]],
    permissions: dict[str, set[str]],
) -> None:
    states_raw = state_machine.get("states")
    if not isinstance(states_raw, list) or not states_raw:
        raise VNextError("State machine requires states")
    if len(states_raw) != len(set(states_raw)):
        raise VNextError("State machine contains duplicate states")
    states = set(states_raw)
    if state_machine.get("initial_state") not in states:
        raise VNextError("State machine initial_state is unknown")
    terminal_states = state_machine.get("terminal_states")
    if not isinstance(terminal_states, list) or not set(terminal_states) <= states:
        raise VNextError("State machine terminal_states contain unknown states")
    transitions = state_machine.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        raise VNextError("State machine requires transitions")
    seen: set[tuple[str, str]] = set()
    for item in transitions:
        if not isinstance(item, dict):
            raise VNextError("State transition must be a mapping")
        action = item.get("action")
        sources = item.get("from")
        target = item.get("to")
        transition_roles = item.get("roles")
        if not isinstance(action, str) or not action:
            raise VNextError("State transition requires action")
        if not isinstance(sources, list) or not sources or not set(sources) <= states:
            raise VNextError(f"Transition {action} has unknown source state")
        if target not in states:
            raise VNextError(f"Transition {action} has unknown target state")
        if not isinstance(transition_roles, list) or not transition_roles:
            raise VNextError(f"Transition {action} requires roles")
        unknown_roles = sorted(set(transition_roles) - set(roles))
        if unknown_roles:
            raise VNextError(
                f"Transition {action} references unknown roles: {', '.join(unknown_roles)}"
            )
        for source in sources:
            key = (action, source)
            if key in seen:
                raise VNextError(f"Duplicate transition {action} from {source}")
            seen.add(key)
        for role in transition_roles:
            if action not in permissions.get(role, set()):
                raise VNextError(
                    f"Transition {action} grants role {role} without matching permission"
                )


def load_vnext_config(root: Path) -> VNextConfig:
    root = root.resolve()
    manifest_path = root / ".agm" / "manifest.yml"
    manifest = load_yaml_mapping(manifest_path)
    vnext = manifest.get("vnext")
    if not isinstance(vnext, dict) or vnext.get("schema_version") != "agm.vnext_config/v0.2-dev":
        raise VNextError("Manifest is missing vNext development configuration")
    references = vnext.get("policy_references")
    if not isinstance(references, dict):
        raise VNextError("Manifest vNext policy_references must be a mapping")

    required_references = {
        "risk_rules",
        "evidence_profiles",
        "interaction_rules",
        "autonomy_profiles",
        "assurance_profiles",
        "roles",
        "permissions",
        "state_machine",
        "contributor_panel",
        "maintainer_panel",
        "governance_report",
        "messages",
        "agent_entrypoints",
    }
    missing_references = sorted(required_references - set(references))
    if missing_references:
        raise VNextError(
            f"Manifest missing vNext policy references: {', '.join(missing_references)}"
        )

    documents: dict[str, dict[str, Any]] = {"manifest": manifest}
    source_paths = [".agm/manifest.yml"]
    for key in sorted(required_references):
        relative = normalize_path(references[key])
        documents[key] = load_yaml_mapping(safe_project_path(root, relative))
        source_paths.append(relative)

    roles = index_by_id(documents["roles"].get("roles"), "role")
    for role_id, item in roles.items():
        if not isinstance(item.get("human"), bool):
            raise VNextError(f"Role {role_id} must declare human as boolean")

    obligation_map = index_by_id(
        documents["evidence_profiles"].get("obligations"), "obligation"
    )
    _validate_obligations(obligation_map, roles)

    risk_rule_map = index_by_id(documents["risk_rules"].get("risk_rules"), "risk rule")
    _validate_risk_rules(risk_rule_map, obligation_map)
    fallback = documents["risk_rules"].get("fallback")
    if not isinstance(fallback, dict) or not isinstance(fallback.get("rule_id"), str):
        raise VNextError("Risk policy requires a fallback rule")
    if fallback.get("risk_level") not in RISK_RANK:
        raise VNextError("Fallback rule has unknown risk level")
    _validate_obligation_references(
        "Fallback rule", fallback.get("obligation_ids", []), obligation_map
    )

    interactions = index_by_id(
        documents["interaction_rules"].get("interaction_rules"), "interaction rule"
    )
    for interaction_id, item in interactions.items():
        trigger_ids = item.get("all_rule_ids")
        if not isinstance(trigger_ids, list) or len(trigger_ids) < 2:
            raise VNextError(
                f"Interaction rule {interaction_id} requires at least two all_rule_ids"
            )
        unknown_rules = sorted(set(trigger_ids) - set(risk_rule_map))
        if unknown_rules:
            raise VNextError(
                f"Interaction rule {interaction_id} references unknown rules: "
                f"{', '.join(unknown_rules)}"
            )
        if item.get("risk_level") not in RISK_RANK:
            raise VNextError(f"Interaction rule {interaction_id} has unknown risk level")
        _validate_obligation_references(
            f"Interaction rule {interaction_id}",
            item.get("obligation_ids", []),
            obligation_map,
        )

    autonomy_profiles = index_by_id(
        documents["autonomy_profiles"].get("autonomy_profiles"), "autonomy profile"
    )
    assurance_profiles = index_by_id(
        documents["assurance_profiles"].get("assurance_profiles"), "assurance profile"
    )
    _validate_profiles(autonomy_profiles, "Autonomy profile", obligation_map)
    _validate_profiles(assurance_profiles, "Assurance profile", obligation_map)

    permissions_raw = documents["permissions"].get("permissions")
    if not isinstance(permissions_raw, dict):
        raise VNextError("Permissions must be a mapping")
    unknown_permission_roles = sorted(set(permissions_raw) - set(roles))
    if unknown_permission_roles:
        raise VNextError(
            f"Permissions reference unknown roles: {', '.join(unknown_permission_roles)}"
        )
    permissions: dict[str, set[str]] = {}
    for role_id in roles:
        actions = permissions_raw.get(role_id, [])
        if not isinstance(actions, list) or not all(
            isinstance(action, str) and action for action in actions
        ):
            raise VNextError(f"Permissions for {role_id} must be a string list")
        if len(actions) != len(set(actions)):
            raise VNextError(f"Permissions for {role_id} contain duplicates")
        permissions[role_id] = set(actions)

    state_machine = documents["state_machine"]
    _validate_state_machine(state_machine, roles, permissions)
    known_actions = {
        item["action"] for item in state_machine["transitions"]
    } | KNOWN_NON_TRANSITION_ACTIONS
    for role_id, actions in permissions.items():
        unknown_actions = sorted(actions - known_actions)
        if unknown_actions:
            raise VNextError(
                f"Role {role_id} has unknown permissions: {', '.join(unknown_actions)}"
            )

    interfaces = {
        key: documents[key]
        for key in {
            "contributor_panel",
            "maintainer_panel",
            "governance_report",
            "messages",
        }
    }
    messages = documents["messages"].get("messages")
    if not isinstance(messages, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in messages.items()
    ):
        raise VNextError("Interface messages must be a string mapping")
    entrypoints = documents["agent_entrypoints"]
    for group_name in ("protocols", "skills"):
        references_group = entrypoints.get(group_name)
        if not isinstance(references_group, dict):
            raise VNextError(f"Agent entrypoints {group_name} must be a mapping")
        for label, relative in references_group.items():
            if not isinstance(relative, str) or not safe_project_path(
                root, relative
            ).is_file():
                raise VNextError(
                    f"Agent entrypoint {group_name}.{label} references a missing file"
                )
    policy_payload = {
        key: documents[key]
        for key in sorted(documents)
        if key != "manifest"
    }
    policy_payload["manifest_vnext"] = vnext

    return VNextConfig(
        root=root,
        manifest=manifest,
        documents=documents,
        risk_rules=list(risk_rule_map.values()),
        fallback_rule=fallback,
        obligations=obligation_map,
        interaction_rules=list(interactions.values()),
        autonomy_profiles=autonomy_profiles,
        assurance_profiles=assurance_profiles,
        roles=roles,
        permissions=permissions,
        state_machine=state_machine,
        interfaces=interfaces,
        policy_fingerprint=fingerprint(policy_payload),
        source_paths=source_paths,
    )
