import asyncio
import os
import glob
import json
from io import BytesIO
import cv2
import numpy as np
import torch
from PIL import Image
from sklearn.cluster import KMeans
from transformers import OwlViTProcessor, OwlViTForObjectDetection
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.client import PineconeAsyncClient
from rag.embedders import AzureEmbedder

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

from ultralytics import YOLO
from torchvision.transforms import Compose, Resize, ToTensor, Normalize

pipeline_embedder = AzureEmbedder(model_name="florence")


async def process_image(image_path, zone_id="unknown"):
    image_pil = Image.open(image_path).convert("RGB")
    metadata = {
        "zone_id": zone_id,
        "features": []
    }

    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    metadata["embedding"] = await pipeline_embedder.embed(image_bytes)
    print(metadata["embedding"])
    return metadata

async def process_streetviews(base_dir, output_file="embeddings.json"):
    embeddings = []

    for route_dir in glob.glob(os.path.join(base_dir,"*" )):
        if not os.path.isdir(route_dir):
            continue
        route_id = os.path.basename(route_dir)
        if(int(route_id) not in {0,1,2,3,4}):continue
        for waypoint_dir in glob.glob(os.path.join(route_dir, "*")):
            if not os.path.isdir(waypoint_dir):
                continue

            print(f"Processing route {route_id}, waypoint {os.path.basename(waypoint_dir)} ")

            for image_file in glob.glob(os.path.join(waypoint_dir, "*.jpg")):
                angle = os.path.basename(image_file)[:-4]
                try:
                    metadata = await process_image(image_file, zone_id=route_id)
                   
                    metadata["waypoint_id"] = os.path.basename(waypoint_dir)
                    metadata["angle"] = angle
                    embeddings.append(metadata)
                except Exception as e:
                    print(f"Error processing image {image_file}: {e}")
        print(f"Processed {len(embeddings)} images from route {route_id}")

    with open(output_file, "w") as f:
        json.dump(embeddings, f, indent=4)

    print(f"Embeddings saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(process_streetviews(
        os.path.join(os.getcwd(), "streetview_scrapper", "streetviews"),
        output_file="embeddings.json"
    ))
    