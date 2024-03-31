from bot_create_cv import BotCreateCV
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# Define a Pydantic model to specify the input data structure
class CVRequest(BaseModel):
    arg1: str
    arg2: str
    arg3: str
    arg4: str


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/generate_cv/")
async def generate_cv(request: CVRequest):
    # Your existing code to handle the arguments and generate the CV
    try:
        # Set OPENAI_API_KEY environment variable
        os.environ[
            "OPENAI_API_KEY"
        ] = "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"

        # Initialize the bot with provided arguments
        bot_create_cv = BotCreateCV(request.arg1, request.arg2, request.arg3)

        # Process the request
        bot_create_cv.generate_cv()

        # Respond with a success message
        return {"status": "success", "message": "tex file generated successfully"}
    except Exception as e:
        # If there's an error, return an HTTPException with details
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Use uvicorn to run the app; it must be run in async mode
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
