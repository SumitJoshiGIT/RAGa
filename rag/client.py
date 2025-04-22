import asyncio
import os
import uuid
from functools import wraps
import asyncio
from pinecone import PineconeAsyncio, ServerlessSpec
from dotenv import load_dotenv
from PIL import Image
import httpx
import io
import base64
from . import embedders
load_dotenv()

class PineconeAsyncClientParent:
    def __init__(self,embedder=None,index_name="index", text_index_name=None):
        self.embedder=embedder 
        self.pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        self.pinecone = PineconeAsyncio(api_key=self.pinecone_api_key)
        self.index_name = index_name
       
    async def init_indexes(self):
        await self.pinecone.__aenter__()
        if self.index_name:
            self.index = self.pinecone.IndexAsyncio(
                host=os.environ.get("PINECONE_HOST"),
                index_name=self.index_name
            )

    async def create_index(self, index_name: str, dimension: int, metric: str = "cosine"):
        if not await self.pinecone.has_index(index_name):
            await self.pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                deletion_protection="disabled",
                tags={"environment": "development"}
            )

    async def _embed(self, data):
        embedding = await self.embedder.embed(data)
        return embedding

    async def close(self):
        if self.pinecone:
            await self.pinecone.__aexit__(None, None, None)
        if self.embedder:
            await self.embedder.close()

class PineconeAsyncClient(PineconeAsyncClientParent):
    async def insert(self, input: bytes, metadata: dict = None,embedding:list[int]=None):
        if embedding==None: embedding = await self.embedder.embed(input)
        vector = {
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": metadata or {}
        }
        response = await self.index.upsert(vectors=[vector])
        return response

    async def search(self, data: bytes, filter: dict = None, top_k: int = 3):
        """
        Output Format :
        {
            "matches": [
                {
                    "id": "unique_id",
                    "score": 0.123456,
                    "metadata": {
                        "key1": "value1",
                        "key2": "value2"
                    }
                },
                ...
            ]
        }
        """
        embedding = await self._embed(data)
        response = await self.index.query(
            vector=embedding,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
            filter=filter
        )
              
        return response


if __name__=="__main__":

     async def example():
        embedder=embedders.AzureEmbedder(model_name="florence")
        pc= PineconeAsyncClient(embedder=embedder)
        await pc.init_indexes()

        image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Red square
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        data = buffer.getvalue()

        metadata = {"type": "example", "description": "An example image"}
        
        await pc.insert(data, metadata=metadata)
        query_response = await pc.search(data=data, top_k=3)
        print("Query Response:", query_response)
        await pc.close()

     asyncio.run(example())
