from bot_create_cv import BotCreateCV
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import os

class Education(BaseModel):
    degree: str
    university: str
    start_year: str
    end_year: str
    description: Optional[str] = None

class Experience(BaseModel):
    company: str
    position: str
    start_year: str
    end_year: str
    description: Optional[str] = None

class ExpertType(BaseModel):
    id: int
    expert_type: str
    description: Optional[str] = None

class EngagementType(BaseModel):
    id: int
    engagement_type: str
    description: Optional[str] = None

class EngagementModel(BaseModel):
    id: int
    engagement_model: str
    description: Optional[str] = None

class UserInfo(BaseModel):
    id: int
    email: str
    contact_no: str
    bio: str
    education: List[Education]
    experience: List[Experience]
    skills: List[str]
    certifications: List[str]
    image: str
    website: str
    linkedin: str
    calendly_url: str
    expert_type_id: int
    engagement_type_id: List[int]
    engagement_model_id: List[int]
    rating: int
    first_name: str
    last_name: str
    resume: str
    dob: str
    nationality: str
    district: str
    state: str
    address: str
    expert_type: ExpertType
    engagement_types: List[EngagementType]
    engagement_models: List[EngagementModel]

class CVRequest(BaseModel):
    user_name: str
    user_info_path: UserInfo
    unique_id: str
    cv_template_path: Optional[str] = None
    cl_template_path: Optional[str] = None
    job_desc_link: Optional[str] = None
    cv_comp_type: Optional[str] = None
    cl_comp_type: Optional[str] = None

app = FastAPI()

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
            request.user_info_path,
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