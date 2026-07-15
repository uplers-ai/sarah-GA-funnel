# Sarah Funnel — Auto-updating dashboard

A public dashboard for the **Sarah AI Hiring Agent** funnel on uplers.com, hosted on
GitHub Pages. A GitHub Action refreshes the GA4 rows every morning using a Google
**service account**, so it runs on its own — no computer needs to be on. The
lead-quality numbers and analysis notes are edited by hand.

## Files

| File | What it is | Who updates it |
|------|-----------|----------------|
| `index.html` | The dashboard. Loads the two JSON files and renders the funnel. | Rarely (design only) |
| `data.json` | GA4 numbers: homepage sessions, India sessions, Sarah clicks (India / outside). | **Automatic** — daily Action |
| `manual.json` | Lead quality (job seekers) + the good / bad / next notes. | **You**, whenever you like |
| `fetch_ga4.py` | Pulls the GA4 numbers and writes `data.json`. | — |
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

Month-to-date by default (`GA4_WINDOW: "mtd"` in the workflow). For a rolling window,
set `GA4_WINDOW` to a number of days, e.g. `"28"`.

## Updating the manual numbers

Open `manual.json` on GitHub, click the pencil ✏️, edit, commit:

```json
{
  "jobSeekerCount": 12,
  "goodText": "one point per line",
  "badText": "one point per line",
  "nextText": "one point per line"
}
```

`jobSeekerCount` is how many of the total Sarah conversations were job seekers; the
dashboard computes **genuine buyers** as `total clicks − job seekers` automatically.
The daily Action never overwrites this file.
