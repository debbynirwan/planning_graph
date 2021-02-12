import pytest

from planning_graph.planning_graph import PlanningGraph, Plan, LayeredPlan, \
    NoOpAction, Graph
from pddlpy import Operator


class TestPlan:

    def test_constructor(self):
        op1 = Operator("op1")
        op2 = Operator("op2")
        expected_plan = [op1, op2]
        plan = Plan()
        plan.append(op1)
        plan.append(op2)
        assert plan.plan == expected_plan


class TestLayeredPlan:

    def test_constructor(self):
        op1 = Operator("op1")
        op2 = Operator("op2")
        plan = Plan()
        plan.append(op1)
        plan.append(op2)
        layered_plan = LayeredPlan()
        layered_plan[0] = plan

        assert layered_plan[0] == plan
        assert layered_plan.data[0] == plan


class TestNoOpAction:

    def test_dummy_action(self):
        data = (1, 2, 3)
        noop = NoOpAction(data)
        assert noop.precondition_pos == noop.effect_pos
        assert noop.precondition_neg == set()
        assert noop.effect_neg == set()


class TestGraph:

    def test_constructor(self):
        graph = Graph()
        assert graph.fixed_point is False
        assert graph.visualize is False
        assert graph.act[0] is None
        assert graph.act_mutexes[0] is None
        assert graph.prop_mutexes[0] is None


class TestPlanningGraph:

    def test_create(self):
        planning_graph = PlanningGraph(
            'domain/dock-worker-robot-domain.pddl',
            'domain/dock-worker-robot-problem.pddl')
        graph = planning_graph.create(max_num_of_levels=10)
        assert graph.num_of_levels == 4
        assert graph.fixed_point is False

    def test_expand(self):
        planning_graph = PlanningGraph(
            'domain/dock-worker-robot-domain.pddl',
            'domain/dock-worker-robot-problem.pddl')
        graph = planning_graph.create(max_num_of_levels=2)
        assert graph.num_of_levels == 2
        assert graph.fixed_point is False
        graph = planning_graph.expand(graph)
        assert graph.num_of_levels == 3
        assert graph.fixed_point is False

    def test_expand_fixed(self):
        planning_graph = PlanningGraph(
            'domain/dock-worker-robot-domain.pddl',
            'domain/dock-worker-robot-problem.pddl')
        graph = planning_graph.create(max_num_of_levels=4)
        assert graph.num_of_levels == 4
        assert graph.fixed_point is False
        graph = planning_graph.expand(graph)
        assert graph.num_of_levels == 5
        assert graph.fixed_point is True

    def test_expand_invalid(self):
        planning_graph = PlanningGraph(
            'domain/dock-worker-robot-domain.pddl',
            'domain/dock-worker-robot-problem.pddl')
        graph = Graph()
        with pytest.raises(ValueError):
            planning_graph.expand(graph)
