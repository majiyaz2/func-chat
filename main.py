# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import json
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="API for querying employee and project information",
    version="1.0.0"
)
with open("./data.json", "r") as file:
    # Read in the data string
    json_string = file.read()
    # Parse JSON data
    data = json.loads(json_string)

# Create DataFrames
employees_df = pd.DataFrame(data['employees'])
projects_df = pd.DataFrame(data['projects'])

# Fix project data: some projects have 'person_id' instead of 'employee_id'
if 'person_id' in projects_df.columns:
    # Copy values from person_id to employee_id where employee_id is missing
    mask = projects_df['employee_id'].isna() & ~projects_df['person_id'].isna()
    projects_df.loc[mask, 'employee_id'] = projects_df.loc[mask, 'person_id']

# Define Pydantic models for request and response
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

# Helper functions
def df_row_to_dict(row):
    """Convert a DataFrame row to a dictionary with proper handling of list columns"""
    row_dict = row.to_dict()
    for key, value in row_dict.items():
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            try:
                row_dict[key] = json.loads(value)
            except:
                pass
    return row_dict

# API routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Employee and Project API", "version": "1.0.0"}

@app.get("/employees", response_model=List[Dict[str, Any]])
async def get_all_employees():
    return employees_df.to_dict(orient='records')

@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee_info(employee_id: str):
    if employee_id in employees_df['employee_id'].values:
        return {"employee": employees_df[employees_df['employee_id'] == employee_id].iloc[0].to_dict()}
    return {"error": "Employee ID not found."}

@app.get("/employees/name/{name}", response_model=EmployeeResponse)
async def get_employee_by_name(name: str):
    if name in employees_df['name'].values:
        return {"employee": employees_df[employees_df['name'] == name].iloc[0].to_dict()}
    return {"error": "Employee name not found."}

@app.get("/employees/{employee_id}/skills", response_model=SkillsResponse)
async def get_employee_skills(employee_id: str):
    if employee_id in employees_df['employee_id'].values:
        skills = employees_df[employees_df['employee_id'] == employee_id]['skills'].iloc[0]
        return {"skills": skills if isinstance(skills, str) else ", ".join(skills)}
    return {"error": "Employee ID not found."}

@app.get("/employees/{employee_id}/projects", response_model=ProjectsResponse)
async def get_projects_by_employee(employee_id: str):
    if employee_id in projects_df['employee_id'].values:
        projects = projects_df[projects_df['employee_id'] == employee_id].to_dict(orient='records')
        return {"projects": projects}
    return {"error": "No projects found for this employee ID."}

@app.get("/projects", response_model=List[Dict[str, Any]])
async def get_all_projects():
    return projects_df.to_dict(orient='records')

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_info(project_id: str):
    if project_id in projects_df['project_id'].values:
        return {"project": projects_df[projects_df['project_id'] == project_id].iloc[0].to_dict()}
    return {"error": "Project ID not found."}

@app.get("/projects/title/{title}", response_model=ProjectResponse)
async def get_project_by_title(title: str):
    if title in projects_df['title'].values:
        return {"project": projects_df[projects_df['title'] == title].iloc[0].to_dict()}
    return {"error": "Project title not found."}

@app.get("/projects/status/{status}", response_model=ProjectsResponse)
async def get_projects_by_status(status: str):
    if status in projects_df['status'].values:
        projects = projects_df[projects_df['status'] == status].to_dict(orient='records')
        return {"projects": projects}
    return {"error": f"No projects found with status '{status}'."}

@app.get("/projects/technology/{technology}", response_model=ProjectsResponse)
async def get_projects_by_technology(technology: str):
    # Filter projects that use the specified technology
    matching_projects = []
    for _, project in projects_df.iterrows():
        if isinstance(project['technologies'], list):
            if technology in project['technologies']:
                matching_projects.append(project.to_dict())
        elif isinstance(project['technologies'], str):
            if technology in project['technologies'].split(', '):
                matching_projects.append(project.to_dict())
    
    if matching_projects:
        return {"projects": matching_projects}
    return {"error": f"No projects found using {technology}."}

