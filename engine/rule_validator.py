class RuleValidator:
    REQUIRED_FIELDS = {
        "id": str,
        "name": str,
        "type": str,
        "scope": str,
        "priority": int,
        "hard": bool,
        "conditions": dict,
        "constraint": dict,
        "active": bool
    }

    def validate(self, rule):
        for field, ftype in self.REQUIRED_FIELDS.items():
            if field not in rule:
                raise ValueError(f"Missing field {field}")
            if not isinstance(rule[field], ftype):
                raise ValueError(f"Invalid type for {field}")
