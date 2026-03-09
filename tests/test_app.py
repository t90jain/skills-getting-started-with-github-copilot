"""
Test suite for the High School Management System API

Tests are structured using the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Tests for retrieving all activities"""

    def test_get_all_activities(self):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Club", "Science Club"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        returned_activities = response.json()
        for activity in expected_activities:
            assert activity in returned_activities
        assert len(returned_activities) == len(activities)


class TestSignupForActivity:
    """Tests for signing up students for activities"""

    def test_signup_for_activity_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

        # Cleanup
        activities[activity_name]["participants"].remove(email)

    def test_signup_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self):
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_at_capacity(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        original_count = len(activities[activity_name]["participants"])
        max_capacity = activities[activity_name]["max_participants"]
        for i in range(max_capacity - original_count):
            activities[activity_name]["participants"].append(f"temp_student_{i}@mergington.edu")

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "max capacity" in response.json()["detail"]

        # Cleanup
        for i in range(max_capacity - original_count):
            activities[activity_name]["participants"].pop()


class TestRemoveParticipant:
    """Tests for removing students from activities"""

    def test_remove_participant_success(self):
        # Arrange
        activity_name = "Science Club"
        email = "test_remove@mergington.edu"
        activities[activity_name]["participants"].append(email)
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_from_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        # Arrange
        # (No specific state needed for this test)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
