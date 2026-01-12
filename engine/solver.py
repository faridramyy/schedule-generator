from ortools.sat.python import cp_model

class ShiftSolver:
    def __init__(self, context, constraints):
        self.context = context
        self.constraints = constraints
        self.model = cp_model.CpModel()
        self.vars = {}

    def solve(self):
        self._build_vars()
        self._apply_constraints()

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status != cp_model.OPTIMAL:
            return []

        schedule = []
        for (e, d, t), v in self.vars.items():
            if solver.Value(v):
                schedule.append({
                    "employee": e,
                    "day": d,
                    "time": t
                })

        return schedule

    def _build_vars(self):
        for e in self.context["employees"]:
            for d in self.context["days"]:
                for t in self.context["time_slots"]:
                    self.vars[(e["id"], d, t)] = self.model.NewBoolVar(
                        f"x_{e['id']}_{d}_{t}"
                    )

    def _apply_constraints(self):
        for c in self.constraints:
            if c["type"] == "TIME_BOUND":
                self._apply_time_bound(c)
            if c["type"] == "SUM_LIMIT":
                self._apply_sum_limit(c)

    def _apply_time_bound(self, c):
        for (e, d, t), var in self.vars.items():
            if "role" in c["filter"]:
                employee = next(emp for emp in self.context["employees"] if emp["id"] == e)
                if c["filter"]["role"] not in employee["roles"]:
                    continue

            if "start_time" in c["params"]:
                if t < c["params"]["start_time"]:
                    self.model.Add(var == 0)

    def _apply_sum_limit(self, c):
        max_hours = c["params"]["max_hours"]

        for e in self.context["employees"]:
            emp_vars = [
                self.vars[(e["id"], d, t)]
                for d in self.context["days"]
                for t in self.context["time_slots"]
            ]
            self.model.Add(sum(emp_vars) <= max_hours)
