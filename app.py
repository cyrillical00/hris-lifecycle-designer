import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="HRIS Lifecycle Designer", page_icon="👤", layout="wide")

st.sidebar.markdown("## 👤 HRIS Lifecycle Designer")
st.sidebar.markdown("Configure JML automation flows and export production-ready runbooks.")
st.sidebar.markdown("---")
st.sidebar.subheader("Environment Configuration")

HRIS_OPTIONS = ["ADP Workforce Now", "Workday", "BambooHR", "Rippling", "Custom"]
IDENTITY_OPTIONS = [
    "Okta (SCIM)", "Okta (HR-mastered provisioning)", "Azure AD", "Custom"
]
APP_OPTIONS = [
    "Google Workspace", "Slack Enterprise Grid", "GitHub Enterprise",
    "Salesforce", "Jira/Confluence", "Box", "Zoom", "Custom",
]
OKTA_ACTIONS = [
    "Create user", "Activate user", "Update profile",
    "Move to new group", "Suspend", "Deactivate", "Delete",
]
APP_ACTIONS = ["provision", "update", "deprovision", "notify"]

LIFE360_DEFAULTS = {
    "hris": "ADP Workforce Now",
    "identity": "Okta (HR-mastered provisioning)",
    "apps": ["Google Workspace", "Slack Enterprise Grid", "GitHub Enterprise", "Jira/Confluence", "Box", "Zoom"],
}

if "prefilled" not in st.session_state:
    st.session_state.prefilled = False

if st.sidebar.button("Load Life360 Example"):
    st.session_state.prefilled = True

pf = st.session_state.prefilled

hris = st.sidebar.selectbox(
    "HRIS source", HRIS_OPTIONS,
    index=HRIS_OPTIONS.index(LIFE360_DEFAULTS["hris"]) if pf else 0,
)
identity = st.sidebar.selectbox(
    "Identity platform", IDENTITY_OPTIONS,
    index=IDENTITY_OPTIONS.index(LIFE360_DEFAULTS["identity"]) if pf else 0,
)
downstream_apps = st.sidebar.multiselect(
    "Downstream apps", APP_OPTIONS,
    default=LIFE360_DEFAULTS["apps"] if pf else [],
)

st.title("HRIS Lifecycle Designer")
if downstream_apps:
    st.caption(f"{hris} → {identity} → {', '.join(downstream_apps)}")
else:
    st.caption("Select downstream apps in the sidebar to begin.")


def flow_step(number, title, detail, color):
    return (
        f'<div style="display:flex;align-items:flex-start;margin-bottom:12px;">'
        f'<div style="background:{color};color:#fff;border-radius:50%;width:30px;height:30px;'
        f'display:flex;align-items:center;justify-content:center;font-weight:bold;'
        f'flex-shrink:0;font-family:monospace;font-size:0.85em;">{number}</div>'
        f'<div style="margin-left:12px;background:#1E293B;border-left:3px solid {color};'
        f'padding:10px 14px;border-radius:4px;flex:1;">'
        f'<div style="font-weight:bold;color:{color};font-family:monospace;margin-bottom:4px;">{title}</div>'
        f'<div style="color:#CBD5E1;font-size:0.88em;font-family:monospace;">{detail}</div>'
        f'</div></div>'
    )


