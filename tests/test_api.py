from datetime import date, timedelta

def payload(name="Sanjai", email="sanjai@example.com", **kwargs):
    return {"full_name": name, "email": email, **kwargs}

def test_create_get_list_and_pagination(client):
    response = client.post("/employees", json=payload(role_ids=[1], department_id=1))
    assert response.status_code == 201, response.text
    employee_id = response.json()["id"]
    assert client.get(f"/employees/{employee_id}").json()["email"] == "sanjai@example.com"
    assert client.get("/employees?page=1&size=1").json()["total"] == 1
    assert len(client.get("/employees?page=1&size=1").json()["items"]) == 1

def test_patch_and_soft_delete(client):
    created = client.post("/employees", json=payload()).json()
    updated = client.patch(f"/employees/{created['id']}", json={"full_name": "Updated Name"})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Name"
    assert client.delete(f"/employees/{created['id']}").status_code == 200
    assert client.get(f"/employees/{created['id']}").status_code == 404
    assert client.get("/employees").json()["total"] == 0

def test_filter_search_and_department_team(client):
    manager = client.post("/employees", json=payload("Manager", "manager@example.com", department_id=1)).json()
    client.post("/employees", json=payload("Sanjai Developer", "dev@example.com", department_id=1, manager_id=manager["id"]))
    client.post("/employees", json=payload("HR Person", "hr@example.com", department_id=2))
    assert client.get("/employees?department=1").json()["total"] == 2
    assert client.get("/employees?q=Developer").json()["total"] == 1
    assert len(client.get("/departments/1/employees").json()) == 2
    assert len(client.get(f"/employees/{manager['id']}/team").json()) == 1

def test_validation_and_not_found(client):
    assert client.post("/employees", json=payload(email="not-an-email")).status_code == 422
    assert client.post("/employees", json=payload(name="   ")).status_code == 422
    assert client.post("/employees", json=payload(joining_date=(date.today()+timedelta(days=1)).isoformat())).status_code == 422
    assert client.get("/employees/9999").status_code == 404

def test_duplicate_email_and_invalid_department(client):
    assert client.post("/employees", json=payload()).status_code == 201
    assert client.post("/employees", json=payload("Second", "sanjai@example.com")).status_code == 409
    assert client.post("/employees", json=payload(department_id=999)).status_code == 404

def test_page_validation(client):
    assert client.get("/employees?page=0").status_code == 422
    assert client.get("/employees?size=101").status_code == 422

def test_department_and_roles_endpoints(client):
    assert len(client.get("/departments").json()) == 2
    assert len(client.get("/roles").json()) == 2
    assert client.get("/departments/999/employees").status_code == 404
