from pydantic import BaseModel, Field
from typing import Optional, List


class Education(BaseModel):
    degree: str = Field(..., description="The degree of the user")
    university: str = Field(..., description="The institution of the user")
    start_year: str = Field(..., description="The start year of the education")
    end_year: str = Field(..., description="End year  of the education")


class Experience(BaseModel):
    company: str = Field(..., description="The company of the user")
    position: str = Field(..., description="The position of the user")
    start_year: str = Field(..., description="The start year of the experience")
    end_year: str = Field(..., description="The end year of the experience")
    summary: str = Field(..., description="the summary of the experience")


class Project(BaseModel):
    title: str = Field(..., description="The title of the project")
    role: str = Field(..., description="The role played in the project")
    description: str = Field(..., description="Description of the project")
    responsibilities: List[str] = Field(..., description="List of responsibilities")


class UserInfo(BaseModel):
    id: int
    email: str
    contact_no: str
    bio: str
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]
    skills: List[str]
    certifications: List[str]
    image: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    calendly_url: Optional[str] = None
    first_name: str
    last_name: str
    address: str


class CVRequest(BaseModel):
    user_info: UserInfo = Field(..., description="The user info of the user")
    user_name: str = Field(..., description="The name of the user")
    cv_template_path: Optional[str] = Field(
        None, description="Path to the CV template file"
    )
    cl_template_path: Optional[str] = Field(
        None, description="Path to the cover letter template file"
    )
    job_desc_link: Optional[str] = Field(
        None, description="Link to the job description"
    )
    cv_comp_type: Optional[str] = Field(None, description="CV compilation type")
    cl_comp_type: Optional[str] = Field(
        None, description="Cover letter compilation type"
    )


class JobDescription(BaseModel):
    job_title: str = Field(..., description="The job title/position offered by company")
    job_overview: str = Field(..., description="Overview of the job")
    company_name: str = Field(..., description="Company name offering the job")
    about_company: str = Field(..., description="About the company")
    job_responsibilities: str = Field(..., description="Responsibilities of the role")
    job_requirements: str = Field(
        ..., description="Requirements/experience for the job"
    )
    skills_required: Optional[str] = Field(
        None, description="Skills required for the job"
    )
    salary_range: Optional[int] = Field(None, description="Salary range for the job")
    company_perks: Optional[str] = Field(
        None, description="Benefits offered by the company for the role"
    )
