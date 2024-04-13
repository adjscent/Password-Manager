import pytest
from app import app as flask_app
from app import NewUser, Passwords
from modules.PasswordGenerator import PasswordGenerator


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    yield flask_app


@pytest.fixture(scope="session", autouse=True)
def startup():
    try:
        user = NewUser.objects.get_or_404(username="testuser").delete()
        password = Passwords.objects.get_or_404(user="testuser").delete()
    except:
        pass


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Test the home page
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Have trouble remembering your passwords?" in response.data


# Test the login page
def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login--main__form" in response.data


# Test register
def test_register_success(client):
    response = client.post(
        "/register.py",
        data={
            "register--name": "Test User",
            "register--email": "testuser@example.com",
            "register--username": "testuser",
            "register--password": "password",
        },
    )
    assert b"login--main__form" in response.data
    assert response.status_code == 200


# Test successful login
def test_login_success(client):
    response = client.post(
        "/login.py",
        data={"login--username": "testuser", "login--password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data


# Test login failure
def test_login_failure(client):
    response = client.post(
        "/login.py",
        data={"login--username": "wronguser", "login--password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_generate_password(client):
    # Log in first
    response = client.get("/gen_pass", follow_redirects=True)
    assert response.status_code == 200
    assert b"password" in response.data


# Test password saving
def test_save_password(client):
    # Log in first
    client.post(
        "/login.py",
        data={"login--username": "testuser", "login--password": "password"},
        follow_redirects=True,
    )
    response = client.post(
        "/save_pass",
        json={
            "user": "testuser",
            "website": "example.com",
            "username": "user",
            "password": "pass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saved" in response.data


# Test password retrieval
def test_get_password(client):
    # Log in first
    client.post(
        "/login.py",
        data={"login--username": "testuser", "login--password": "password"},
        follow_redirects=True,
    )
    response = client.get("/get_pass", follow_redirects=True)
    assert response.status_code == 200
    assert b"passwords" in response.data

# Test password delete
def test_delete_password(client):
    # Log in first
    client.post(
        "/login.py",
        data={"login--username": "testuser", "login--password": "password"},
        follow_redirects=True,
    )
    response = client.post(
        "/del_pass",
        json={
            "user": "testuser",
            "website": "example.com",
            "username": "user",
            "password": "pass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"OK" in response.data