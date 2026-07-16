# Sarah Funnel — Auto-updating dashboard

A public dashboard for the **Sarah AI Hiring Agent** funnel on uplers.com, hosted on
GitHub Pages. A GitHub Action refreshes the whole dashboard every morning using a Google
**service account** for GA4, so it runs on its own — no computer needs to be on. The
lead-quality split (job seekers vs genuine buyers) is pulled automatically from the Sarah
intake API in the same run. Nothing on the page is edited by hand.

## Files

| File | What it is | Who updates it |
|------|-----------|----------------|
| `index.html` | The dashboard. Loads `data.json` and renders the funnel. | Rarely (design only) |
| `data.json` | GA4 traffic numbers **and** the lead-quality split (from the Sarah intake API). | **Automatic** — daily Action |
| `fetch_ga4.py` | Pulls the GA4 numbers + the lead-quality API and writes `data.json`. | — |
| `.github/workflows/update.yml` | Runs `fetch_ga4.py` daily and publishes to Pages. | — |
| `requirements.txt` | Python dependency (`google-analytics-data`). | — |

## One-time setup

### 1 · Google Cloud — create the service account
1. Go to <https://console.cloud.google.com> and create (or pick) a project.
2. **APIs & Services → Library →** search **"Google Analytics Data API"** → **Enable**.
3. **IAM & Admin → Service Accounts → Create service account.** Give it a name
   (e.g. `sarah-dashboard`). No project roles are needed — click through and **Done**.
4. Open the new service account → **Keys → Add key → Create new key → JSON → Create**.
   A `.json` file downloads. Keep it safe.
5. Copy the service account **email** (looks like
   `sarah-dashboard@your-project.iam.gserviceaccount.com`).

### 2 · GA4 — give it read access
6. In Google Analytics, open **Admin** for the **www.uplers.com - GA4** property
   (id `285344907`) → **Property Access Management → +** → add the service-account
   **email** with the **Viewer** role.

### 3 · GitHub — publish + schedule
7. Create a new repository and upload every file from this folder
   (keep the `.github/workflows/` path intact).
8. **Settings → Secrets and variables → Actions → New repository secret.**
   Name it `GA4_SA_KEY` and paste the **entire contents** of the JSON key file.
9. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
10. **Actions** tab → **Daily GA4 refresh** → **Run workflow** to publish immediately
    (afterwards it runs itself every morning).

## The public URL

After the first run, the URL appears in the workflow's **deploy** step and under
**Settings → Pages**:

```
https://<your-github-username>.github.io/<repo-name>/
```

Share it with anyone — no login required.

## Schedule

Runs daily at **04:00 UTC = 09:30 IST** (`cron: "0 4 * * *"` in `update.yml`).
Change that line to move the time. The Action also has a **Run workflow** button for
on-demand refreshes.

## Reporting window

Anchored to Sarah's launch day: `GA4_START: "2026-07-08"` in the workflow reports from
that date through today ("since launch"). Change the date to move the start, or remove
`GA4_START` and set `GA4_WINDOW` to `"mtd"` (month-to-date) or a number of days (e.g.
`"28"`) for a rolling window instead.

## Lead quality (row 5)

Pulled automatically from the Sarah intake API
(`https://platform.uplers.com/api/public-intake/lead-quality`) on each run:

- `candidate` → **Job seekers / unqualified**
- `hiring_manager` → **Genuine buyers**
- `not_identified` and `total_started` are also stored in `data.json` (not shown on the page yet).

Shares in row 5 are computed within the classified set (job seekers + genuine buyers).
If the API is ever unreachable during a run, the job keeps the previous values rather than
zeroing the row. Override the endpoint with the `LEAD_QUALITY_API` env var if it changes.