def render_flow_tab(tab_key, trigger_desc, color, default_okta_action, default_app_action):
    left, right = st.columns([4, 6])

    with left:
        st.markdown(f"**Trigger event:** {trigger_desc}")
        timing_val = st.number_input(
            "Timing offset", min_value=0, value=0, key=f"timing_val_{tab_key}"
        )
        timing_unit = st.selectbox(
            "Unit", ["days before trigger", "days after trigger"], key=f"timing_unit_{tab_key}"
        )
        okta_idx = OKTA_ACTIONS.index(default_okta_action) if default_okta_action in OKTA_ACTIONS else 0
        okta_action = st.selectbox(
            "Okta action", OKTA_ACTIONS, index=okta_idx, key=f"okta_action_{tab_key}"
        )
        group_rules = st.text_area(
            "Group assignment rules",
            key=f"group_rules_{tab_key}",
            placeholder="e.g. Assign to department group + location group + role group",
        )

        app_actions = {}
        if downstream_apps:
            st.markdown("**Downstream app actions:**")
            for app in downstream_apps:
                cols = st.columns([3, 2, 2])
                cols[0].markdown(f"**{app}**")
                app_idx = APP_ACTIONS.index(default_app_action) if default_app_action in APP_ACTIONS else 0
                action = cols[1].selectbox(
                    "Action", APP_ACTIONS, index=app_idx, key=f"app_action_{tab_key}_{app}"
                )
                offset = cols[2].number_input(
                    "Days", min_value=0, value=0, key=f"app_offset_{tab_key}_{app}"
                )
                app_actions[app] = {"action": action, "offset": offset}

    with right:
        st.markdown("**Flow Preview**")
        steps_html = ""
        steps_html += flow_step(
            1, "HRIS Trigger",
            f"{trigger_desc}<br>{timing_val} {timing_unit}",
            color,
        )
        steps_html += flow_step(
            2, identity,
            f"Action: {okta_action}<br>Groups: {group_rules or 'Not configured'}",
            color,
        )
        for i, app in enumerate(downstream_apps):
            info = app_actions.get(app, {})
            steps_html += flow_step(
                i + 3, app,
                f"Action: {info.get('action', '—')} | Offset: {info.get('offset', 0)} days",
                color,
            )
        st.markdown(steps_html, unsafe_allow_html=True)

    return {
        "trigger": trigger_desc,
        "timing": f"{timing_val} {timing_unit}",
        "okta_action": okta_action,
        "group_rules": group_rules,
        "app_actions": app_actions,
    }


tab_j, tab_m, tab_l = st.tabs(["Joiner", "Mover", "Leaver"])

with tab_j:
    joiner = render_flow_tab(
        "joiner",
        "New hire record created in HRIS with start date T",
        "#10B981",
        "Create user",
        "provision",
    )

with tab_m:
    mover = render_flow_tab(
        "mover",
        "Employee record updated — department, title, manager, or location changed",
        "#F59E0B",
        "Update profile",
        "update",
    )

with tab_l:
    leaver = render_flow_tab(
        "leaver",
        "Termination date set in HRIS or employment status = Terminated",
        "#EF4444",
        "Deactivate",
        "deprovision",
    )


# Validation
st.subheader("Validation Checklist")

checks = []

joiner_ok = joiner["okta_action"] in ("Create user", "Activate user")
checks.append((
    joiner_ok, "Joiner",
    "Okta action is 'Create user' or 'Activate user'",
    "Set Joiner Okta action to 'Create user' or 'Activate user'.",
))

leaver_ok = leaver["okta_action"] in ("Suspend", "Deactivate")
leaver_fix = ""
if leaver["okta_action"] == "Delete":
    leaver_fix = (
        "Deleting Okta users immediately removes audit trail — "
        "recommend Deactivate + 90-day retention policy."
    )
elif not leaver_ok:
    leaver_fix = "Set Leaver Okta action to 'Suspend' or 'Deactivate'."
checks.append((leaver_ok, "Leaver", "Okta action is 'Suspend' or 'Deactivate' (not Delete)", leaver_fix))

leaver_apps = leaver.get("app_actions", {})
all_deprov = all(v["action"] == "deprovision" for v in leaver_apps.values()) if leaver_apps else True
checks.append((
    all_deprov, "Leaver",
    "All downstream apps have 'deprovision' action",
    "Set all Leaver downstream app actions to 'deprovision'.",
))

mover_groups_ok = bool(mover.get("group_rules", "").strip())
checks.append((
    mover_groups_ok, "Mover",
    "Group assignment rules are non-empty",
    "Add group assignment rules for the Mover tab.",
))

leaver_timing_ok = (
    "before" in leaver.get("timing", "") or leaver.get("timing", "").startswith("0")
)
checks.append((
    leaver_timing_ok, "Leaver",
    "Okta deactivation is same-day or before HRIS termination date",
    "Set Leaver timing offset to 0 or use 'days before trigger'.",
))

