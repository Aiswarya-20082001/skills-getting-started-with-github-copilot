"""
Tests for the GET /activities endpoint.
"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0


def test_get_activities_contains_required_fields(client):
    """Test that each activity contains required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert all(field in activity_data for field in required_fields)
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_participants_are_emails(client):
    """Test that participants are valid email strings"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation


def test_get_activities_chess_club_exists(client):
    """Test that Chess Club activity exists with expected data"""
    response = client.get("/activities")
    activities = response.json()
    
    assert "Chess Club" in activities
    chess_club = activities["Chess Club"]
    assert chess_club["max_participants"] == 12
    assert isinstance(chess_club["participants"], list)
