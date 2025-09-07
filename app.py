from flask import Flask, render_template_string, request
from dataclasses import dataclass
from datetime import datetime, timedelta
import time as pytime
import sys

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None  # fallback if not available

app = Flask(__name__)

# -------------------------------
# Demo Preset Timetable
# -------------------------------
PRESET_TIMETABLE = [
    {
        "route": "479",
        "destination": "Guildford",
        "stop_id": "Effingham",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "times": ["07:00","08:00","08:51","09:24","09:59","10:29","10:59","11:29","11:59",
                  "12:29","12:59","13:29","13:59","14:29","15:12","16:03","16:33",
                  "17:03","17:39","18:09","18:54","19:20","19:50","20:56"],
    },
    {
        "route": "479",
        "destination": "Epsom",
        "stop_id": "Effingham",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "times": ["06:23","07:10","07:31","08:16","08:46","09:23","09:53","10:23","10:53",
                  "11:23","11:53","12:23","12:53","13:23","13:53","14:40","15:10","15:44",
                  "16:27","17:15","17:44","18:11","18:41","19:11","19:56","20:56"],
    },
    {
        "route": "479",
        "destination": "Epsom",
        "stop_id": "Effingham",
        "days": ["Sat"],
        "times": ["07:52","08:22","08:52","09:23","09:53","10:23","10:53","11:23","11:53",
                  "12:23","12:53","13:23","13:53","14:40","15:10","15:44","16:27","17:15",
                  "17:44","18:11","18:41","19:11","19:56"],
    },
    {
        "route": "479",
        "destination": "Epsom",
        "stop_id": "Effingham",
        "days": ["Sun"],
        "times": ["10:04","11:04","12:04","13:04","14:04","15:04","16:04","17:04","18:04","19:04"],
    },
    {
        "route": "479",
        "destination": "Guildford",
        "stop_id": "Effingham",
        "days": ["Sat"],
        "times": ["08:29","08:59","09:29","09:59","10:29","10:59","11:29","11:59","12:29","12:59",
                  "13:29","13:59","14:29","14:59","15:29","15:59","16:29","16:59","17:29","17:59",
                  "18:29","18:59","19:25","19:55","20:50"],
    },
    {
        "route": "479",
        "destination": "Guildford",
        "stop_id": "Effingham",
        "days": ["Sun"],
        "times": ["09:44","10:44","11:44","12:44","13:44","14:44","15:44","16:44","18:44"],
    },
    {
        "route": "478",
        "destination": "Leatherhead",
        "stop_id": "Effingham",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "times": ["08:40","09:50","11:50","14:00","17:20"],
    },
    {
        "route": "478",
        "destination": "Guildford",
        "stop_id": "Effingham",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "times": ["10:30","12:30","14:50"],
    },
    {

"route": "479",

"destination": "Guildford",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["06:15","07:15","07:45","08:40","09:15","09:45","10:15","10:45",

"11:15","11:45","12:15","12:45","13:15","13:45","14:25","15:00","15:45",

"16:15","16:55","17:25","18:10","18:40","19:10","20:10"],

},

{

"route": "479",

"destination": "Bookham",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["21:10"],

},

{

"route": "479",

"destination": "Guildford",

"stop_id": "Epsom",

"days": ["Sat"],

"times": ["07:45","08:45","09:15","09:45","10:15","10:45",

"11:15","11:45","12:15","12:45","13:15","13:45","14:15","14:45","15:15","15:45",

"16:15","16:45","17:15","17:45","18:15","18:45","19:15","20:10"],

},

{

"route": "479",

"destination": "Guildford",

"stop_id": "Epsom",

"days": ["Sun"],

"times": ["09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00"],

},

{

"route": "408",

"destination": "Cobham",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["06:30","07:47","08:00","09:14","10:14","11:14","12:14","13:14","14:14","15:14","17:45"],

},

{

"route": "408",

"destination": "Chipstead valley (via Banstead)",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["16:00"],

},

{

"route": "E16",

"destination": "Worcester park",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["07:20","09:00","10:00","11:00","12:00","13:00","14:05","15:10","16:30","17:45"],

}, 

{

"route": "E16",

"destination": "Worcester park",

"stop_id": "Epsom",

"days": ["Sat"],

"times": ["08:00","09:00","10:00","11:00","12:00","13:00","14:05","15:10","16:30","17:45"],

},
{

"route": "21",

"destination": "Crawley",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["06:55","09:00","11:00","12:50","15:05","17:20"],
}, 

{

"route": "21",

"destination": "Crawley",

"stop_id": "Epsom",

"days": ["Sat"],

"times": ["09:25","11:25","13:25","15:25","17:25"],

},
]

