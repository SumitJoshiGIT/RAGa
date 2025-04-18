import httpx
import asyncio
import os
import uuid
import numpy as np
from functools import wraps
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from PIL import Image  

class PineconeAsyncClientParent:
    def __init__(self, image_index_name, environment, text_index_name=None):
        self.image_base_url = f"https://{image_index_name}-{environment}.svc.pinecone.io"
        self.text_base_url = f"https://{text_index_name}-{environment}.svc.pinecone.io"
        self.client = httpx.AsyncClient(headers={
            "Api-Key": os.environ.get("PINECONE"),
            "Content-Type": "application/json"
        })

        self.text_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _embedText(self, context: str):
        return self.text_model.encode(context, normalize_embeddings=True).astype(np.float32).tolist()

    def _embedImage(self, image):
        inputs = self.clip_processor(images=image, return_tensors="pt")
        outputs = self.clip_model.get_image_features(**inputs)
        image_embedding = outputs[0] / outputs[0].norm()
        return image_embedding.cpu().detach().numpy().astype(np.float32).tolist()

    def insert(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            embedding, url, metadata = func(self, *args, **kwargs)
            payload = {
                "vectors": [{
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": metadata or {}
                }]
            }
            res = await self.client.post(url, json=payload)
            return res.json()
        return wrapper

    def search(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            embedding, url, metadata = func(self, *args, **kwargs)
            payload = {
                "vector": embedding,
                "topK": 5,
                "includeMetadata": True
            }
            res = await self.client.post(url, json=payload)
            return res.json()
        return wrapper


class PineconeAsyncClient(PineconeAsyncClientParent):    
    
    @PineconeAsyncClientParent.insert
    def insertImage(self, image, metadata=None):
        url = f"{self.image_base_url}/vectors/upsert"
        embedding = self._embedImage(image)
        return embedding, url, metadata

    @PineconeAsyncClientParent.insert
    def insertText(self, text, metadata=None):
        url = f"{self.text_base_url}/vectors/upsert"
        embedding = self._embedText(text)
        return embedding, url, metadata

    @PineconeAsyncClientParent.search
    def searchImage(self, image):
        url = f"{self.image_base_url}/query"
        embedding = self._embedImage(image)
        return embedding, url, None

    @PineconeAsyncClientParent.search
    def searchText(self, text):
        url = f"{self.text_base_url}/query"
        embedding = self._embedText(text)
        return embedding, url, None

    async def close(self):
        await self.client.aclose()


if __name__ == "__main__":
    async def main():
        client = PineconeAsyncClient(
            image_index_name="your-image-index",
            text_index_name="your-text-index",
            environment="your-env"
        )

        from PIL import Image
        image = Image.open("example.jpg")

        await client.insertImage(image, {"type": "image", "name": "example"})
        result = await client.searchImage(image)
        print(result)

        await client.close()

    asyncio.run(main())
