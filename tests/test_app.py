from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities_returns_available_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in data
    assert "participants" in data[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={new_email}"

    # Act
    response = client.post(signup_url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert data["message"] == f"Signed up {new_email} for {activity_name}"


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = initial_activities[activity_name]["participants"][0]
    signup_url = f"/activities/{activity_name}/signup?email={existing_email}"

    # Act
    response = client.post(signup_url)
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_entry():
    # Arrange
    activity_name = "Chess Club"
    existing_email = initial_activities[activity_name]["participants"][0]
    delete_url = f"/activities/{activity_name}/participants?email={existing_email}"

    # Act
    response = client.delete(delete_url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert existing_email not in activities[activity_name]["participants"]
    assert data["message"] == f"Unregistered {existing_email} from {activity_name}"


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missingstudent@mergington.edu"
    delete_url = f"/activities/{activity_name}/participants?email={missing_email}"

    # Act
    response = client.delete(delete_url)
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Participant not found"


def test_signup_to_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={email}"

    # Act
    response = client.post(signup_url)
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"


def test_unregister_from_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    delete_url = f"/activities/{activity_name}/participants?email={email}"

    # Act
    response = client.delete(delete_url)
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"
