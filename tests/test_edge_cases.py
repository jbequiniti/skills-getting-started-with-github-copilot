"""
Additional edge case tests for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestEdgeCases:
    """Test class for edge cases and error scenarios."""

    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)

    def test_signup_with_empty_email(self):
        """Test signup with empty email parameter."""
        response = self.client.post("/activities/Chess Club/signup?email=")
        # FastAPI should handle this gracefully
        assert response.status_code in [200, 400, 422]

    def test_signup_with_missing_email_param(self):
        """Test signup without email parameter."""
        response = self.client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity

    def test_unregister_with_empty_email(self):
        """Test unregistration with empty email parameter."""
        response = self.client.delete("/activities/Chess Club/unregister?email=")
        # Check the actual response - could be success if empty string was somehow registered,
        # or failure if not registered
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            # If successful, empty string was in participants list
            data = response.json()
            assert "message" in data
        else:
            # If failed, empty string was not registered
            data = response.json()
            assert "not registered" in data["detail"]

    def test_unregister_with_missing_email_param(self):
        """Test unregistration without email parameter."""
        response = self.client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Unprocessable Entity

    def test_activity_name_with_special_characters(self):
        """Test operations with activity names containing special characters."""
        # URL encoding is handled by the client, but let's test some scenarios
        response = self.client.get("/activities")
        activities = response.json()
        
        # Test with an existing activity that might have spaces
        for activity_name in activities.keys():
            if " " in activity_name:
                # Test signup
                signup_response = self.client.post(
                    f"/activities/{activity_name}/signup?email=test@mergington.edu"
                )
                assert signup_response.status_code in [200, 400]  # Success or duplicate
                break

    def test_concurrent_signups_same_student(self):
        """Test multiple rapid signups for the same student to same activity."""
        activity_name = "Science Club"
        email = "concurrent@mergington.edu"
        
        # Make multiple rapid requests
        responses = []
        for _ in range(3):
            response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
            responses.append(response)
        
        # Only one should succeed, others should fail with duplicate error
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 1

    def test_case_sensitive_activity_names(self):
        """Test that activity names are case sensitive."""
        response1 = self.client.post("/activities/chess club/signup?email=test@mergington.edu")
        response2 = self.client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # First should fail (wrong case), second should succeed or fail due to duplicate
        assert response1.status_code == 404
        assert response2.status_code in [200, 400]

    def test_long_email_addresses(self):
        """Test with very long email addresses."""
        long_email = "a" * 100 + "@mergington.edu"
        response = self.client.post(f"/activities/Chess Club/signup?email={long_email}")
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_unicode_in_email(self):
        """Test with unicode characters in email addresses."""
        unicode_email = "tëst@mergington.edu"
        response = self.client.post(f"/activities/Chess Club/signup?email={unicode_email}")
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_multiple_operations_same_student(self):
        """Test signup followed by unregister for the same student."""
        activity_name = "Drama Society"
        email = "testuser@mergington.edu"
        
        # First signup
        signup_response = self.client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Try to unregister again (should fail)
        unregister_again = self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_again.status_code == 400

    def test_activities_endpoint_returns_consistent_data(self):
        """Test that activities endpoint returns consistent data structure."""
        response1 = self.client.get("/activities")
        response2 = self.client.get("/activities")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Data should be identical (assuming no concurrent modifications)
        data1 = response1.json()
        data2 = response2.json()
        
        assert len(data1) == len(data2)
        assert set(data1.keys()) == set(data2.keys())


class TestDataIntegrity:
    """Test class for data integrity and state management."""

    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)

    def test_participant_count_consistency(self):
        """Test that participant counts remain consistent after operations."""
        # Get initial state
        initial_response = self.client.get("/activities")
        initial_activities = initial_response.json()
        
        # Pick an activity and count initial participants
        activity_name = "Art Club"
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Add a participant
        email = "integrity@mergington.edu"
        self.client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Check count increased
        after_signup = self.client.get("/activities")
        after_signup_activities = after_signup.json()
        after_signup_count = len(after_signup_activities[activity_name]["participants"])
        
        assert after_signup_count == initial_count + 1
        assert email in after_signup_activities[activity_name]["participants"]
        
        # Remove the participant
        self.client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Check count decreased
        after_unregister = self.client.get("/activities")
        after_unregister_activities = after_unregister.json()
        after_unregister_count = len(after_unregister_activities[activity_name]["participants"])
        
        assert after_unregister_count == initial_count
        assert email not in after_unregister_activities[activity_name]["participants"]