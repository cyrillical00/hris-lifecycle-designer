# HRIS Lifecycle Designer

Visual configurator for Joiner/Mover/Leaver (JML) automation flows from HRIS → Okta → downstream SaaS apps. Validates provisioning logic and exports production-ready runbooks and JSON configs.

Demonstrates ADP → Okta HR-mastered lifecycle automation covering 900 employees.

![Screenshot placeholder](screenshot.png)

## Features

- HRIS source selector (ADP, Workday, BambooHR, Rippling, Custom)
- Identity platform selector (Okta SCIM, Okta HR-mastered, Azure AD, Custom)
- Per-tab Joiner / Mover / Leaver flow configurators with live visual preview
- Color-coded step diagrams (green = Joiner, amber = Mover, red = Leaver)
- Validation checklist with actionable fix recommendations
- "Load Life360 Example" pre-fill button
- Markdown runbook export + JSON config export

## Local Setup

```bash
git clone https://github.com/cyrillical00/hris-lifecycle-designer
cd hris-lifecycle-designer
pip install -r requirements.txt
streamlit run app.py
```

No API keys required — deploy directly.

## Deploy to Streamlit Cloud

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

---

Built by [Oleg Strutsovski](https://linkedin.com/in/olegst)
