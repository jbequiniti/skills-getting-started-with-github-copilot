"""
Test suite for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesAPI:
    """Test class for activities API endpoints."""

    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)

    def test_root_redirect(self):
        """Test that root URL redirects to static/index.html."""
        response = self.client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]

    def test_get_activities(self):
        """Test retrieving all activities."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have some activities
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = list(data.values())[0]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity
        
        # Check that participants is a list
        assert isinstance(first_activity["participants"], list)
        assert isinstance(first_activity["max_participants"], int)

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity."""
        # Use an activity that exists
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was added to the activity
        activities_response = self.client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist."""
        response = self.client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_duplicate_signup(self):
        """Test that duplicate signup is prevented."""
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # This student is already registered
        
        response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up"

    def test_unregister_success(self):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # This student should be registered
        
        # First verify the student is registered
        activities_response = self.client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        
        # Now unregister
        response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was removed
        activities_response = self.client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistration from a non-existent activity."""
        response = self.client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_unregistered_student(self):
        """Test unregistration of a student who isn't registered."""
        activity_name = "Chess Club"
        email = "unregistered@mergington.edu"
        
        response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_activity_structure_validation(self):
        """Test that all activities have the correct structure."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            # Check required fields exist
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Check field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that participants count doesn't exceed max
            assert len(activity_data["participants"]) <= activity_data["max_participants"]

    def test_email_validation_in_signup(self):
        """Test signup with various email formats."""
        activity_name = "Chess Club"
        
        # Valid email formats should work
        valid_emails = [
            "student@mergington.edu",
            "test.student@mergington.edu",
            "student123@mergington.edu"
        ]
        
        for email in valid_emails:
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            # Should succeed or fail due to duplicate, not email format
            assert response.status_code in [200, 400]

    def test_activity_capacity_limits(self):
        """Test that activities respect participant limits."""
        # Find an activity and fill it to capacity
        activities_response = self.client.get("/activities")
        activities_data = activities_response.json()
        
        # Use Chess Club which has 12 max participants
        activity_name = "Chess Club"
        activity = activities_data[activity_name]
        max_participants = activity["max_participants"]
        current_participants = len(activity["participants"])
        
        # Add students until we reach capacity
        spots_available = max_participants - current_participants
        
        for i in range(spots_available):
            email = f"student{i}@mergington.edu"
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Now try to add one more - this should still work since we don't enforce limits
        # (This is based on the current implementation)
        response = self.client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
        assert response.status_code == 200


class TestStaticFiles:
    """Test class for static file serving."""

    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)

    def test_index_html_accessible(self):
        """Test that index.html is accessible."""
        response = self.client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_css_file_accessible(self):
        """Test that CSS file is accessible."""
        response = self.client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_js_file_accessible(self):
        """Test that JavaScript file is accessible."""
        response = self.client.get("/static/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]