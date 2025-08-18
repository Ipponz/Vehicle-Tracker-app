from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
from datetime import datetime
import json
import os
import random
from time import time

app = Flask(__name__)
app.jinja_env.globals.update(time=time)  # expose time() to Jinja

DATA_FILE = "data.json"

# Bootstrap default colors + custom extras
BOOTSTRAP_COLORS = [
    "primary", "secondary", "success", "danger", "warning",
    "info", "light", "dark",
    "purple", "pink", "teal", "orange", "cyan", "indigo", "lime"
]

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        vehicles = data.get("vehicles", [])
        locations = data.get("locations", ["Showroom", "Body Fitter", "Radio Installer", "Repair Shop"])
        location_colors = data.get("location_colors", {})
else:
    vehicles = []
    locations = ["Showroom", "Body Fitter", "Radio Installer", "Repair Shop"]
    location_colors = {}

# Assign missing colors
for i, loc in enumerate(locations):
    if loc not in location_colors:
        location_colors[loc] = BOOTSTRAP_COLORS[i % len(BOOTSTRAP_COLORS)]

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "vehicles": vehicles,
            "locations": locations,
            "location_colors": location_colors
        }, f)

@app.route("/")
def dashboard():
    query = request.args.get("search", "").strip().upper()

    # Ensure all locations (even from vehicles) have a color
    for v in vehicles:
        loc = v.get("location")
        if loc and loc not in location_colors:
            # fallback to secondary if out of colors
            location_colors[loc] = random.choice(BOOTSTRAP_COLORS)

    if query:
        filtered_vehicles = [v for v in vehicles if query in v["reg"].upper()]
    else:
        filtered_vehicles = vehicles

    resp = make_response(render_template(
        "dashboard.html",
        vehicles=filtered_vehicles,
        search=query,
        location_colors=location_colors
    ))
    # 🔧 prevent cached dashboard
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# The rest of your routes unchanged...

@app.route("/add", methods=["GET", "POST"])
def add_vehicle():
    if request.method == "POST":
        reg = request.form["reg"].strip().upper()
        location = request.form["location"]
        moved_by = request.form["moved_by"].strip()
        moved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        vehicle = {
            "reg": reg,
            "location": location,
            "moved_by": moved_by,
            "moved_at": moved_at,
            "history": [(location, moved_by, moved_at)]
        }
        vehicles.append(vehicle)
        save_data()
        return redirect(url_for("dashboard"))

    return render_template("add_vehicle.html", locations=locations)


@app.route("/move/<reg>", methods=["GET", "POST"])
def move_vehicle(reg):
    vehicle = next((v for v in vehicles if v["reg"] == reg), None)
    if not vehicle:
        return "Vehicle not found", 404
    if request.method == "POST":
        location = request.form["location"]
        moved_by = request.form["moved_by"].strip()
        moved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vehicle["location"] = location
        vehicle["moved_by"] = moved_by
        vehicle["moved_at"] = moved_at
        vehicle["history"].append((location, moved_by, moved_at))
        save_data()
        return redirect(url_for("dashboard"))
    return render_template("move_vehicle.html", vehicle=vehicle, locations=locations)

@app.route("/delete/<reg>", methods=["POST"])
def delete_vehicle(reg):
    global vehicles
    vehicles[:] = [v for v in vehicles if v["reg"] != reg]
    save_data()
    return redirect(url_for("dashboard"))

@app.route("/add-location", methods=["GET", "POST"])
def add_location():   # FIX 2: keep just this one version
    if request.method == "POST":
        new_location = request.form["location"].strip()
        if new_location and new_location not in locations:
            locations.append(new_location)
            location_colors[new_location] = BOOTSTRAP_COLORS[len(location_colors) % len(BOOTSTRAP_COLORS)]
            save_data()
        return redirect(url_for("add_location"))
    return render_template("add_location.html", locations=locations)

@app.route("/edit-location/<loc>", methods=["GET", "POST"])
def edit_location(loc):
    if request.method == "POST":
        new_name = request.form["location"].strip()
        if new_name and new_name not in locations:
            index = locations.index(loc)
            locations[index] = new_name
            location_colors[new_name] = location_colors.pop(
                loc, BOOTSTRAP_COLORS[len(location_colors) % len(BOOTSTRAP_COLORS)]
            )
            for v in vehicles:
                if v["location"] == loc:
                    v["location"] = new_name
                v["history"] = [(new_name if h[0] == loc else h[0], h[1], h[2]) for h in v["history"]]
            save_data()
        return redirect(url_for("add_location"))
    return render_template("edit_location.html", location=loc)

@app.route("/delete-location/<loc>", methods=["POST"])
def delete_location(loc):
    if loc in locations:
        locations.remove(loc)
        location_colors.pop(loc, None)
        for v in vehicles:
            if v["location"] == loc:
                v["location"] = "Unknown"
                v["history"].append(("Unknown", "system", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        save_data()
    return redirect(url_for("add_location"))

# PWA files
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

if __name__ == "__main__":
    app.run(debug=True)
