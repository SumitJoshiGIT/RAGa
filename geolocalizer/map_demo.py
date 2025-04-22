import json
import random
import math
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
import matplotlib.pyplot as plt

map_path = r"G:\RAGa\geolocalizer\gjson.json"

import json
import random
import math
import time
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
import matplotlib.pyplot as plt

DISTANCE_THRESHOLD = 100  
MIN_NEIGHBORS = 3
PAUSE_TIME = 2  
NUM_FRAMES = 100  

with open(map_path) as f:
    data = json.load(f)

polygons = []
names = []
for feature in data["features"]:
    if feature["geometry"]["type"] == "Polygon":
        polygons.append(shape(feature["geometry"]))
        names.append(feature.get("properties", {}).get("name", "Unnamed"))

minx, miny, maxx, maxy = polygons[0].bounds
for poly in polygons:
    x1, y1, x2, y2 = poly.bounds
    minx, miny = min(minx, x1), min(miny, y1)
    maxx, maxy = max(maxx, x2), max(maxy, y2)

def get_direction(from_point, to_point):
    dx = to_point.x - from_point.x
    dy = to_point.y - from_point.y
    angle = math.degrees(math.atan2(dy, dx))
    compass = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
    index = round(((angle + 360) % 360) / 45) % 8
    return compass[index]

plt.ion()
fig, ax = plt.subplots(figsize=(10, 10))

for _ in range(NUM_FRAMES):
    # Clear previous frame
    ax.clear()

    # Plot all polygons
    for poly in polygons:
        x, y = poly.exterior.xy
        ax.plot(x, y, color="black", linewidth=1)

    # Pick random point
    rand_x = random.uniform(minx, maxx)
    rand_y = random.uniform(miny, maxy)
    pt = Point(rand_x, rand_y)
    ax.plot(pt.x, pt.y, "bo", markersize=8)
    ax.set_title("Random Point Proximity Visualization")

    # Find nearby polygons
    nearby = []
    for name, poly in zip(names, polygons):
        if poly.contains(pt):
            nearby.append((0, name, poly, pt))  # zero distance
        else:
            nearest_pt = nearest_points(poly.boundary, pt)[0]
            dist = pt.distance(nearest_pt) * 111139
            if dist <= DISTANCE_THRESHOLD:
                nearby.append((dist, name, poly, nearest_pt))

    # Ensure at least MIN_NEIGHBORS are selected (add closest beyond threshold if needed)
    if len(nearby) < MIN_NEIGHBORS:
        all_dists = []
        for name, poly in zip(names, polygons):
            nearest_pt = nearest_points(poly.boundary, pt)[0]
            dist = pt.distance(nearest_pt) * 111139
            all_dists.append((dist, name, poly, nearest_pt))
        all_dists.sort(key=lambda x: x[0])
        for entry in all_dists:
            if entry not in nearby:
                nearby.append(entry)
            if len(nearby) >= MIN_NEIGHBORS:
                break

    # Sort final selection
    nearby.sort(key=lambda x: x[0])

    # Plot lines + annotate
    for dist, name, poly, np in nearby:
        ax.plot([pt.x, np.x], [pt.y, np.y], 'r--')
        ax.text(np.x, np.y, f"{name}\n{round(dist, 1)}m", fontsize=6, color="red")

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect('equal')
    ax.grid(True)
    plt.pause(PAUSE_TIME)

plt.ioff()
plt.show()
