import json
import os
from utils.validators import validate_employee, validate_day
from engine.rule_validator import RuleValidator
from engine.conflict_resolver import ConflictResolver
from engine.constraint_compiler import ConstraintCompiler
from engine.solver import ShiftSolver

DATA_DIR = "data"
WEEK_ID = "test-week"

def load_json(path, default=None):
    if default is None:
        default = []

    if not os.path.exists(path):
        return default

    with open(path, "r") as f:
        content = f.read().strip()
        if not content:
            return default
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in {path}: {e}")

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ===================== MAIN MENU =====================

def main_menu():
    while True:
        print("\n==============================")
        print(" SHIFT SCHEDULER SYSTEM")
        print("==============================")
        print("1. Manage Employees")
        print("2. Manage Store Days")
        print("3. Validate Rules")
        print("4. Check Rule Conflicts")
        print("5. Compile Constraints")
        print("6. Run Scheduler")
        print("7. View Schedule")
        print("8. Exit")

        choice = input("Select option: ")

        if choice == "1":
            employee_menu()
        elif choice == "2":
            day_menu()
        elif choice == "3":
            validate_rules()
        elif choice == "4":
            check_conflicts()
        elif choice == "5":
            compile_constraints()
        elif choice == "6":
            run_scheduler()
        elif choice == "7":
            view_schedule()
        elif choice == "8":
            break
        else:
            print("❌ Invalid option")

# ===================== EMPLOYEES =====================

def employee_menu():
    while True:
        print("\n--- EMPLOYEE MANAGEMENT ---")
        print("1. View Employees")
        print("2. Add Employee")
        print("3. Remove Employee")
        print("4. Back")

        choice = input("Select: ")

        if choice == "1":
            employees = load_json(f"{DATA_DIR}/employees.json")
            print(json.dumps(employees, indent=2))

        elif choice == "2":
            add_employee()

        elif choice == "3":
            remove_employee()

        elif choice == "4":
            break

def add_employee():
    employees = load_json(f"{DATA_DIR}/employees.json")

    emp = {
        "id": input("Employee ID: ").strip(),
        "name": input("Name: ").strip(),
        "roles": input("Roles (comma separated): ").split(",")
    }

    validate_employee(emp)

    employees.append(emp)
    save_json(f"{DATA_DIR}/employees.json", employees)
    print("✅ Employee added")

def remove_employee():
    employees = load_json(f"{DATA_DIR}/employees.json")
    emp_id = input("Employee ID to remove: ").strip()

    employees = [e for e in employees if e["id"] != emp_id]
    save_json(f"{DATA_DIR}/employees.json", employees)
    print("✅ Employee removed")

# ===================== DAYS =====================

def day_menu():
    while True:
        print("\n--- STORE DAYS MANAGEMENT ---")
        print("1. View Days")
        print("2. Add / Edit Day")
        print("3. Remove Day")
        print("4. Back")

        choice = input("Select: ")

        if choice == "1":
            store = load_json(f"{DATA_DIR}/store_config.json")
            print(json.dumps(store, indent=2))

        elif choice == "2":
            add_or_edit_day()

        elif choice == "3":
            remove_day()

        elif choice == "4":
            break

def add_or_edit_day():
    store = load_json(f"{DATA_DIR}/store_config.json") or {"days": {}, "time_slots": []}

    day = input("Day name (e.g. Monday): ").strip()
    open_time = input("Open time (HH:MM): ")
    close_time = input("Close time (HH:MM):")

    validate_day(day, open_time, close_time)

    store["days"][day] = {
        "open": open_time,
        "close": close_time
    }

    store["time_slots"] = sorted(
        list(set(store["time_slots"] + [open_time, close_time]))
    )

    save_json(f"{DATA_DIR}/store_config.json", store)
    print("✅ Day saved")

def remove_day():
    store = load_json(f"{DATA_DIR}/store_config.json")
    day = input("Day to remove: ").strip()

    store["days"].pop(day, None)
    save_json(f"{DATA_DIR}/store_config.json", store)
    print("✅ Day removed")

# ===================== ENGINE =====================

def validate_rules():
    rules = load_json(f"{DATA_DIR}/rules/global_rules.json")
    validator = RuleValidator()
    for r in rules:
        validator.validate(r)
    print("✅ Rules valid")

def check_conflicts():
    rules = load_json(f"{DATA_DIR}/rules/global_rules.json")
    resolver = ConflictResolver()
    result = resolver.resolve(rules)
    print(json.dumps(result, indent=2))

def compile_constraints():
    rules = load_json(f"{DATA_DIR}/rules/global_rules.json")
    store = load_json(f"{DATA_DIR}/store_config.json")
    employees = load_json(f"{DATA_DIR}/employees.json")

    compiler = ConstraintCompiler()
    constraints = compiler.compile(rules, {
        "employees": employees,
        "days": list(store["days"].keys()),
        "time_slots": store["time_slots"]
    })

    os.makedirs(f"{DATA_DIR}/compiled", exist_ok=True)
    save_json(f"{DATA_DIR}/compiled/{WEEK_ID}.json", constraints)
    print("✅ Constraints compiled")

def run_scheduler():
    constraints = load_json(f"{DATA_DIR}/compiled/{WEEK_ID}.json")
    store = load_json(f"{DATA_DIR}/store_config.json")
    employees = load_json(f"{DATA_DIR}/employees.json")

    solver = ShiftSolver({
        "employees": employees,
        "days": list(store["days"].keys()),
        "time_slots": store["time_slots"]
    }, constraints)

    schedule = solver.solve()

    os.makedirs(f"{DATA_DIR}/schedules", exist_ok=True)
    save_json(f"{DATA_DIR}/schedules/{WEEK_ID}.json", schedule)
    print("✅ Schedule generated")

def view_schedule():
    schedule = load_json(f"{DATA_DIR}/schedules/{WEEK_ID}.json")
    for s in schedule:
        print(s)
