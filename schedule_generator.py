# schedule_generator.py

import json
import os
from employees_manager import load_employees
from global_rules_manager import load_rules
from google import genai
from dotenv import load_dotenv

# =====================
# ENV & Gemini Client
# =====================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a shift scheduling rule parser.
Return ONLY valid JSON, no markdown, no explanation.
Use this schema:

{
  "type": "availability" | "coverage" | "limit",
  "priority": number,
  "hard": boolean,
  "applies_to": "employee" | "shift" | "global",
  "data": object
}

If cannot parse, return: {"error":"cannot_parse"}
"""

# =====================
# CONSTANTS
# =====================
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SHIFTS = ["morning", "evening"]

# =====================
# HELPER FUNCTIONS
# =====================

def create_empty_schedule():
    """Create empty schedule structure for a week"""
    return {day: {shift: [] for shift in SHIFTS} for day in DAYS}


def print_schedule(schedule):
    """Pretty print the schedule"""
    print("\n=== GENERATED SCHEDULE ===")
    for day, shifts in schedule.items():
        print(f"\n{day}")
        for shift, emps in shifts.items():
            print(f"  {shift}: {', '.join(emps)}")


# =====================
# GEMINI NLP PARSER
# =====================

def parse_nlp_rule(text: str) -> dict:
    """Send a natural language rule to Gemini and return JSON"""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[SYSTEM_PROMPT, f"Rule: {text}"]
    )
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "invalid_json"}


# =====================
# RULE MERGING
# =====================

def get_all_rules(run_nlp_rules: list):
    """Combine global rules and run-specific NLP rules"""
    data = load_rules()
    rules = data.get("rules", [])
    return rules + run_nlp_rules


# =====================
# SCHEDULE GENERATOR
# =====================

def generate_schedule_with_rules(run_nlp_rules=[]):
    """Generate weekly schedule using global + NLP rules with per-shift coverage"""
    employees_data = load_employees()
    employees = [e["name"] for e in employees_data.get("employees", [])]

    if not employees:
        print("No employees available.")
        return None

    all_rules = get_all_rules(run_nlp_rules)
    schedule = create_empty_schedule()
    emp_count = len(employees)
    emp_index = 0  # round-robin index

    # Build shift-specific coverage map
    coverage_rules = [r for r in all_rules if r.get("type") == "coverage"]
    shift_requirements = {shift: {"min": 1, "max": emp_count} for shift in SHIFTS}  # defaults

    for rule in coverage_rules:
        for req in rule.get("data", {}).get("requirements", []):
            shift = req.get("shift_type")
            if shift in SHIFTS:
                shift_requirements[shift]["min"] = req.get("min", 1)
                shift_requirements[shift]["max"] = req.get("max", emp_count)

    # Naive round-robin assignment
    for day in DAYS:
        for shift in SHIFTS:
            min_needed = shift_requirements[shift]["min"]
            max_allowed = shift_requirements[shift]["max"]
            assigned = 0

            # Assign employees until min requirement is satisfied
            while assigned < min_needed:
                employee = employees[emp_index % emp_count]

                # Check availability rules
                forbidden = [
                    r for r in all_rules
                    if r.get("type") == "availability" and r.get("data", {}).get("employee_name") == employee
                ]
                blocked = False
                for f in forbidden:
                    if shift in f.get("data", {}).get("forbidden_shifts", []):
                        blocked = True
                        break

                if not blocked and employee not in schedule[day][shift]:
                    schedule[day][shift].append(employee)
                    assigned += 1

                emp_index += 1

            # If max_allowed > min_needed, optionally add extra employees
            while len(schedule[day][shift]) < max_allowed:
                employee = employees[emp_index % emp_count]

                # Same availability check
                forbidden = [
                    r for r in all_rules
                    if r.get("type") == "availability" and r.get("data", {}).get("employee_name") == employee
                ]
                blocked = False
                for f in forbidden:
                    if shift in f.get("data", {}).get("forbidden_shifts", []):
                        blocked = True
                        break

                if not blocked and employee not in schedule[day][shift]:
                    schedule[day][shift].append(employee)

                emp_index += 1

    return schedule


# =====================
# SIMPLE RUN EXAMPLE
# =====================

if __name__ == "__main__":
    # Example: NLP rules for this run
    nlp_rule_texts = [
        "John cannot work night shifts",
        "At least 2 employees per shift"
    ]

    run_rules = []
    for text in nlp_rule_texts:
        rule = parse_nlp_rule(text)
        if "error" not in rule:
            run_rules.append(rule)

    sched = generate_schedule_with_rules(run_rules)
    if sched:
        print_schedule(sched)
