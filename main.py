# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import json
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Employee and Project API",
    description="API for querying employee and project information",
    version="1.0.0"
)

# Load the data from JSON
data_json = """
{
  "employees": [
    {
      "employee_id": "001",
      "name": "John Doe",
      "username": "johndoe123",
      "email": "johndoe@example.com",
      "role": "Full Stack Developer",
      "bio": "I am a passionate full stack developer with experience in building web applications using modern technologies. I love creating clean, efficient, and user-friendly solutions. In my free time, I enjoy learning about new frameworks, contributing to open-source projects, and solving coding challenges.",
      "location": "New York, USA",
      "avatar": "https://img.icons8.com/ios-filled/50/image.png",
      "social_links": {
        "github": "https://github.com/johndoe123",
        "linkedin": "https://linkedin.com/in/johndoe123",
        "portfolio": "https://johndoeportfolio.com",
        "blog": "https://johndoe.dev/blog"
      },
      "skills": [
        "JavaScript",
        "React",
        "Node.js",
        "MongoDB",
        "Express",
        "Python",
        "HTML/CSS",
        "Docker"
      ],
      "education": [
        {
          "degree": "Bachelor's in Computer Science",
          "institution": "University of New York",
          "year_graduated": "2022"
        },
        {
          "degree": "Certified Web Developer",
          "institution": "Udemy",
          "year_graduated": "2023"
        }
      ],
      "experience": [
        {
          "role": "Junior Web Developer",
          "company": "Tech Solutions Inc.",
          "duration": "2022-2023",
          "responsibilities": [
            "Developed user interfaces using React",
            "Collaborated on API development with Node.js",
            "Implemented MongoDB for database management"
          ]
        }
      ],
      "achievements": [
        "Winner of 'Best Web Application' at Hackathon 2023",
        "Completed 100+ coding challenges on LeetCode"
      ],
      "availability": "Available for Freelance",
      "languages_spoken": ["English", "Spanish"]
    },
    {
      "employee_id": "002",
      "name": "Alice Smith",
      "username": "alicesmith456",
      "email": "alice.smith@example.com",
      "role": "Frontend Developer",
      "bio": "Frontend developer focused on building responsive and user-friendly web interfaces. I enjoy turning ideas into code using the latest frameworks and technologies. Outside of work, I enjoy UI/UX design and photography.",
      "location": "San Francisco, USA",
      "avatar": "https://img.icons8.com/ios-filled/50/image.png",
      "social_links": {
        "github": "https://github.com/alicesmith456",
        "linkedin": "https://linkedin.com/in/alicesmith456",
        "portfolio": "https://alicesmithportfolio.com"
      },
      "skills": [
        "HTML",
        "CSS",
        "JavaScript",
        "Vue.js",
        "Sass",
        "Webpack"
      ],
      "education": [
        {
          "degree": "Bachelor's in Web Development",
          "institution": "San Francisco State University",
          "year_graduated": "2021"
        }
      ],
      "experience": [
        {
          "role": "Frontend Developer",
          "company": "Creative Web Studio",
          "duration": "2021-2023",
          "responsibilities": [
            "Developed and maintained responsive websites using Vue.js",
            "Collaborated with design teams to create UI/UX designs",
            "Optimized performance and accessibility of web pages"
          ]
        }
      ],
      "availability": "Open to Full-time Opportunities",
      "languages_spoken": ["English"]
    },
    {
      "employee_id": "003",
      "name": "Bob Johnson",
      "username": "bobjohnson789",
      "email": "bob.johnson@example.com",
      "role": "Data Scientist",
      "bio": "A data scientist with expertise in machine learning, data analysis, and statistical modeling. I love extracting insights from data and building predictive models that solve real-world problems.",
      "location": "Chicago, USA",
      "avatar": "https://img.icons8.com/ios-filled/50/image.png",
      "social_links": {
        "github": "https://github.com/bobjohnson789",
        "linkedin": "https://linkedin.com/in/bobjohnson789",
        "portfolio": "https://bobjohnsonportfolio.com"
      },
      "skills": [
        "Python",
        "R",
        "Machine Learning",
        "Pandas",
        "NumPy",
        "TensorFlow"
      ],
      "education": [
        {
          "degree": "Master's in Data Science",
          "institution": "University of Chicago",
          "year_graduated": "2022"
        }
      ],
      "experience": [
        {
          "role": "Data Scientist",
          "company": "Data Analytics Corp.",
          "duration": "2022-2024",
          "responsibilities": [
            "Developed predictive models using machine learning algorithms",
            "Conducted data analysis to identify trends and insights",
            "Collaborated with cross-functional teams to implement data-driven solutions"
          ]
        }
      ],
      "availability": "Available for Consulting",
      "languages_spoken": ["English"]
    }
  ],
  "projects": [
    {
      "project_id": "001",
      "title": "Portfolio Website",
      "created_on": "2023-08-15",
      "description": "A personal portfolio website showcasing my work and skills.",
      "technologies": ["HTML", "CSS", "JavaScript", "React"],
      "status": "Completed",
      "category": "Web Development",
      "platform": "Web",
      "app_type": "Single-page Application",
      "is_cli": false,
      "employee_id": "001",
      "screenshot": "https://img.icons8.com/ios-filled/50/image.png"
    },
    {
      "project_id": "002",
      "title": "E-commerce Platform",
      "created_on": "2024-01-10",
      "description": "An online store where users can browse and purchase products.",
      "technologies": ["Node.js", "Express", "MongoDB", "React"],
      "status": "In Progress",
      "category": "Web Development",
      "platform": "Web",
      "app_type": "Single-page Application",
      "is_cli": false,
      "person_id": "001",
      "screenshot": "https://img.icons8.com/ios-filled/50/image.png"
    },
    {
      "project_id": "003",
      "title": "Personal Blog",
      "created_on": "2023-11-01",
      "description": "A personal blog to share tech tutorials and articles.",
      "technologies": ["Vue.js", "Sass", "Node.js"],
      "status": "Completed",
      "category": "Blog",
      "platform": "Web",
      "app_type": "Single-page Application",
      "is_cli": false,
      "employee_id": "002",
      "screenshot": "https://img.icons8.com/ios-filled/50/image.png"
    },
    {
      "project_id": "004",
      "title": "Data Analysis Tool",
      "created_on": "2024-02-01",
      "description": "A tool to analyze and visualize large datasets using machine learning.",
      "technologies": ["Python", "TensorFlow", "Pandas"],
      "status": "In Progress",
      "category": "Data Science",
      "platform": "Desktop",
      "app_type": "Desktop Application",
      "is_cli": false,
      "employee_id": "003",
      "screenshot": "https://img.icons8.com/ios-filled/50/image.png"
    },
    {
      "project_id": "005",
      "title": "Task Manager CLI",
      "created_on": "2024-01-15",
      "description": "A simple command-line interface to manage tasks and to-dos.",
      "technologies": ["Python"],
      "status": "Completed",
      "category": "CLI Application",
      "platform": "Cross-platform",
      "app_type": "Command-line Interface",
      "is_cli": true,
      "employee_id": "003",
      "screenshot": "https://img.icons8.com/ios-filled/50/image.png"
    }
  ]
}
"""

# Parse JSON data
data = json.loads(data_json)

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