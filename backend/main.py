from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
from fast_processor_gemini import process_file  # Import your processing function
import boto3

app = FastAPI()

# Enable CORS if your frontend is hosted on a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, you can allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a temporary directory exists for uploads
UPLOAD_DIR = "uploaded_samples"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Function to generate pre-signed URLs
def get_s3_url(object_key, bucket_name="form-sage-storage", expiration=3600):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2"
    )
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df_pages, df_extracted, df_info = process_file(file_path)

        # Fix non-serializable columns
        for df in [df_pages, df_extracted, df_info]:
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, set)) else x)
        
        # for page in df_pages.to_dict(orient="records"):
        #     page["s3_url"] = get_s3_url(page["preprocessed"])

        pages = df_pages.to_dict(orient="records")
        for page in pages:
            page["s3_url"] = get_s3_url(page["preprocessed"])

        extracted = df_extracted.to_dict(orient="records") if df_extracted is not None else []
        info = df_info.to_dict(orient="records") if df_info is not None else []

        print(extracted[0])
        
        return JSONResponse({
            "filename": file.filename,
            "pages": pages,
            "extracted": extracted,
            "info": info,
            "message": "File processed successfully"
        })
    except Exception as e:
        # Log the exception details
        import traceback
        print("Error in /upload endpoint:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

