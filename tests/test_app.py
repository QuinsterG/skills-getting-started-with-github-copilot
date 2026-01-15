"""Tests for the Mergington High School API"""
import pytest


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    """Tests for getting activities"""

    def test_get_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data

    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_activities_have_participants(self, client, reset_activities):
        """Test that initial participants are present"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Basketball"]["participants"]
        assert "james@mergington.edu" in data["Tennis Club"]["participants"]


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "test@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert email in participants

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when already registered for an activity"""
        email = "alex@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multisport@mergington.edu"
        
        client.post(f"/activities/Basketball/signup?email={email}")
        client.post(f"/activities/Tennis Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        
        assert email in data["Basketball"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "alex@mergington.edu"
        client.delete(f"/activities/Basketball/unregister?email={email}")
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert email not in participants

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when not registered for an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "signup_then_unregister@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Basketball/unregister?email={email}")
        response = client.get("/activities")
        assert email not in response.json()["Basketball"]["participants"]
