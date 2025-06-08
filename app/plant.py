def update_growth(task_completed: bool, plant):
    """
    Update the growth level of a plant based on task completion.

    If the task is completed, the plant's growth increases by 10 units,
    but does not exceed the maximum value of 100.

    Args:
        task_completed (bool): Indicates whether the task has been completed.
        plant: An object representing the plant, expected to have a 'growth' attribute.

    Returns:
        The updated plant object with possibly increased growth.
    """
    if task_completed:
        plant.growth = min(plant.growth + 10, 100)
    return plant
