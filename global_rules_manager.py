import json
import os
from dotenv import load_dotenv
from google import genai

# =====================
# ENV & CLIENT SETUP
# =====================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

RULES_FILE = "data/global_rules.json"

# =====================
# GEMINI PROMPT
# =====================

SYSTEM_PROMPT = """
You are a rule parser for a work shift scheduling system.

Return ONLY valid JSON.
NO explanations.
NO markdown.
NO extra text.

The JSON MUST follow this schema:

{
  "type": string,
  "priority": number,
  "hard": boolean,
  "applies_to": "employee" | "shift" | "global",
  "data": object
}

Supported rule types:
- availability
- coverage
- limit

If the input is unclear, return:
{ "error": "cannot_parse" }
"""

# =====================
# FILE HANDLING
# =====================

def load_rules():
    if not os.path.exists(RULES_FILE):
        return {"rules": []}

    try:
        with open(RULES_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {"rules": []}

            data = json.loads(content)
            if "rules" not in data or not isinstance(data["rules"], list):
                return {"rules": []}

            return data
    except (json.JSONDecodeError, IOError):
        return {"rules": []}


def save_rules(data):
    os.makedirs(os.path.dirname(RULES_FILE), exist_ok=True)
    with open(RULES_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =====================
# GEMINI NLP PARSER
# =====================

def parse_rule_with_gemini(text: str) -> dict:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            SYSTEM_PROMPT,
            f"Rule: {text}"
        ]
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "invalid_json"}


# =====================
# VALIDATION
# =====================

def validate_rule(rule: dict) -> bool:
    required_fields = {"type", "priority", "hard", "applies_to", "data"}
    if not required_fields.issubset(rule.keys()):
        return False

    if rule["type"] not in {"availability", "coverage", "limit"}:
        return False

    if rule["applies_to"] not in {"employee", "shift", "global"}:
        return False

    return True


# =====================
# MENU ACTIONS
# =====================

def list_rules():
    data = load_rules()
    rules = data["rules"]

    if not rules:
        print("No global rules found.")
        return

    print("\nGlobal Rules:")
    for i, rule in enumerate(rules, start=1):
        print(f"{i}. {json.dumps(rule, indent=2)}")


def add_rule_from_nlp():
    text = input("Enter rule in natural language: ").strip()
    if not text:
        print("Rule cannot be empty.")
        return

    rule = parse_rule_with_gemini(text)

    if "error" in rule:
        print("Failed to parse rule:", rule["error"])
        return

    if not validate_rule(rule):
        print("Invalid rule structure returned by Gemini.")
        return

    data = load_rules()
    data["rules"].append(rule)
    save_rules(data)

    print("Rule added successfully.")


def remove_rule():
    data = load_rules()
    rules = data["rules"]

    if not rules:
        print("No rules to remove.")
        return

    list_rules()
    try:
        idx = int(input("Rule number to remove: ").strip()) - 1
        if idx < 0 or idx >= len(rules):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return

    rules.pop(idx)
    save_rules(data)
    print("Rule removed.")


# =====================
# GLOBAL RULES MENU
# =====================

def global_rules_menu():
    while True:
        print("\n--- Global Rules Menu (NLP Powered) ---")
        print("1. List rules")
        print("2. Add rule (NLP → Gemini)")
        print("3. Remove rule")
        print("4. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            list_rules()

        elif choice == "2":
            add_rule_from_nlp()

        elif choice == "3":
            remove_rule()

        elif choice == "4":
            break

        else:
            print("Invalid choice.")
