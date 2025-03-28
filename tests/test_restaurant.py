"""
Tests for restaurant core module.
"""

import pytest
from app.core.restaurant import (
    get_restaurant_by_id,
    get_restaurant_by_phone,
    get_all_restaurants,
    create_restaurant,
    update_restaurant,
    delete_restaurant,
    initialize_default_restaurant
)
from app.models.schemas import Restaurant

def test_initialize_default_restaurant():
    """
    Test initializing the default restaurant.
    """
    default_restaurant = initialize_default_restaurant()
    assert default_restaurant is not None
    assert default_restaurant.id == "default"
    assert default_restaurant.name == "Pulsara Restaurant"
    assert default_restaurant.address == "1509 W Taylor St, Chicago, IL 60607"
    assert default_restaurant.phone == "224-651-4178"

def test_get_restaurant_by_id():
    """
    Test getting a restaurant by ID.
    """
    # Initialize the default restaurant
    initialize_default_restaurant()
    
    # Get the restaurant by ID
    restaurant = get_restaurant_by_id("default")
    assert restaurant is not None
    assert restaurant.id == "default"
    assert restaurant.name == "Pulsara Restaurant"

def test_get_restaurant_by_phone():
    """
    Test getting a restaurant by phone number.
    """
    # Initialize the default restaurant
    initialize_default_restaurant()
    
    # Get the restaurant by phone
    restaurant = get_restaurant_by_phone("224-651-4178")
    assert restaurant is not None
    assert restaurant.id == "default"
    assert restaurant.name == "Pulsara Restaurant"

def test_get_all_restaurants():
    """
    Test getting all restaurants.
    """
    # Initialize the default restaurant
    initialize_default_restaurant()
    
    # Get all restaurants
    restaurants = get_all_restaurants()
    assert len(restaurants) >= 1
    assert any(r.id == "default" for r in restaurants)

def test_create_restaurant():
    """
    Test creating a new restaurant.
    """
    # Create a new restaurant
    new_restaurant = Restaurant(
        name="Test Restaurant",
        address="123 Test St, Test City, TC 12345",
        phone="555-123-4567"
    )
    created = create_restaurant(new_restaurant)
    
    # Verify the restaurant was created
    assert created is not None
    assert created.id is not None
    assert created.name == "Test Restaurant"
    
    # Verify we can retrieve it
    retrieved = get_restaurant_by_id(created.id)
    assert retrieved is not None
    assert retrieved.name == "Test Restaurant"

def test_update_restaurant():
    """
    Test updating a restaurant.
    """
    # Initialize the default restaurant
    default_restaurant = initialize_default_restaurant()
    
    # Update the restaurant
    updated = update_restaurant(default_restaurant.id, {"name": "Updated Restaurant"})
    assert updated is not None
    assert updated.id == default_restaurant.id
    assert updated.name == "Updated Restaurant"
    
    # Verify the update was persisted
    retrieved = get_restaurant_by_id(default_restaurant.id)
    assert retrieved is not None
    assert retrieved.name == "Updated Restaurant"

def test_delete_restaurant():
    """
    Test deleting a restaurant.
    """
    # Create a restaurant to delete
    new_restaurant = Restaurant(
        name="Restaurant to Delete",
        address="123 Delete St, Delete City, DC 12345",
        phone="555-987-6543"
    )
    created = create_restaurant(new_restaurant)
    
    # Delete the restaurant
    result = delete_restaurant(created.id)
    assert result is True
    
    # Verify it was deleted
    retrieved = get_restaurant_by_id(created.id)
    assert retrieved is None
