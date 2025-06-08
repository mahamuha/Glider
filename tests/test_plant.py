def test_growth():
    """Test that the plant's growth increases correctly when a task is completed."""

    from app.plant import update_growth  # Function to update plant growth
    from app.models import Plant  # Plant model class

    # Create a Plant instance with initial growth of 0
    plant = Plant(group_id=1, growth=0)

    # Simulate completing a task to trigger growth
    plant = update_growth(True, plant)

    # Check that the growth has increased by 10
    assert plant.growth == 10
