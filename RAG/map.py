import polyline
import requests
import httpx
import os
import asyncio


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
                        'encodedPolyline': 'ipkcFfichVd@?d@?vB?N?R?z@?L?t@@R?d@?`B@j@?\\?'
                        },
                        'navigationInstruction': {
                        'maneuver': 'DEPART',
                        'instructions': 'Head south on Huff Ave'
                        }
                    },
                    {
                        'polyline': {
                        'encodedPolyline': '{}jcFjichVL@@K@YD_B@_@Bo@CYBq@?_@@a@B_A@s@?A@O@SB{ABo@B}@'
                        },
                        'navigationInstruction': {
                        'maneuver': 'TURN_LEFT',
                        'instructions': 'Turn left onto Plymouth St'
                        }
                    },
                    ]
                }
                ],
                'distanceMeters': 774,
                'duration': '147s',
                'polyline': {
                'encodedPolyline': 'ipkcFfichVd@?d@?vB?N?R?z@?L?t@@R?d@?`B@j@?\\?L@@K@YD_B@_@Bo@CYBq@?_@@a@B_A@s@?A@O@SB{ABo@B}@K?qA?_A?_@?_@?'
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

    async def get_street_view_image(self, location, heading, pitch, output_file):
        params = {
            "size": "600x300",
            "location": f"{location[0]},{location[1]}",
            "heading": heading,
            "pitch": pitch,
            "key": self.api_key
        }

        response = await self.client.get(self.street_view_url, params=params)

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

        origin = (37.419734, -122.0827784)
        destination = (37.417670, -122.079595)
        
        try:
            route_data = await navigator.get_route(origin, destination)
            print(route_data)
            encoded_polyline = route_data['routes'][0]['polyline']['encodedPolyline']
            decoded_points = navigator.decode_polyline(encoded_polyline)
            print(decoded_points)

            # Get a street view image
            #location = (46.414382, 10.013988)
            #await navigator.get_street_view_image(location, heading="151.78", pitch="-0.76", output_file="street_view_image.jpg")
        except Exception as e:
            print(e)
        await navigator.close()
    asyncio.run(main())