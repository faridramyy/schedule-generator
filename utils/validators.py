def validate_employee(emp):
    if not emp["id"]:
        raise ValueError("Employee ID required")
    if not emp["name"]:
        raise ValueError("Employee name required")
    if not emp["roles"]:
        raise ValueError("At least one role required")

def validate_day(day, open_time, close_time):
    if not day:
        raise ValueError("Day name required")
    if open_time >= close_time:
        raise ValueError("Open time must be before close time")
