"""PDDL Adapter

Description:
    The adaptation layer (wrapper) of pddlpy module.

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
from pddlpy import DomainProblem, Operator, Atom
from typing import Set, Tuple, List
import itertools


class PlanningProblem(object):

    def __init__(self, dom_file: str, problem_file: str):
        self._domain_file = dom_file
        self._problem_file = problem_file
        self._domain_problem = DomainProblem(self._domain_file,
                                             self._problem_file)
        self._initial_state = self._to_set_of_tuples(self._domain_problem.
                                                     initialstate())
        self._goal_state = self._to_set_of_tuples(self._domain_problem.goals())
        self._actions = self._get_ground_operators()

    @staticmethod
    def _type_symbols(variable_type, world_objects: dict):
        # if variable type is found in the world objects,
        # return list of object names, such as robr, robq
        return (k for k, v in world_objects.items() if v == variable_type)

    def _instantiate(self, variables, world_objects: dict):
        variable_ground_space = []
        for variable_name, variable_type in variables:
            c = []
            for symbol in self._type_symbols(variable_type, world_objects):
                c.append((variable_name, symbol))
            variable_ground_space.append(c)
        return itertools.product(*variable_ground_space)

    def _get_ground_operators(self) -> List[Operator]:
        ground_operators = []
        for operator in self._domain_problem.operators():
            op = self._domain_problem.domain.operators[operator]
            for ground in self._instantiate(op.variable_list.items(),
                                            self._domain_problem.
                                            worldobjects()):
                st = dict(ground)
                gop = Operator(operator)
                gop.variable_list = st
                gop.precondition_pos = set(
                    [a.ground(st) for a in op.precondition_pos])
                gop.precondition_neg = set(
                    [a.ground(st) for a in op.precondition_neg])
                gop.effect_pos = set([a.ground(st) for a in op.effect_pos])
                gop.effect_neg = set([a.ground(st) for a in op.effect_neg])
                ground_operators.append(gop)
        return ground_operators

    @staticmethod
    def _to_set_of_tuples(state: Set[Atom]) -> Set[Tuple]:
        set_of_tuples = set()
        for atom in state:
            tup = tuple(atom.predicate)
            set_of_tuples.add(tup)
        return set_of_tuples

    @property
    def initial_state(self):
        return self._initial_state

    @property
    def goal_state(self):
        return self._goal_state

    @property
    def actions(self):
        return self._actions
