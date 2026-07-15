#!/usr/bin/env python3
"""
Daily GA4 refresh for the Sarah funnel dashboard.

Reads the Google Analytics 4 property, computes the four funnel rows, and writes
them into data.json. Never touches manual.json (the lead-quality + notes file).

Auth: a Google service account. The GitHub Action writes the service-account JSON
key to a file and points GOOGLE_APPLICATION_CREDENTIALS at it, so this script needs
no secrets in code.

Env vars:
  GA4_PROPERTY_ID  GA4 property id (default: 285344907 = www.uplers.com - GA4)
  GA4_WINDOW       "mtd" (month-to-date, default) or an integer N for a rolling N-day window
"""
import os
import json
import datetime

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    Filter,
    FilterExpression,
    FilterExpressionList,
)

PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "285344907")
EVENT_NAME = "Start with Sarah - CTA Clicks"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "data.json")

# ---- reporting window ------------------------------------------------------
# Priority: GA4_START (a fixed launch date) > GA4_WINDOW ("mtd" or N days).
today = datetime.date.today()
start_env = os.environ.get("GA4_START")            # e.g. "2026-07-08" (Sarah launch day)
window = os.environ.get("GA4_WINDOW", "mtd")
if start_env:
    start = datetime.date.fromisoformat(start_env)
    window_label = f"{start.strftime('%b %-d')} – {today.strftime('%-d, %Y')} (since launch)"
elif window == "mtd":
    start = today.replace(day=1)
    window_label = f"{start.strftime('%b %-d')} – {today.strftime('%-d, %Y')} (month to date)"
else:
    days = int(window)
    start = today - datetime.timedelta(days=days - 1)
    window_label = f"last {days} days ({start.strftime('%b %-d')} – {today.strftime('%-d, %Y')})"

START = start.isoformat()
END = today.isoformat()

client = BetaAnalyticsDataClient()


def eq(field, value):
    return FilterExpression(
        filter=Filter(
            field_name=field,
            string_filter=Filter.StringFilter(
                match_type=Filter.StringFilter.MatchType.EXACT, value=value
            ),
        )
    )


def run(dimensions, metrics, dim_filter=None):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=START, end_date=END)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        dimension_filter=dim_filter,
    )
    return client.run_report(req)


# 1. Homepage sessions (landing page = "/")
r = run([], ["sessions"], eq("landingPagePlusQueryString", "/"))
homepage = int(r.rows[0].metric_values[0].value) if r.rows else 0

# 2. India homepage sessions
india_filter = FilterExpression(
    and_group=FilterExpressionList(
        expressions=[eq("landingPagePlusQueryString", "/"), eq("country", "India")]
    )
)
r = run([], ["sessions"], india_filter)
india = int(r.rows[0].metric_values[0].value) if r.rows else 0

# 3. "Start with Sarah" CTA clicks, split India vs outside
r = run(["country"], ["eventCount"], eq("eventName", EVENT_NAME))
sarah_total = 0
sarah_india = 0
for row in r.rows:
    country = row.dimension_values[0].value
    n = int(row.metric_values[0].value)
    sarah_total += n
    if country == "India":
        sarah_india += n
sarah_outside = sarah_total - sarah_india

data = {
    "homepageSessions": homepage,
    "indiaSessions": india,
    "sarahIndiaClicks": sarah_india,
    "sarahOutsideClicks": sarah_outside,
    "windowLabel": window_label,
    "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print("Wrote", DATA_FILE)
print(json.dumps(data, indent=2))