gws_check = None
if "Google Workspace" in downstream_apps:
    gws_action = leaver.get("app_actions", {}).get("Google Workspace", {}).get("action", "")
    if gws_action == "deprovision":
        gws_check = (
            False,
            "Google Workspace",
            "Drive data transfer step documented before deprovisioning",
            "GWS deprovisioning without Drive transfer loses user data — "
            "add a Drive transfer step before deprovisioning.",
        )
    else:
        gws_check = (True, "Google Workspace", "Drive data transfer step documented before deprovisioning", "")

if gws_check:
    checks.append(gws_check)

for passed, area, label, fix in checks:
    if passed:
        color = "#10B981"
        icon = "✅"
    else:
        color = "#EF4444"
        icon = "❌"
    st.markdown(
        f'<span style="color:{color};font-family:monospace;">{icon} [{area}] {label}</span>',
        unsafe_allow_html=True,
    )
    if not passed and fix:
        st.caption(f"Fix: {fix}")


# Export
st.subheader("Export")


def build_runbook():
    sections = ["# JML Lifecycle Runbook"]
    sections.append(
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d')}  \n"
        f"**HRIS:** {hris} | **Identity:** {identity}  \n"
        f"**Downstream Apps:** {', '.join(downstream_apps) or 'None'}"
    )
    sections.append("---")

    for flow_name, cfg, label in [("Joiner", joiner, "green"), ("Mover", mover, "amber"), ("Leaver", leaver, "red")]:
        lines = [f"## {flow_name} Flow"]
        lines.append(f"**Trigger:** {cfg['trigger']}  \n**Timing:** {cfg['timing']}")
        lines.append(f"**Okta action:** {cfg['okta_action']}  \n**Group rules:** {cfg['group_rules'] or 'Not configured'}")
        if cfg.get("app_actions"):
            lines.append("**Downstream app actions:**")
            for app, info in cfg["app_actions"].items():
                lines.append(f"- {app}: {info['action']} ({info['offset']} days offset)")
        lines.append("")
        lines.append("**Okta Workflow Trigger Configuration:**")
        lines.append(
            f"- Create an Okta Workflow triggered on the appropriate lifecycle event "
            f"(User Created / User Updated / User Deactivated)."
        )
        lines.append(f"- Use an Okta HR source connector pointing to {hris}.")
        lines.append(
            f"- Apply group assignment rule: {cfg['group_rules'] or 'Define group rules before deploying to production'}."
        )
        lines.append(
            "- For each downstream app, trigger provisioning/deprovisioning via the "
            "app integration after the Okta action completes."
        )
        sections.append("\n".join(lines))

    sections.append("## Validation Results")
    val_lines = []
    for passed, area, label, _ in checks:
        icon = "PASS" if passed else "FAIL"
        val_lines.append(f"- [{icon}] [{area}] {label}")
    sections.append("\n".join(val_lines))

    return "\n\n".join(sections)


col1, col2 = st.columns(2)
with col1:
    runbook_md = build_runbook()
    st.download_button(
        "Download JML Runbook as Markdown",
        data=runbook_md,
        file_name="jml_runbook.md",
        mime="text/markdown",
    )
with col2:
    config_obj = {
        "hris": hris,
        "identity": identity,
        "downstream_apps": downstream_apps,
        "joiner": {k: v for k, v in joiner.items() if k != "app_actions"},
        "joiner_app_actions": joiner.get("app_actions", {}),
        "mover": {k: v for k, v in mover.items() if k != "app_actions"},
        "mover_app_actions": mover.get("app_actions", {}),
        "leaver": {k: v for k, v in leaver.items() if k != "app_actions"},
        "leaver_app_actions": leaver.get("app_actions", {}),
    }
    st.download_button(
        "Download as JSON Config",
        data=json.dumps(config_obj, indent=2),
        file_name="jml_config.json",
        mime="application/json",
    )

st.sidebar.markdown("---")
st.sidebar.markdown("Built by [Oleg Strutsovski](https://linkedin.com/in/olegst)")
