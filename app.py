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

"times": ["06:30","07:47","09:14","10:14","11:14","12:14","13:14","14:14","15:14","17:45"],

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
{

"route": "166",

"destination": "West Croydon",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],

"times": ["07:29","08:30","09:29","10:30","11:30","12:30","13:30","14:30","15:30","16:30","17:30","18:30","19:30","20:30"],

},
{

"route": "166",

"destination": "Epsom",

"stop_id": "Wood Post",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["06:37","07:40","08:37","09:37","10:40","11:37","12:37","13:37","14:37","15:37","16:37","17:37","18:37","19:37","20:34"],

},
{

"route": "166",

"destination": "Epsom",

"stop_id": "Wood Post",

"days": ["Sat"],

"times": ["06:53","07:32","08:34","09:35","10:34","11:32","12:35","13:34","14:34","15:32","16:32","17:32","18:32","19:30"],

},
{

"route": "408",

"destination": "Cobham (Via Epsom, Leatherhead)",

"stop_id": "Wood Post",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["07:15"],

},
{

"route": "460",

"destination": "Crawley",

"stop_id": "Epsom",

"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],

"times": ["05:55","06:43","07:05","07:40","09:10","10:10","11:14",
"12:14","13:14","14:18","15:18","16:15","17:33","18:44","19:31","19:46",
"20:17","21:10","22:10","23:10","00:10"],

},
{
"route": "293",
"destination": "Morden",
"stop_id": "Epsom High Street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": [
"06:27","06:52","07:17","07:40","08:01","08:21","08:41","09:01",
"09:19","09:36","09:54","10:13","10:33","10:53","11:13","11:33",
"11:53","12:13","12:33","12:53","13:13","13:33","13:53","14:13",
"14:33","14:53","15:14","15:34","15:54","16:14","16:34","16:54",
"17:14","17:34","17:54","18:13","18:32","18:50","19:08","19:26",
"19:44","20:03","20:22","20:41","21:01","21:21","21:40","21:59",
"22:20","22:49","23:19","23:49","00:19","00:49"]
},
{
"route": "406",
"destination": "Kingston",
"stop_id": "Epsom High Street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": [
"06:05","06:25","06:50","07:15","07:35","07:57","08:22","08:42",
"09:01","09:20","09:36","09:53","10:12","10:32","10:52","11:12",
"11:32","11:52","12:12","12:32","12:52","13:12","13:32","13:52",
"14:12","14:32","14:52","15:12","15:32","15:52","16:12","16:32",
"16:52","17:12","17:32","17:52","18:12","18:32","18:52","19:12",
"19:32","19:52","20:12","20:32","20:52","21:12","21:32","21:52",
"22:12","22:32","22:52","23:12","23:32","00:12"]
},
{
"route": "S2",
"destination": "St Helier Station",
"stop_id": "Epsom High Street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": [
"06:47", "07:09", "07:32", "07:56", "08:19", "08:29", "08:43", "08:59",
"09:15", "09:30", "09:50", "10:10", "10:30", "10:50", "11:10", "11:30",
"11:51", "12:11", "12:31", "12:51", "13:11", "13:31", "13:51", "14:11",
"14:31", "14:51", "15:11", "15:30", "15:51", "16:08", "16:28", "16:48",
"17:08", "17:26", "17:45", "18:05", "18:24", "18:41", "18:59", "19:18",
"19:35", "19:52", "20:12", "20:30", "20:49", "21:08", "21:28", "21:57",
"22:27", "22:57", "23:27", "23:57", "00:27"]
},
{
  "route": "467",
  "destination": "Kingston",
  "stop_id": "Epsom High Street",
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "times": [
    "06:37", "07:12", "08:02", "09:08", "09:46", "10:31", "11:31",
    "12:31", "13:30", "14:30", "15:56", "16:53", "17:56", "19:11"]
},
{"route":"467",
"destination":"Hook",
"stop_id":"Epsom High Street",
"days":["Mon","Tue","Wed","Thu","Fri"],
"times":[
"06:20","07:23","08:25","09:25","10:25","11:01","12:01","13:01",
"14:01","15:01","16:01","17:01","18:01","19:01"]
},
{
"route":"467",
"destination":"Hook",
"stop_id":"Epsom High Street",
"days":["Mon","Tue","Wed","Thu","Fri"],
"times":[
"06:20","07:23","08:25","09:25","10:25","11:01","12:01","13:01",
"14:01","15:01","16:01","17:01","18:01","19:01"]
},
{
"route": "E16",
"destination": "Worcester park",
"stop_id": "Epsom High street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": ["07:20","09:00","10:00","11:00","12:00","13:00",
"14:05","15:10","16:30","17:45"],
}, 
{
"route":"293",
"destination":"Epsom",
"stop_id":"Ewell High Street",
"days":["Mon","Tue","Wed","Thu","Fri"],
"times":[
"06:17","06:47","07:17","07:47","08:17","08:47","09:17","09:47",
"10:17","10:47","11:17","11:47","12:17","12:47","13:17","13:47",
"14:17","14:47","15:17","15:47","16:17","16:47","17:17","17:47",
"18:17","18:47","19:17","19:47","20:17","20:47","21:17","21:47",
"22:17","22:47","23:17"]
},
{
"route":"406",
"destination":"Epsom",
"stop_id":"Ewell High Street",
"days":["Mon","Tue","Wed","Thu","Fri"],
"times":[
"06:20","06:50","07:20","07:50","08:20","08:50","09:20","09:50",
"10:20","10:50","11:20","11:50","12:20","12:50","13:20","13:50",
"14:20","14:50","15:20","15:50","16:20","16:50","17:20","17:50",
"18:20","18:50","19:20","19:50","20:20","20:50","21:20","21:50",
"22:20","22:50","23:20"]
},
{
"route":"S2",
"destination":"Epsom",
"stop_id":"Ewell High Street",
"days":["Mon","Tue","Wed","Thu","Fri"],
"times":[
"06:30","07:00","07:30","08:00","08:30","09:00","09:30","10:00",
"10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00",
"14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00",
"18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00",
"22:30","23:00","23:30"]
},
{
"route": "E16",
"destination": "Epsom",
"stop_id": "Ewell High Street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": [
"07:28", "10:08", "12:08", "14:13", "16:38",
"09:08", "11:08", "13:08", "15:08", "17:53"]
},
{
"route": "467",
"destination": "Epsom High Street",
"stop_id": "Ewell High Street",
"days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
"times": [
"06:32","07:06","07:52","09:00","09:39","10:24","11:24",
"12:24","13:23","14:23","15:48","16:46","17:49","19:05"]
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
    if delta_min < 2:
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
    return render_template_string(TEMPLATE, stop_id=stop_id, now=now_local.strftime("%Y-%m-%d %H:%M:%S"),
                                  upcoming=upcoming, format_due=format_due, stops=available)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
