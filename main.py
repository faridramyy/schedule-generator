from employees_manager import employees_menu
from global_rules_manager import global_rules_menu
from schedule_generator import generate_schedule_with_rules, print_schedule, parse_nlp_rule


def show_menu():
    print("\n=== SHIFT SCHEDULER ===")
    print("1. Employees")
    print("2. Rules (global) [NLP → Gemini]")
    print("3. Generate schedule")
    print("4. Exit")

def main():
    while True:
        show_menu()
        choice = input("Select option: ").strip()

        if choice == "1":
            employees_menu()

        elif choice == "2":
            global_rules_menu()

        elif choice == "3":
            # Ask user for NLP rules for this run
            run_rules_texts = []
            print("\nEnter run-specific rules in natural language.")
            print("Type 'done' when finished.")
            while True:
                text = input("Rule: ").strip()
                if text.lower() == "done":
                    break
                if text:
                    run_rules_texts.append(text)

            # Parse NLP rules via Gemini
            run_rules = []
            for text in run_rules_texts:
                rule = parse_nlp_rule(text)
                if "error" not in rule:
                    run_rules.append(rule)
                else:
                    print(f"Could not parse rule: {text} -> {rule.get('error')}")

            # Generate schedule
            schedule = generate_schedule_with_rules(run_rules)
            if schedule:
                print_schedule(schedule)

        elif choice == "4":
            print("Goodbye 👋")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
