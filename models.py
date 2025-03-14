# Define Pydantic models for request and response
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class SocialLinks(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    blog: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    year_graduated: str

class Experience(BaseModel):
    role: str
    company: str
    duration: str
    responsibilities: List[str]

class Employee(BaseModel):
    employee_id: str
    name: str
    username: str
    email: str
    role: str
    bio: str
    location: str
    avatar: str
    social_links: SocialLinks
    skills: List[str]
    education: List[Education]
    experience: List[Experience]
    achievements: Optional[List[str]] = []
    availability: str
    languages_spoken: List[str]

class Project(BaseModel):
    project_id: str
    title: str
    created_on: str
    description: str
    technologies: List[str]
    status: str
    category: str
    platform: str
    app_type: str
    is_cli: bool
    employee_id: Optional[str] = None
    person_id: Optional[str] = None
    screenshot: str

class EmployeeResponse(BaseModel):
    employee: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SkillsResponse(BaseModel):
    skills: Optional[str] = None
    error: Optional[str] = None

class ProjectsResponse(BaseModel):
    projects: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class ProjectResponse(BaseModel):
    project: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MistralQuery(BaseModel):
    query: str
    model: str = "mistral-large-latest"
    api_key: str

class MistralResponse(BaseModel):
    response: str