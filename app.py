from fastapi import FastAPI , HTTPException
from RAGStore import RAGClient
from dotenv import load_dotenv
from types import ImageMeta , TextMeta
from fastapi.responses import JSONResponse

load_dotenv()
app= FastAPI()
store= RAGStore()

@app.post("/getImageContext")
async def request(image: UploadFile):       
    
    try:
      context=store.searchImage(image)
      return {"status": "success","data":context}
    except Exception as e :
        raise HTTPException(
            status_code=500,
            detail=f"Error in retrieval: {str(e)}"
        )

@app.post("/getTextContext")
async def request(context: str):
    
    try:    
        context=await store.searchText(context)
        return {"status": "success","data":context}
    except Exception as e :
        raise HTTPException(
            status_code=500,
            detail=f"Error in retrieval: {str(e)}"
        )

@app.post("/protected/insertImage")
async def insert_image(image: UploadFile,context: str,meta: ImageMeta):
    
    try:
        result = await store.insertImage(image, context, meta)
        return {"status": "success", "message": "Image inserted", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/protected/insertText")
async def insert_text(context: str,document: str,meta: TextMeta):
    
    try:
        result = await store.insertText(document, context, meta)
        return {"status": "success", "message": "Text inserted", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing text: {str(e)}"
        )        

        






