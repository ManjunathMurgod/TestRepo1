import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities as activities_data
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities_data)
    yield
    activities_data.clear()
    activities_data.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities_returns_activity_data():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Programming Class"]["max_participants"] == 20


def test_signup_for_activity_succeeds():
    # Arrange
    activity_name = "Art Workshop"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_student_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_succeeds():
    # Arrange
    activity_name = "Basketball Team"
    email = "leah@mergington.edu"
    url = f"/activities/{activity_name}/participant"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "notregistered@mergington.edu"
    url = f"/activities/{activity_name}/participant"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404():
    # Arrange
    activity_name = "Space Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/participant"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
