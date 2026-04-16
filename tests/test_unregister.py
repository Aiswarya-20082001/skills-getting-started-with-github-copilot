"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest
from urllib.parse import quote


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    email = "michael@mergington.edu"  # Already in Chess Club
    
    response = client.delete(
        f"/activities/Chess%20Club/unregister?email={quote(email)}"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert "Chess Club" in result["message"]


def test_unregister_removes_participant(client):
    """Test that unregister removes participant from the activity"""
    email = "daniel@mergington.edu"  # Already in Chess Club
    
    # Get initial participants count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Chess Club"]["participants"])
    assert email in initial_response.json()["Chess Club"]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/Chess%20Club/unregister?email={quote(email)}"
    )
    assert response.status_code == 200
    
    # Verify participant was removed
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()["Chess Club"]["participants"]
    assert len(updated_participants) == initial_count - 1
    assert email not in updated_participants


def test_unregister_nonexistent_activity(client):
    """Test unregister from non-existent activity returns 404"""
    response = client.delete(
        "/activities/NonExistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "not found" in result["detail"].lower()


def test_unregister_not_enrolled(client):
    """Test unregister for student not enrolled returns 400 error"""
    email = "notenrolled@mergington.edu"
    
    response = client.delete(
        f"/activities/Art%20Studio/unregister?email={quote(email)}"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "detail" in result
    assert "not signed up" in result["detail"].lower()


def test_unregister_availability_increases(client):
    """Test that available spots increase after unregister"""
    email = "john@mergington.edu"  # Already in Gym Class
    
    # Get initial availability
    initial = client.get("/activities").json()
    initial_max = initial["Gym Class"]["max_participants"]
    initial_count = len(initial["Gym Class"]["participants"])
    initial_spots = initial_max - initial_count
    
    # Unregister
    client.delete(
        f"/activities/Gym%20Class/unregister?email={quote(email)}"
    )
    
    # Check updated availability
    updated = client.get("/activities").json()
    updated_count = len(updated["Gym Class"]["participants"])
    updated_spots = initial_max - updated_count
    
    assert updated_spots == initial_spots + 1


def test_signup_then_unregister_flow(client):
    """Test complete signup then unregister flow"""
    email = "flowtest@mergington.edu"
    activity = "Soccer Club"
    
    # Initial state - not enrolled
    initial = client.get("/activities").json()
    assert email not in initial[activity]["participants"]
    
    # Sign up
    signup_response = client.post(
        f"/activities/{quote(activity)}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200
    
    # Verify enrolled
    after_signup = client.get("/activities").json()
    assert email in after_signup[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    )
    assert unregister_response.status_code == 200
    
    # Verify not enrolled
    after_unregister = client.get("/activities").json()
    assert email not in after_unregister[activity]["participants"]
