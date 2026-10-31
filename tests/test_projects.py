from fastapi.testclient import TestClient
from release_tracker.main import app

# Set up the test client.
client = TestClient(app)


def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# test project with id 
def test_get_project():
    response = client.get("/projects/1")
    assert response.status_code == 200
    data = response.json()
    print("Response data",data)
    assert data["id"] == 1

def test_create_project():
    ## The database normally generates the project ID.
    response = client.post("/projects", json = {"name": "Middleware Apii", "description":"Middleware APII Project"})
    print("Response",response.json())
    assert response.status_code == 201 


      
    

