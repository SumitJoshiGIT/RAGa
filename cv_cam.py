import asyncio
import datetime
import io
import logging
from rag.client import PineconeAsyncClient
from rag.embedders import AzureEmbedder
import PIL.Image as Image
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class CAM:
    def __init__(self, cap):
        self.cap = cap
        self.background_tasks = set()
        self.frame_count = 0
        self.running = True

    async def init_rag(self):    
        self.embedder = AzureEmbedder(model_name="florence")
        self.pc = PineconeAsyncClient(embedder=self.embedder)

    def convert_to_img(self, frame):
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        byte_io = io.BytesIO()
        pil_image.save(byte_io, format='PNG')
        return byte_io.getvalue()

    async def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to grab frame")
            return None
        return self.convert_to_img(frame)

    async def capture_frames(self, frequency, callback):
        await self.pc.init_indexes()
        delta = 1 / frequency
        count = 0

        while self.running:
            image = await self.capture_frame()
            if image and callback:
                task = asyncio.create_task(callback(image))
                self.background_tasks.add(task)
                task.add_done_callback(lambda t: self.background_tasks.discard(t))
            await asyncio.sleep(delta)
            count += 1

        logger.info(f"Captured {count} frames")
        await self.pc.close()

    def geo_filter(self,lat):
        return {
            "lat": {
                "$gte": lat - 0.00001,  
                "$lte": lat + 0.00001   
            }
        }
       
    async def context_callback(self, image,filter={}):
        logger.info("Sending query to Pinecone...")
        query_response = await self.pc.search(
            data=image,
            top_k=3,
            filter=filter,
        )
        logger.info(f"Query Response : {query_response}")
        expected_value=[x.get("score")*x.get("metadata", {}).get("angle") for x in query_response.get("matches", [{}])]
        route_id=query_response.get("matches", [{}])[0].get("metadata", {}).get("route_id")
        waypoint_id=query_response.get("matches", [{}])[0].get("metadata", {}).get("waypoint_id")
        return [route_id,expected_value]

    async def close(self):
        self.running = False
        await self.pc.close()

async def main():
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera.")
        exit()
        
    cam = CAM(cap)
    frequency = 1  
    await cam.init_rag()
    try:
        await cam.capture_frames(frequency, cam.context_callback)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        await cam.close()
        cap.release()
        print("Camera released and program ended.")


if __name__ == "__main__":
    asyncio.run(main())