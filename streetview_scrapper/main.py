import json 
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from rag.client import PineconeAsyncClient
from rag.embedders import AzureEmbedder


async def main():

    with open('embeddings.json', 'r') as file:
        data = json.load(file)
        pc= PineconeAsyncClient()
        await pc.init_indexes()
          
        for e in data:
            emb=e.pop('embedding')
            await pc.insert(0, metadata=e, embedding=emb)

        print("Inserted all embeddings")
        await pc.close()

async def test(): 
        pass 
                 
asyncio.run(main())