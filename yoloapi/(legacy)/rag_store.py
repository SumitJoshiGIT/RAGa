import numpy as np
from functools import wraps
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from models import ImageEmbedding,TextEmbedding
from sqlalchemy import func



class ClientParent:
    def __init__(self):
        connection_string = os.getenv("DB_CONNECTION_STRING")
        self.text_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        engine = create_async_engine(connection_string, echo=True)
        self.AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    def _embedText(self, context: str):
        return self.text_model.encode(context, normalize_embeddings=True).astype(np.float32).tolist()

    def _embedImage(self, image):
        inputs = self.clip_processor(images=image, return_tensors="pt")
        outputs = self.clip_model.get_image_features(**inputs)
        image_embedding = outputs[0] / outputs[0].norm()
        return image_embedding.cpu().detach().numpy().astype(np.float32).tolist()


    @staticmethod
    def search(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with self.AsyncSessionLocal() as session:
               try: 
                query = func(self, *args, **kwargs)
                result = await session.execute(query)
                return result.scalars().all()
               except Exception as e:
                  return e 

        return wrapper
   
    @staticmethod
    def insert(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with self.AsyncSessionLocal() as session:
                async with session.begin():
                   try: 
                    item = func(self, *args, **kwargs)
                    session.add(item)
                    await session.commit()
                   except Exception as e:
                     session.rollback()
                     return e  
        return wrapper


class RAGClient(ClientParent):

    @ClientParent.search
    def searchImage(self, context, top_k: int = 5):
        embedding = np.array(self._embedImage(context)).tolist()
        return select(ImageEmbedding).order_by(func.l2_distance(ImageEmbedding.embedding, embedding)).limit(top_k)
    
    @ClientParent.search
    def searchText(self, context, top_k: int = 5):
        embedding = np.array(self._embedText(context)).tolist()
        return select(TextEmbedding).order_by(func.l2_distance(TextEmbedding.embedding,embedding)).limit(top_k)

    @ClientParent.insert
    def insertImage(self, context, metadata: str, document: str):
        embedding = self._embedImage(context)
        return ImageEmbedding(embedding=embedding, document=document, meta=metadata)

    @ClientParent.insert
    def insertText(self, context: str, metadata, document):
        embedding = self._embedText(context)
        return TextEmbedding(embedding=embedding, document=document, meta=metadata)

     