# -------------------------------
# Core Structures
# -------------------------------
WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

@dataclass
class Trip:
    route: str
    destination: str
    stop_id: str
    dep_minutes: int
    service_day_idx: int

def parse_time_to_minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h*60 + m

def service_matches_day(service_days: list[str], day_idx: int) -> bool:
    if "Daily" in service_days:
        return True
    return WEEKDAYS[day_idx % 7] in service_days

def build_trips_for_week(timetable: list[dict]) -> list[Trip]:
    trips = []
    for day_idx in range(7):
        for row in timetable:
            if not service_matches_day(row["days"], day_idx):
                continue
            for t in row["times"]:
                mins = parse_time_to_minutes(t)
                trips.append(Trip(row["route"], row["destination"], row["stop_id"],
                                  mins + day_idx*1440, day_idx))
    trips.sort(key=lambda tr: tr.dep_minutes)
    return trips

def pick_timezone(tz_arg: str | None):
    if tz_arg and ZoneInfo:
        try:
            return ZoneInfo(tz_arg)
        except Exception:
            pass
    return None

def now_in_tz(tz):
    return datetime.now(tz) if tz else datetime.now()

def filter_upcoming(trips, now_local, stop_id, horizon_min, limit):
    now_abs = (now_local.weekday() * 1440) + now_local.hour * 60 + now_local.minute
    max_abs = now_abs + horizon_min
    results = []
    for tr in trips:
        if tr.stop_id != stop_id:
            continue
        if now_abs <= tr.dep_minutes <= max_abs:
            due = tr.dep_minutes - now_abs
            results.append((due, tr))
    results.sort(key=lambda x: x[0])
    return results[:limit]

def format_due(delta_min: int) -> str:
    if delta_min <= 0:
        return "Due"
    if delta_min < 60:
        return f"{delta_min} min"
    hours, mins = divmod(delta_min, 60)
    return f"{hours:02d}:{mins:02d}"

# -------------------------------
# Web App
# -------------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Bus Departures</title>
  <meta http-equiv="refresh" content="30">
  <style>
    body { font-family: sans-serif; background: #111; color: #eee; text-align: center; }
    table { margin: auto; border-collapse: collapse; }
    th, td { padding: 8px 12px; border: 1px solid #444; }
    th { background: #333; }
    tr:nth-child(even) { background: #222; }
    select, button { font-size: 1rem; padding: 4px 8px; margin-left: 4px; }
  </style>
</head>
<body>
  <h2>RTPI • Stop: {{stop_id}} • {{now}}</h2>

  <form method="get" action="/">
    <label for="stop">Select Stop:</label>
    <select name="stop" id="stop">
      {% for s in stops %}
        <option value="{{s}}" {% if s == stop_id %}selected{% endif %}>{{s}}</option>
      {% endfor %}
    </select>
    <button type="submit">Go</button>
  </form>

  <table>
    <tr><th>Route</th><th>Destination</th><th>Due</th><th>Scheduled</th></tr>
    {% for due, tr in upcoming %}
    <tr>
      <td>{{tr.route}}</td>
      <td>{{tr.destination}}</td>
      <td>{{format_due(due)}}</td>
      <td>{{'%02d:%02d' % ((tr.dep_minutes % 1440) // 60, (tr.dep_minutes % 1440) % 60)}}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""

trips = build_trips_for_week(PRESET_TIMETABLE)

@app.route("/")
def board():
    tz = pick_timezone("Europe/London")
    now_local = now_in_tz(tz)

    # Get stop_id from query parameter, default to first available
    available = sorted({row["stop_id"] for row in PRESET_TIMETABLE})
    stop_id = request.args.get("stop", available[0])
    if stop_id not in available:
        stop_id = available[0]

    upcoming = filter_upcoming(trips, now_local, stop_id, 120, 8)
    return render_template_string(TEMPLATE, stop_id=stop_id, now=now_local,
                                  upcoming=upcoming, format_due=format_due, stops=available)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
