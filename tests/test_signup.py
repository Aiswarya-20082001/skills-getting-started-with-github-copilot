"""
Tests for the POST /activities/{activity_name}/signup endpoint.
"""

import pytest
from urllib.parse import quote


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "newstudent@mergington.edu" in result["message"]
    assert "Chess Club" in result["message"]


def test_signup_adds_participant(client):
    """Test that signup adds participant to the activity"""
    email = "testuser234@mergington.edu"
    
    # Get initial participants count
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()["Chess Club"]["participants"].copy()
    initial_count = len(initial_participants)
    
    # Sign up
    response = client.post(
        f"/activities/Chess%20Club/signup?email={quote(email)}"
    )
    assert response.status_code == 200
    
    # Verify participant was added
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()["Chess Club"]["participants"]
    assert len(updated_participants) == initial_count + 1
    assert email in updated_participants


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity returns 404"""
    response = client.post(
        "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"].lower()


def test_signup_duplicate_fails(client):
    """Test that duplicate signup returns 400 error"""
    email = "michael@mergington.edu"  # Already in Chess Club
    
    response = client.post(
        f"/activities/Chess%20Club/signup?email={quote(email)}"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"].lower()


def test_signup_with_special_characters_in_email(client):
    """Test signup with special characters in email"""
    email = "test+alias@mergington.edu"
    
    response = client.post(
        f"/activities/Programming%20Class/signup?email={quote(email)}"
    )
    assert response.status_code == 200
    
    # Verify it was added
    activities = client.get("/activities").json()
    assert email in activities["Programming Class"]["participants"]


def test_signup_availability_decreases(client):
    """Test that available spots decrease after signup"""
    email = "spottest@mergington.edu"
    
    # Get initial availability
    initial = client.get("/activities").json()
    initial_max = initial["Basketball Team"]["max_participants"]
    initial_count = len(initial["Basketball Team"]["participants"])
    initial_spots = initial_max - initial_count
    
    # Sign up
    client.post(
        f"/activities/Basketball%20Team/signup?email={quote(email)}"
    )
    
    # Check updated availability
    updated = client.get("/activities").json()
    updated_count = len(updated["Basketball Team"]["participants"])
    updated_spots = initial_max - updated_count
    
    assert updated_spots == initial_spots - 1
