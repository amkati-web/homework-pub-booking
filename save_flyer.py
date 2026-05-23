import os
import pathlib
import shutil
import subprocess
import time

# Run the exercise
result = subprocess.run(["uv", "run", "python", "-m", "starter.edinburgh_research.run"], text=True)

# Wait a moment
time.sleep(1)

# Search in common locations
search_dirs = [
    pathlib.Path("sessions"),
    pathlib.Path("C:/Users/Ekaterina/AppData/Local/Temp"),
    pathlib.Path.home() / "AppData/Local/Temp",
]

found = False
for search_dir in search_dirs:
    if not search_dir.exists():
        continue
    for p in search_dir.rglob("flyer.html"):
        dest = pathlib.Path("flyer.html")
        shutil.copy(p, dest)
        print(f"Found and copied from: {p}")
        print(f"Saved to: {dest.absolute()}")
        os.startfile(str(dest.absolute()))
        found = True
        break
    if found:
        break

if not found:
    print("Flyer not found - searching all of AppData/Local/Temp:")
    for p in pathlib.Path("C:/Users/Ekaterina/AppData/Local/Temp").rglob("*.html"):
        print(f"  found html: {p}")
