import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from models import User, Task
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.app_context():
        db.init_app(app)
        db.create_all()
       
        u = User(login="alice", hasloHash=generate_password_hash("password"))
        db.session.add(u)
        db.session.commit()
    with app.test_client() as client:
        yield client
    
    with app.app_context():
        db.drop_all()

def login(client, login="alice", password="password"):
    return client.post("/login", data={"login":login, "password":password}, follow_redirects=True)

def test_add_task_validation(client):
    
    rv = login(client)
    assert b"Your Tasks" in rv.data or rv.status_code == 200

    
    res = client.post("/add_task", json={"title":"aa","category":"c","priority":3})
    assert res.status_code == 400
    j = res.get_json()
    assert j["status"] == 400
    assert any(e["field"]=="title" for e in j.get("fieldErrors", []))

def test_add_task_duplicate(client):
    login(client)
    
    res1 = client.post("/add_task", json={"title":"My Task 1","category":"cat","priority":3})
    assert res1.status_code == 201

    
    res2 = client.post("/add_task", json={"title":"My Task 1","category":"cat","priority":3})
    assert res2.status_code == 409
    j = res2.get_json()
    assert j["status"] == 409

def test_get_nonexistent_task_and_delete(client):
    login(client)
   
    res = client.delete("/delete_task/9999")
    assert res.status_code == 404
    j = res.get_json()
    assert j["status"] == 404

    res2 = client.put("/update_task/9999", json={"title":"abc"})
    assert res2.status_code == 404
