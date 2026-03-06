# System productivity and error reports on iPhone
_Exported on 3/5/2026 at 17:54:23 GMT+8 from Cursor (2.5.25)_

---

**User**

is there a way that i can get system productivity and error reports on my phone? app? email. iphone? look: @docs/DOCS_INDEX.md 



---

**Cursor**


Checking the production-alerts workflow and how reports/notifications are delivered:



Checking whether the observability workflow or any script sends reports via email or another channel:



Here’s how you can get **system productivity and error reports on your phone** with what’s already in the repo, plus one optional improvement.

---

## 1. **Email (easiest — use GitHub)**

Your docs already describe this in [docs/BRANCH_PROTECTION_REQUIREMENTS.md](docs/BRANCH_PROTECTION_REQUIREMENTS.md):

- In **GitHub**: **Settings → Notifications** (or [github.com/settings/notifications](https://github.com/settings/notifications)).
- Turn **Email** on for **Actions** (workflow runs).
- For this repo: set watch to **Custom → Actions** so you get notified when workflows run (and fail).

When a workflow fails, GitHub sends an email. You’ll get those on your **iPhone** (or any device) in whatever app you use for that email (Mail, Gmail, etc.). That’s your main way to get **error reports** on your phone today.

---

## 2. **iPhone app — GitHub app**

- Install the **GitHub** app on your iPhone.
- Turn on **push notifications** for this repo (e.g. Issues, or “Custom” and then Actions/Issues as you prefer).

The repo’s [production-alerts workflow](.github/workflows/production-alerts.yml) **opens a GitHub Issue** (with label `production-alert`) whenever any of these fail:

- Core tests  
- Release gates  
- Pearl News gates  
- Teacher gates  
- Brand guards  
- Docs CI  
- Simulation 10k  
- Production observability  

So you’ll get **error reports on your phone** as issue notifications in the GitHub app (and optionally by email as above).

---

## 3. **What’s not there yet**

- There is **no Phoenix-specific iPhone app** in the docs; the control plane is the **Mac app + Streamlit**.
- Workflows do **not** send email/Slack/webhooks themselves; they only create **issues** and upload **artifacts**. So:
  - **Productivity/health “digests”** (e.g. daily/weekly summary of runs, pass/fail, KPIs) are **not** emailed or pushed to your phone by the current setup.
  - You only get **failure** visibility via GitHub (issues + optional email/push from GitHub).

---

## Summary

| What you want              | How to get it on your phone                          |
|----------------------------|------------------------------------------------------|
| **Error reports**          | GitHub **email** for Actions + **GitHub iPhone app** for issue (production-alert) notifications. |
| **Productivity / health**  | No built-in email or app; you’d add a step (e.g. scheduled job that emails a summary or posts to Slack). |

So: **yes** — you can get **system error reports** on your phone via **email** (GitHub notifications) and the **GitHub iPhone app** (for the production-alert issues). **Productivity/health reports** (e.g. daily digest) would need a new small piece (e.g. a workflow step that sends email or calls a webhook). I can outline that next if you want.

---

**User**

document everything use @docs/DOCS_INDEX.md 

---

**Cursor**


Checking the Document all — usage and complete inventory sections and listing `scripts/video/` and related docs:



Checking the rest of the complete inventory for a Video pipeline scripts subsection and the domain table:



Updating DOCS_INDEX per "Document all — usage": adding the missing video script to the Video pipeline section and to the complete inventory; adding a Video pipeline domain row; and ensuring the doc date is correct.



Checking whether all video-related docs are listed in the complete inventory:



Adding the remaining video docs to the complete inventory.



Verifying the video doc paths exist:



Marking `flux_shnell_research.rtf` as missing in the inventory.


