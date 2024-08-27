from pydantic import BaseModel, Field
from typing import Optional, List

class UserInfo(BaseModel):
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    phone: str = Field(..., description="The phone number of the user")
    address: str = Field(..., description="The address of the user")
    city: str = Field(..., description="The city of the user")

class Education(BaseModel):
    degree: str = Field(..., description="The degree of the user")
    institution: str = Field(..., description="The institution of the user")
    year: int = Field(..., description="The year of the user")

class Experience(BaseModel):
    company: str = Field(..., description="The company of the user")
    position: str = Field(..., description="The position of the user")
    year: int = Field(..., description="The year of the user")

class CVRequest(BaseModel):
    user_info: UserInfo = Field(..., description="The user info of the user")
    education: List[Education] = Field(..., description="The education of the user")
    experience: List[Experience] = Field(..., description="The experience of the user")
    user_name: str = Field(..., description="The name of the user")
    user_info_path: str = Field(..., description="Path to the user info file")
    cv_template_path: Optional[str] = Field(None, description="Path to the CV template file")
    cl_template_path: Optional[str] = Field(None, description="Path to the cover letter template file")
    job_desc_link: Optional[str] = Field(None, description="Link to the job description")
    cv_comp_type: Optional[str] = Field(None, description="CV compilation type")
    cl_comp_type: Optional[str] = Field(None, description="Cover letter compilation type")

class JobDescription(BaseModel):
    job_title: str = Field(..., description="The job title/position offered by company")
    job_overview: str = Field(..., description="Overview of the job")
    company_name: str = Field(..., description="Company name offering the job")
    about_company: str = Field(..., description="About the company")
    job_responsibilities: str = Field(..., description="Responsibilities of the role")
    job_requirements: str = Field(..., description="Requirements/experience for the job")
    skills_required: Optional[str] = Field(None, description="Skills required for the job")
    salary_range: Optional[int] = Field(None, description="Salary range for the job")
    company_perks: Optional[str] = Field(None, description="Benefits offered by the company for the role")
