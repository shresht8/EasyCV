from bot_create_cv import BotCreateCV
from fastapi import FastAPI, HTTPException
from models import UserInfo, CVRequest  # Import from models.py
import os
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


# Define a Pydantic model to specify the input data structure
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
        bot_create_cv = BotCreateCV(
            request.user_name,
            request.user_info,
            request.cv_template_path,
            request.cl_template_path,
            request.job_desc_link,
            request.cv_comp_type,
            request.cl_comp_type,
        )
        print("cv compilation type:", request.cv_comp_type)
        if request.cv_template_path:
            # Process the request
            bot_create_cv.generate_cv()
        if request.cl_template_path:
            bot_create_cv.generate_cl()

        # Respond with a success message
        return {"status": "success", "message": "tex file generated successfully"}
    except Exception as e:
        # If there's an error, return an HTTPException with details
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Use uvicorn to run the app; it must be run in async mode
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