# Optional: Add Mistral integration
@app.post("/query", response_model=MistralResponse)
async def process_query(query_data: MistralQuery):
    try:
        from mistralai import Mistral
        
        # Define function specifications for Mistral AI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_employee_info",
                    "description": "Get information about an employee by ID or name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "The employee ID.",
                            },
                            "name": {
                                "type": "string",
                                "description": "The employee name.",
                            }
                        },
                        "required": []
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_employee_skills",
                    "description": "Get skills of an employee by ID or name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "The employee ID.",
                            },
                            "name": {
                                "type": "string",
                                "description": "The employee name.",
                            }
                        },
                        "required": []
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_projects_by_employee",
                    "description": "Get projects associated with an employee by ID or name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "The employee ID.",
                            },
                            "name": {
                                "type": "string",
                                "description": "The employee name.",
                            }
                        },
                        "required": []
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_project_info",
                    "description": "Get information about a project by ID or title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "The project ID.",
                            },
                            "title": {
                                "type": "string",
                                "description": "The project title.",
                            }
                        },
                        "required": []
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_projects_by_status",
                    "description": "Get projects with a specific status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "The project status (e.g., 'Completed', 'In Progress').",
                            }
                        },
                        "required": ["status"]
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_projects_by_technology",
                    "description": "Get projects that use a specific technology",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "technology": {
                                "type": "string",
                                "description": "The technology to filter by (e.g., 'React', 'Python').",
                            }
                        },
                        "required": ["technology"]
                    },
                },
            }
        ]
        
        # Define function implementations
        def get_employee_info_impl(employee_id=None, name=None):
            if employee_id:
                if employee_id in employees_df['employee_id'].values:
                    employee_data = employees_df[employees_df['employee_id'] == employee_id].iloc[0].to_dict()
                    return json.dumps({'employee': employee_data})
                return json.dumps({'error': 'Employee ID not found.'})
            
            elif name:
                if name in employees_df['name'].values:
                    employee_data = employees_df[employees_df['name'] == name].iloc[0].to_dict()
                    return json.dumps({'employee': employee_data})
                return json.dumps({'error': 'Employee name not found.'})
            
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        def get_employee_skills_impl(employee_id=None, name=None):
            if employee_id:
                if employee_id in employees_df['employee_id'].values:
                    skills = employees_df[employees_df['employee_id'] == employee_id]['skills'].iloc[0]
                    return json.dumps({'skills': skills})
                return json.dumps({'error': 'Employee ID not found.'})
            
            elif name:
                if name in employees_df['name'].values:
                    skills = employees_df[employees_df['name'] == name]['skills'].iloc[0]
                    return json.dumps({'skills': skills})
                return json.dumps({'error': 'Employee name not found.'})
            
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        def get_projects_by_employee_impl(employee_id=None, name=None):
            if employee_id:
                if employee_id in projects_df['employee_id'].values:
                    projects = projects_df[projects_df['employee_id'] == employee_id].to_dict(orient='records')
                    return json.dumps({'projects': projects})
                return json.dumps({'error': 'No projects found for this employee ID.'})
            
            elif name:
                if name in employees_df['name'].values:
                    employee_id = employees_df[employees_df['name'] == name]['employee_id'].iloc[0]
                    if employee_id in projects_df['employee_id'].values:
                        projects = projects_df[projects_df['employee_id'] == employee_id].to_dict(orient='records')
                        return json.dumps({'projects': projects})
                    return json.dumps({'error': 'No projects found for this employee.'})
                return json.dumps({'error': 'Employee name not found.'})
            
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        def get_project_info_impl(project_id=None, title=None):
            if project_id:
                if project_id in projects_df['project_id'].values:
                    project_data = projects_df[projects_df['project_id'] == project_id].iloc[0].to_dict()
                    return json.dumps({'project': project_data})
                return json.dumps({'error': 'Project ID not found.'})
            
            elif title:
                if title in projects_df['title'].values:
                    project_data = projects_df[projects_df['title'] == title].iloc[0].to_dict()
                    return json.dumps({'project': project_data})
                return json.dumps({'error': 'Project title not found.'})
            
            return json.dumps({'error': 'Please provide either project_id or title.'})
        
        def get_projects_by_status_impl(status):
            if status in projects_df['status'].values:
                projects = projects_df[projects_df['status'] == status].to_dict(orient='records')
                return json.dumps({'projects': projects})
            return json.dumps({'error': 'No projects found with this status.'})
        
        def get_projects_by_technology_impl(technology):
            matching_projects = []
            for _, project in projects_df.iterrows():
                if isinstance(project['technologies'], list):
                    if technology in project['technologies']:
                        matching_projects.append(project.to_dict())
                elif isinstance(project['technologies'], str):
                    if technology in project['technologies'].split(', '):
                        matching_projects.append(project.to_dict())
            
            if matching_projects:
                return json.dumps({'projects': matching_projects})
            return json.dumps({'error': f'No projects found using {technology}.'})
        
        # Map function names to their implementations
        names_to_functions = {
            'get_employee_info': get_employee_info_impl,
            'get_employee_skills': get_employee_skills_impl,
            'get_projects_by_employee': get_projects_by_employee_impl,
            'get_project_info': get_project_info_impl,
            'get_projects_by_status': get_projects_by_status_impl,
            'get_projects_by_technology': get_projects_by_technology_impl
        }
        
        # Initialize Mistral client
        client = Mistral(api_key=query_data.api_key)
        
        # Send initial query to model with tool specifications
        messages = [{"role": "user", "content": query_data.query}]
        response = client.chat.complete(
            model=query_data.model,
            messages=messages,
            tools=tools,
            tool_choice="any",
        )
        
        # Add model response to messages
        messages.append(response.choices[0].message)
        
        # Check if a tool was called
        if response.choices[0].message.tool_calls:
            # Execute the function
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            
            # Call the function
            function_result = names_to_functions[function_name](**function_params)
            
            # Add function result to messages
            messages.append({
                "role": "tool", 
                "name": function_name, 
                "content": function_result, 
                "tool_call_id": tool_call.id
            })
            
            # Get final response from model
            final_response = client.chat.complete(
                model=query_data.model,
                messages=messages
            )
            
            return {"response": final_response.choices[0].message.content}
        
        # If no tool was called, return the initial response
        return {"response": response.choices[0].message.content}
    
    except ImportError:
        return {"response": "Mistral AI SDK is not installed. Please install it using 'pip install mistralai'."}
    except Exception as e:
        return {"response": f"Error processing query: {str(e)}"}

# Run the FastAPI app with Uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)