from planning_graph.pddl_adapter import PlanningProblem


initial_state = [("adjacent", "loc1", "loc2"),
                 ("adjacent", "loc2", "loc1"),
                 ("in", "conta", "loc1"),
                 ("in", "contb", "loc2"),
                 ("atl", "robr", "loc1"),
                 ("atl", "robq", "loc2"),
                 ("unloaded", "robr"),
                 ("unloaded", "robq")]

goal_state = [("in", "contb", "loc1"),
              ("in", "conta", "loc2")]


class TestPlanningProblem:

    def test_constructor(self):
        pp = PlanningProblem("domain/dock-worker-robot-domain.pddl",
                             "domain/dock-worker-robot-problem.pddl")

        assert type(pp.initial_state) is set
        assert type(pp.goal_state) is set
        assert type(pp.actions) is list

    def test_initial_state(self):
        pp = PlanningProblem("domain/dock-worker-robot-domain.pddl",
                             "domain/dock-worker-robot-problem.pddl")
        assert pp.initial_state == set(initial_state)

    def test_goal_state(self):
        pp = PlanningProblem("domain/dock-worker-robot-domain.pddl",
                             "domain/dock-worker-robot-problem.pddl")
        print(f"{pp.actions}")
        assert pp.goal_state == set(goal_state)
