class ConflictResolver:
    def resolve(self, rules):
        seen = {}
        conflicts = []

        for r in rules:
            key = (r["type"], tuple(sorted(r["conditions"].items())))
            if key in seen:
                conflicts.append(
                    f"Conflict between {seen[key]['id']} and {r['id']}"
                )
            else:
                seen[key] = r

        return {
            "blocked": len(conflicts) > 0,
            "conflicts": conflicts
        }
