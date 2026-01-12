class ConstraintCompiler:
    def compile(self, rules, context):
        compiled = []

        for r in rules:
            if not r["active"]:
                continue

            if r["type"] == "TIME_WINDOW":
                compiled.append({
                    "rule_id": r["id"],
                    "type": "TIME_BOUND",
                    "filter": r["conditions"],
                    "params": r["constraint"],
                    "hard": r["hard"]
                })

            if r["type"] == "LIMIT":
                compiled.append({
                    "rule_id": r["id"],
                    "type": "SUM_LIMIT",
                    "filter": r["conditions"],
                    "params": r["constraint"],
                    "hard": r["hard"]
                })

        return compiled
