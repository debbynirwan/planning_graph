"""Planning Graph

Description:
    This module is responsible in creating and expanding Planning Graph.

License:
    Copyright 2021 Debby Nirwan

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from .pddl_adapter import PlanningProblem
from pddlpy import Operator
from typing import List, Set, Tuple, Dict, Optional
from itertools import permutations
import pydot


class Plan(object):

    def __init__(self):
        self._plan: List[Operator] = []

    def __eq__(self, other):
        if self._plan == other.plan:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Plan object. {self._plan}"

    def append(self, action: Operator):
        self._plan.append(action)

    def remove(self, action: Operator):
        self._plan.remove(action)

    @property
    def plan(self):
        return self._plan


class LayeredPlan(object):

    def __init__(self):
        self._layered_plan: Dict[int, Plan] = {}

    def __setitem__(self, key, value):
        self._layered_plan[key] = value

    def __getitem__(self, key):
        try:
            value = self._layered_plan[key]
        except KeyError:
            value = None
        return value

    def __repr__(self):
        return f"LayeredPlan. Levels={len(self._layered_plan)}"

    @property
    def data(self):
        return self._layered_plan


class NoOpAction(Operator):

    def __init__(self, atom: tuple, name="NoOp"):
        super().__init__(name)
        self.precondition_pos.add(atom)
        self.effect_pos.add(atom)

    def __repr__(self):
        return f"NoOp Action. Preconds={self.precondition_pos}, Effects=" \
               f"{self.effect_pos}"


class Graph(object):

    def __init__(self, visualize=False):
        self.num_of_levels: int = 0
        self.act = {}
        self.act_mutexes = {}
        self.prop = {}
        self.prop_mutexes = {}
        self.fixed_point = False
        self.visualize = visualize
        self.dot = pydot.Dot(graph_type="digraph", rankdir="LR")
        self._init()

    def __repr__(self):
        return f"Planning Graph object with {self.num_of_levels} levels"

    def _init(self):
        self.act = {0: None}
        self.act_mutexes = {0: None}
        self.prop_mutexes = {0: None}

    def visualize_png(self, filename='planning_graph.png'):
        if self.visualize:
            self.dot.write_png(filename)


class PlanningGraph(object):

    def __init__(self, dom_file: str, problem_file: str, visualize=False):
        self._planning_problem = PlanningProblem(dom_file, problem_file)
        self._graph: Graph = Graph(visualize)

    def create(self, max_num_of_levels=10):
        self._graph.prop = {0: self._planning_problem.initial_state}
        self._graph.num_of_levels = 1

        for level in range(1, max_num_of_levels):
            self._graph = self.expand(self._graph)

            goal_set = self._planning_problem.goal_state
            index = self._graph.num_of_levels - 1
            proposition_list = self._graph.prop[index]
            proposition_mutex_list = self._graph.prop_mutexes[index]
            if goal_set.issubset(proposition_list):
                # goals in proposition list and
                # goals not in mutex proposition list
                goal_found = True
                for goal_pair in list(permutations(goal_set, 2)):
                    if goal_pair in proposition_mutex_list:
                        goal_found = False
                        break
                if goal_found:
                    break
            elif index > 0 and self._graph.prop[index-1] == proposition_list:
                self._graph.fixed_point = True
                break

        return self._graph

    def expand(self, gr: Graph) -> Graph:
        graph_result = gr
        level = gr.num_of_levels

        if level <= 0:
            raise ValueError("Input Graph should not be empty")

        # Compute Ai
        action_list = []
        for action in self._planning_problem.actions:
            if self._applicable(action, graph_result.prop[level - 1],
                                graph_result.prop_mutexes[level - 1]):
                action_list.append(action)
        for proposition in graph_result.prop[level - 1]:
            action_list.append(NoOpAction(proposition))
        graph_result.act[level] = action_list
        if graph_result.visualize:
            edge = pydot.Edge(self.beautify_state(
                graph_result.prop[level - 1]),
                              self.beautify_state(graph_result.act[level]), )
            graph_result.dot.add_edge(edge)

        # Compute Pi
        proposition_list = set()
        for action in action_list:
            for effect in action.effect_pos:
                proposition_list.add(effect)
        graph_result.prop[level] = proposition_list
        if graph_result.visualize:
            edge = pydot.Edge(self.beautify_state(graph_result.act[level]),
                              self.beautify_state(graph_result.prop[level]))
            graph_result.dot.add_edge(edge)

        # Compute mutex Ai
        action_mutex_list = []
        for action_pair in list(permutations(action_list, 2)):
            if self.compute_mutex_action(action_pair,
                                         graph_result.prop_mutexes[level - 1]):
                action_mutex_list.append(action_pair)
        graph_result.act_mutexes[level] = action_mutex_list

        # Compute mutex Pi
        proposition_mutex_list = []
        for proposition_pair in list(permutations(proposition_list, 2)):
            if self.compute_mutex_precondition(proposition_pair,
                                               action_list,
                                               action_mutex_list):
                if proposition_pair not in proposition_mutex_list:
                    swapped = (proposition_pair[1], proposition_pair[0])
                    if swapped not in proposition_mutex_list:
                        proposition_mutex_list.append(proposition_pair)
        graph_result.prop_mutexes[level] = proposition_mutex_list

        # update number of levels
        graph_result.num_of_levels = level + 1
        if graph_result.prop[level - 1] == proposition_list:
            graph_result.fixed_point = True

        return graph_result

    @staticmethod
    def beautify_state(state) -> str:
        """set of tuples to multiple lines of string"""
        final_string = str()
        for atom in state:
            if isinstance(atom, NoOpAction):
                pass
            elif isinstance(atom, Operator):
                atom_string = atom.operator_name + ": " + str(atom.effect_pos)
                final_string += atom_string + '\n'
            else:
                atom_string = str(atom)
                final_string += atom_string + '\n'
        return final_string

    @staticmethod
    def compute_mutex_action(pair: tuple,
                             preconds_mutex: List[Tuple[Tuple]]) -> bool:
        a = pair[0]
        b = pair[1]

        # two actions are dependent
        if a.effect_neg.intersection(b.precondition_pos.union(b.effect_pos)) \
                != set():
            return True
        if b.effect_neg.intersection(a.precondition_pos.union(a.effect_pos)) \
                != set():
            return True

        # their preconditions are mutex
        if preconds_mutex is not None:
            for mutex in preconds_mutex:
                # (p, q)
                p = mutex[0]
                q = mutex[1]
                if p in a.precondition_pos and q in b.precondition_pos:
                    return True

        return False

    @staticmethod
    def compute_mutex_precondition(proposition_pair, action_list,
                                   action_mutex):
        p = proposition_pair[0]
        q = proposition_pair[1]

        for action in action_list:
            if p in action.effect_pos and q in action.effect_pos:
                # (p, q) are not mutex if they both are produced by the
                # same action
                return False

        # every action that produces p
        actions_with_p = set()
        for action in action_list:
            if p in action.effect_pos:
                actions_with_p.add(action)

        # every action that produces q
        actions_with_q = set()
        for action in action_list:
            if q in action.effect_pos:
                actions_with_q.add(action)

        all_mutex = True
        for p_action in actions_with_p:
            for q_action in actions_with_q:
                if p_action == q_action:
                    return False
                if (p_action, q_action) not in action_mutex:
                    all_mutex = False
                    break
            if not all_mutex:
                break

        return all_mutex

    @staticmethod
    def _applicable(action: Operator, state: Set[Tuple],
                    preconditions_mutex: Optional[List[Tuple[Tuple]]]) -> bool:
        if action.precondition_pos.issubset(state) and \
                action.precondition_neg.isdisjoint(state):
            applicable = True
            if preconditions_mutex is not None:
                for precondition in list(permutations(action.precondition_pos,
                                                      2)):
                    if precondition in preconditions_mutex:
                        applicable = False
                        break
        else:
            applicable = False

        return applicable

    @property
    def initial_state(self):
        return self._planning_problem.initial_state

    @property
    def goal(self):
        return self._planning_problem.goal_state
