from flask import Flask, request, redirect, session, render_template_string
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "change-this-key"

# =================================================
# DATABASE LOCATION
# =================================================
# Local / testing:
DB_PATH = "rtpi.db"

# Render persistent disk (enable later):
# DB_PATH = "/data/rtpi.db"

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# =================================================
# DATABASE SETUP
# =================================================
def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    if os.path.exists(DB_PATH):
        return
    with db() as con:
        con.executescript("""
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT
        );

        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT,
            destination TEXT,
            stop TEXT,
            days TEXT,
            time TEXT
        );

        INSERT INTO users VALUES ('admin','admin');
        """)
        con.commit()

init_db()

# =================================================
# AUTH
# =================================================
def logged_in():
    return "user" in session

# =================================================
# RTPI LOGIC
# =================================================
def upcoming_services(stop, window=120):
    now = datetime.now()
    now_min = now.hour * 60 + now.minute
    today = WEEKDAYS[now.weekday()]

    with db() as con:
        rows = con.execute(
            "SELECT route, destination, time FROM services "
            "WHERE stop=? AND days LIKE ?",
            (stop, f"%{today}%")
        ).fetchall()

    results = []
    for route, dest, t in rows:
        h, m = map(int, t.split(":"))
        dep = h * 60 + m
        if now_min <= dep <= now_min + window:
            results.append((dep - now_min, route, dest))

    return sorted(results)[:8]

def due_text(minutes):
    return "Due" if minutes < 2 else f"{minutes} min"

# =================================================
# PUBLIC DISPLAY
# =================================================
DISPLAY_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="30">
<style>
body {
    background:black;
    color:white;
    font-family:Arial, Helvetica, sans-serif;
    margin:0;
    padding:20px;
}
h1 { margin:0 0 10px 0; }
.clock { color:#0ff; font-size:1.3em; margin-bottom:15px; }
.row {
    display:grid;
    grid-template-columns: 15% 65% 20%;
    font-size:2em;
    padding:5px 0;
}
.route { color:#ff0; }
.due { color:#0ff; text-align:right; }
select {
    background:black;
    color:#0ff;
    font-size:1em;
    border:1px solid #0ff;
}
</style>
</head>
<body>

<h1>Bus departures — {{ stop }}</h1>
<div class="clock">{{ now }}</div>

<form>
<select name="stop" onchange="this.form.submit()">
{% for s in stops %}
<option value="{{s}}" {{ 'selected' if s == stop else '' }}>{{s}}</option>
{% endfor %}
</select>
</form>

<hr>

{% for mins, route, dest in services %}
<div class="row">
    <div class="route">{{ route }}</div>
    <div>{{ dest }}</div>
    <div class="due">{{ due_text(mins) }}</div>
</div>
{% else %}
<div class="row">
    <div></div>
    <div>No services</div>
    <div></div>
</div>
{% endfor %}

</body>
</html>
"""

@app.route("/")
def board():
    with db() as con:
        stops = [r[0] for r in con.execute(
            "SELECT DISTINCT stop FROM services ORDER BY stop"
        )]

    if not stops:
        return "No stops configured yet."

    stop = request.args.get("stop", stops[0])
    services = upcoming_services(stop)

    return render_template_string(
        DISPLAY_HTML,
        stop=stop,
        stops=stops,
        services=services,
        now=datetime.now().strftime("%A %H:%M"),
        due_text=due_text
    )

# =================================================
# LOGIN
# =================================================
LOGIN_HTML = """
<h2>RTPI Admin Login</h2>
<form method="post">
<input name="username" placeholder="Username"><br><br>
<input name="password" type="password" placeholder="Password"><br><br>
<button>Login</button>
</form>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        with db() as con:
            user = con.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (u, p)
            ).fetchone()

        if user:
            session["user"] = u
            return redirect("/admin")

    return render_template_string(LOGIN_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =================================================
# ADMIN PANEL
# =================================================
ADMIN_HTML = """
<h2>Timetable Admin</h2>
<a href="/">Public Display</a> |
<a href="/logout">Logout</a>

<hr>

<form method="post">
Route <input name="route" required>
Destination <input name="destination" required>
Stop <input name="stop" required><br><br>
Days (Mon,Tue,Wed...) <input name="days" required>
Time (HH:MM) <input name="time" required>
<button>Add Service</button>
</form>

<hr>

<table border="1" cellpadding="6">
<tr>
<th>Route</th><th>Destination</th><th>Stop</th><th>Days</th><th>Time</th>
</tr>
{% for s in services %}
<tr>
<td>{{s[1]}}</td>
<td>{{s[2]}}</td>
<td>{{s[3]}}</td>
<td>{{s[4]}}</td>
<td>{{s[5]}}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not logged_in():
        return redirect("/login")

    if request.method == "POST":
        with db() as con:
            con.execute(
                "INSERT INTO services(route,destination,stop,days,time) "
                "VALUES (?,?,?,?,?)",
                (
                    request.form["route"],
                    request.form["destination"],
                    request.form["stop"],
                    request.form["days"],
                    request.form["time"]
                )
            )
            con.commit()

    with db() as con:
        services = con.execute(
            "SELECT * FROM services ORDER BY stop, time"
        ).fetchall()

    return render_template_string(ADMIN_HTML, services=services)

# =================================================
# RUN
# =================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
