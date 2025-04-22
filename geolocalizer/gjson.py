import json
import random
import math
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
import asyncio

class GeoPolygonAnalyzer:
    def __init__(self, geojson_path, distance_threshold=100, min_neighbors=3):
        self.geojson_path = geojson_path
        self.distance_threshold = distance_threshold
        self.min_neighbors = min_neighbors
        self.current_localization = None
        self.current_point = None
        self.polygons = []
        self.names = []
        self.bounds = None
        self._load_geojson()

    def _load_geojson(self):
        with open(self.geojson_path) as f:
            data = json.load(f)

        for feature in data["features"]:
            if feature["geometry"]["type"] == "Polygon":
                self.polygons.append(shape(feature["geometry"]))
                self.names.append(feature.get("properties", {}).get("name", "Unnamed"))

        minx, miny, maxx, maxy = self.polygons[0].bounds
        for poly in self.polygons:
            x1, y1, x2, y2 = poly.bounds
            minx, miny = min(minx, x1), min(miny, y1)
            maxx, maxy = max(maxx, x2), max(maxy, y2)
        self.bounds = (minx, miny, maxx, maxy)
          
    def get_direction(self, from_point, to_point):
        dx = to_point.x - from_point.x
        dy = to_point.y - from_point.y
        angle = math.degrees(math.atan2(dy, dx))
        return angle
    
    def analyze_point(self, pt: Point):
        results = []

        all_dists = [
            (
                pt.distance((nearest_pt := nearest_points(poly.boundary, pt)[0])) * 111139,  
                name,
                poly,
                nearest_pt,  
                self.get_direction(nearest_pt, pt),  
                idx 
            )
            for idx, (name, poly) in enumerate(zip(self.names, self.polygons))
        ]

        for dist, name, poly, nearest_pt, direction, idx in all_dists:
            if poly.contains(pt):
                results.append((dist, name, poly, nearest_pt, "inside", idx))
            elif dist <= self.distance_threshold:
                results.append((dist, name, poly, nearest_pt, direction, idx))

        if len(results) < self.min_neighbors:
            additional_results = sorted(all_dists, key=lambda x: x[0])
            for entry in additional_results:
                if entry not in results:
                    results.append(entry)
                if len(results) >= self.min_neighbors:
                    break

        return sorted(results, key=lambda x: x[0])

    def plot_analysis(self, pt: Point, analysis_results):
        minx, miny, maxx, maxy = self.bounds
        fig, ax = plt.subplots(figsize=(10, 10))
        for poly in self.polygons:
            x, y = poly.exterior.xy
            ax.plot(x, y, color="black", linewidth=1)

        ax.plot(pt.x, pt.y, "bo", markersize=8)
        for dist, name, poly, near_pt, direction, idx in analysis_results:
            ax.plot([pt.x, near_pt.x], [pt.y, near_pt.y], 'r--')
            ax.text(near_pt.x, near_pt.y, f"{name}\n{r
            ound(dist)}m\n{direction}", fontsize=6, color="red")

        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
        ax.set_aspect("equal")
        ax.set_title("GeoSpatial Analysis")
        ax.grid(True)
        plt.show()

   
map_path = r"G:\RAGa\geolocalizer\gjson.json"

analyzer = GeoPolygonAnalyzer(map_path, distance_threshold=100, min_neighbors=3)

pt = Point(77.9930, 30.2688)
results = analyzer.analyze_point(pt)
print(results)
analyzer.plot_analysis(pt, results)

import asyncio
asyncio.run(analyzer.update_localization,args=(pt,))

# import asyncio
#asyncio.run(analyzer.continuously_update_localization())

