# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import json
import uvicorn

from models import EmployeeResponse, MistralQuery, MistralResponse, Project, ProjectResponse, ProjectsResponse, SkillsResponse

# Create FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="API for querying employee and project information",
    version="1.0.0"
)


with open("data.json", "r") as file:
    # Read in the data string
    json_string = file.read()
    # Parse JSON data
    data = json.loads(json_string)

with open("tools.json", "r") as file:
    # Read in the data string
    json_string = file.read()
    # Parse JSON data
    tools = json.loads(json_string)["tools"]


# Create DataFrames
employees_df = pd.DataFrame(data['employees'])
projects_df = pd.DataFrame(data['projects'])


# API routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Employee and Project API", "version": "1.0.0"}

@app.get("/employees", response_model=List[Dict[str, Any]])
async def get_all_employees():
    return employees_df.to_dict(orient='records')

@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(employee_id: str):
    if employee_id in employees_df['employee_id'].values:
        return {"employee": employees_df[employees_df['employee_id'] == employee_id].iloc[0].to_dict()}
    return {"error": "Employee ID not found."}

@app.get("/employees/name/{name}", response_model=EmployeeResponse)
async def get_employee_by_name(name: str):
    if name in employees_df['name'].values:
        return {"employee": employees_df[employees_df['name'] == name].iloc[0].to_dict()}
    return {"error": "Employee name not found."}

@app.get("/employees/{employee_id}/skills", response_model=SkillsResponse)
async def get_employee_skills_by_id(employee_id: str):
    if employee_id in employees_df['employee_id'].values:
        skills = employees_df[employees_df['employee_id'] == employee_id]['skills'].iloc[0]
        return {"skills": skills if isinstance(skills, str) else ", ".join(skills)}
    return {"error": "Employee ID not found."}

@app.get("/employees/name/{name}/skills", response_model=SkillsResponse)
async def get_employee_skills_by_name(name: str):
    if name in employees_df['name'].values:
        skills = employees_df[employees_df['name'] == name]['skills'].iloc[0]
        return {"skills": skills if isinstance(skills, str) else ", ".join(skills)}
    return {"error": "Employee name not found."}

@app.get("/employees/{employee_id}/projects", response_model=ProjectsResponse)
async def get_projects_by_employee_id(employee_id: str):
    if employee_id in projects_df['employee_id'].values:
        projects = projects_df[projects_df['employee_id'] == employee_id].to_dict(orient='records')
        return {"projects": projects}
    return {"error": "No projects found for this employee ID."}

@app.get("/employees/name/{name}/projects", response_model=ProjectsResponse)
async def get_projects_by_employee_name(name: str):
    if name in projects_df['name'].values:
        projects = projects_df[projects_df['name'] == name].to_dict(orient='records')
        return {"projects": projects}
    return {"error": "No projects found for this employee name."}

@app.get("/projects", response_model=List[Project])
async def get_all_projects():
    return projects_df.to_dict(orient='records')

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_info_by_id(project_id: str):
    if project_id in projects_df['project_id'].values:
        return {"project": projects_df[projects_df['project_id'] == project_id].iloc[0].to_dict()}
    return {"error": "Project ID not found."}

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_info_name(project_id: str):
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
        # Define function implementations
        async def get_employee_info_impl(employee_id=None, name=None):
            if employee_id:
                response = await get_employee_by_id(employee_id=employee_id)
                return json.dumps(response)
            elif name:
                response = await get_employee_by_name(name=name)   
                return json.dumps(response)
               
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        async def get_employee_skills_impl(employee_id=None, name=None):
            if employee_id:
               response = await  get_employee_skills_by_id(employee_id=employee_id)
               return json.dumps(response)
            elif name:
                response = await get_employee_skills_by_name(name=name)
                return json.dumps(response)
            
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        async def get_projects_by_employee_impl(employee_id=None, name=None):
            if employee_id:
                response = await get_projects_by_employee_id(employee_id=employee_id)
                return json.dumps(response)
            elif name:
                response = await get_projects_by_employee_name(name=name)
                return json.dumps(response)
            
            return json.dumps({'error': 'Please provide either employee_id or name.'})
        
        async def get_project_info_impl(project_id=None, title=None):
            if project_id:
                response = await get_project_info_by_id(project_id=project_id)
                return json.dumps(response)
            elif title:
                 response = await get_project_info_name
                 return json.dumps(response)
            
            return json.dumps({'error': 'Please provide either project_id or title.'})
        
        async def get_projects_by_status_impl(status):
            response = await get_projects_by_status(status=status)
            if (response):
                return json.dumps(response)
            
            return json.dumps({'error': 'No projects found with this status.'})
        
        async def get_projects_by_technology_impl(technology):
             response = await  get_projects_by_technology(technology=technology)
             return json.dumps(response)
        
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
            function_result = await names_to_functions[function_name](**function_params)
            
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