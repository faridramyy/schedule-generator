import json
import os

EMP_FILE = "data/employees.json"


def load_employees():
    if not os.path.exists(EMP_FILE):
        return {"employees": []}

    try:
        with open(EMP_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {"employees": []}

            data = json.loads(content)
            if "employees" not in data or not isinstance(data["employees"], list):
                return {"employees": []}

            return data

    except (json.JSONDecodeError, IOError):
        return {"employees": []}


def save_employees(data):
    os.makedirs(os.path.dirname(EMP_FILE), exist_ok=True)
    with open(EMP_FILE, "w") as f:
        json.dump(data, f, indent=2)


def list_employees():
    data = load_employees()
    employees = data["employees"]

    if not employees:
        print("No employees found.")
        return

    print("\nEmployees:")
    for emp in employees:
        print(f'{emp["id"]}. {emp["name"]}')


def add_employee(name):
    data = load_employees()
    employees = data["employees"]

    new_id = 1 if not employees else employees[-1]["id"] + 1

    employees.append({
        "id": new_id,
        "name": name
    })

    save_employees(data)
    print("Employee added successfully.")


def remove_employee(emp_id):
    data = load_employees()
    employees = data["employees"]

    for emp in employees:
        if emp["id"] == emp_id:
            employees.remove(emp)
            save_employees(data)
            print("Employee removed successfully.")
            return

    print("Employee ID not found.")


def employees_menu():
    while True:
        print("\n--- Employees Menu ---")
        print("1. List employees")
        print("2. Add employee")
        print("3. Remove employee")
        print("4. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            list_employees()

        elif choice == "2":
            name = input("Employee name: ").strip()
            if name:
                add_employee(name)
            else:
                print("Name cannot be empty.")

        elif choice == "3":
            list_employees()
            try:
                emp_id = int(input("Enter employee ID to remove: ").strip())
                remove_employee(emp_id)
            except ValueError:
                print("Invalid ID.")

        elif choice == "4":
            break

        else:
            print("Invalid choice.")
