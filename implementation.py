import json
from main import get_employee_by_id, get_employee_by_name, get_employee_skills_by_id, get_employee_skills_by_name, get_project_info_by_id, get_project_info_name, get_projects_by_employee_id, get_projects_by_employee_name, get_projects_by_status, get_projects_by_technology


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
        