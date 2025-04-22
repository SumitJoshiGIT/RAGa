import polyline
import requests
import httpx
import os
import asyncio
import json


class MapsScrapper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.route_headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs.steps.polyline,routes.legs.steps.navigationInstruction'
        }
        self.street_view_headers = {}
        self.route_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
        self.street_view_url = "https://maps.googleapis.com/maps/api/streetview"
        self.client = httpx.AsyncClient() 

    async def get_route(self, origin_coords, destination_coords):
        payload = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin_coords[0],
                        "longitude": origin_coords[1]
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination_coords[0],
                        "longitude": destination_coords[1]
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "polylineQuality": "HIGH_QUALITY",
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        
        response = await self.client.post(self.route_url, headers=self.route_headers, json=payload)
        
        """
        {
            'routes': [
            {
                'legs': [
                {
                    'steps': [
                    {
                        'polyline': {
                        'encodedPolyline':
                        },
                        'navigationInstruction': {
                        'maneuver': ,
                        'instructions': 
                        }
                    },
                    {
                        'polyline': {
                        'encodedPolyline': 
                        },
                        'navigationInstruction': {
                        'maneuver': ,
                        'instructions': 
                        }
                    },
                    ]
                }
                ],
                'distanceMeters': ,
                'duration': ,
                'polyline': {
                'encodedPolyline': 
                }
            }
            ]
        }
        
        """

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        


    def decode_polyline(self, encoded_polyline):
        return polyline.decode(encoded_polyline)

    async def get_street_view_image(self, location, heading, pitch, output_location="./streetviews"):
        if not os.path.exists(output_location):
            os.makedirs(output_location, exist_ok=True)

        params = {
            "size": "600x300",
            "location": f"{location[0]},{location[1]}",
            "heading": heading,
            "pitch": pitch,
            "key": self.api_key
        }
        
        response = await self.client.get(self.street_view_url, params=params)
        output_file = os.path.join(output_location, f"{heading}.jpg")
        if response.status_code == 200:
            with open(output_file, "wb") as image_file:
                image_file.write(response.content)
            print(f"Street view image saved as '{output_file}'")
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
     
    async def close(self):
        await self.client.aclose()

# Example usage 
if __name__ == "__main__":
   
    async def main():
        API_KEY = 'AIzaSyBhM4AXjlf89BHFAoZfcpKocfK9Cjwg6L8'
        navigator = MapsScrapper(API_KEY)
        print(os.getcwd())
        waypoints_file = "G:\SequenceModellingg\RAG-api-example\RAG\streetview_pusher\waypoints.json"
        
        with open(waypoints_file, "r") as file:
            waypoints = json.load(file)
        counter=0
        for x in waypoints:
            origin = (x["start"]["lat"], x["start"]["long"])
            destination = (x["end"]["lat"], x["end"]["long"])     
            id = x["id"]
            if counter>5:break
            counter+=1
            try:
                route_data = await navigator.get_route(origin, destination)
                encoded_polyline = route_data['routes'][0]['polyline']['encodedPolyline']
                decoded_points = navigator.decode_polyline(encoded_polyline)
                     
                for i in  range(len(decoded_points)-1):
                   location = decoded_points[i]
                   for angle in range(0, 360, 30):
                    await navigator.get_street_view_image(location, heading=f"{angle}", pitch="-0.76", output_location=r"G:\SequenceModellingg\RAG-api-example\RAG\streetview_pusher\streetviews\\"+f"{id}\{i}\\")

                with open(r"G:\SequenceModellingg\RAG-api-example\RAG\streetview_pusher\streetviews\\" + f"{id}\\meta.json", "w") as meta_file:
                    json.dump({**x, "route": route_data['routes'][0]}, meta_file, indent=4)
            except Exception as e:print(e)
               
        await navigator.close()

    asyncio.run(main())