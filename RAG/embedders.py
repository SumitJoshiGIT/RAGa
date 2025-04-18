import os 
import httpx
class Embedder:
    def __init__(self, model_name: str):
        self.model_name = model_name

    async def embed(self, text: str) -> list:
        raise NotImplementedError("Subclasses should implement this method")

class AzureEmbedder(Embedder):
    def __init__(self, model_name: str):
        self.client = None
        super().__init__(model_name)

    async def embed(self, image: bytes) -> list:
        if self.client is None:
            self.client = httpx.AsyncClient()
        endpoint = os.getenv("AZURE_ENDPOINT") + "computervision/"
        key = os.getenv("AZURE_KEY")
        version = "?api-version=2023-02-01-preview&modelVersion=latest"
        vectorize_img_url = endpoint + "retrieval:vectorizeImage" + version

        headers = {
         "Content-type": "application/octet-stream",
         "Ocp-Apim-Subscription-Key": key
        }
        try:
            response = await self.client.post(vectorize_img_url, content=image, headers=headers)
          
            if response.status_code == 200:
                image_vector = response.json()["vector"]
                return image_vector
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"An error occurred while processing {image}: {e}")

    async def close(self):
        if self.client is not None:
            await self.client.aclose()
            self.client = None
        return None
    async def close(self):
        await self.client.aclose()
