from planning_graph.planning_graph_planner import GraphPlanner
from planning_graph.planning_graph import PlanningGraph


class TestGraphPlanner:

    def test_plan(self):
        planning_graph = PlanningGraph(
            'domain/dock-worker-robot-domain.pddl',
            'domain/dock-worker-robot-problem.pddl')
        graph = planning_graph.create(max_num_of_levels=100)
        assert graph.fixed_point is False

        goal = planning_graph.goal
        graph_planner = GraphPlanner()
        layered_plan = graph_planner.plan(graph, goal)
        assert len(layered_plan.data) == 4
