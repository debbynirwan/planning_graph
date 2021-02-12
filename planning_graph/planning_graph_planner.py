"""Planning Graph Planner

Description:
    The planner - search algorithm to find solution plan in Planning Graph.

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
from .planning_graph import Graph, LayeredPlan, Plan, PlanningGraph
from typing import Optional


class GraphPlanner(object):

    def __init__(self):
        self._layered_plan: LayeredPlan = LayeredPlan()
        self._mutex = {}

    def plan(self, gr: Graph, g: set):
        index = gr.num_of_levels - 1

        if not g.issubset(gr.prop[index]):
            return None

        plan = self._extract(gr, g, index)
        if plan:
            return self._layered_plan

        if gr.fixed_point:
            n = 0
            try:
                props_mutex = self._mutex[gr.num_of_levels - 1]
            except KeyError:
                props_mutex = None
            if props_mutex:
                n = len(props_mutex)
        else:
            n = 0

        while True:
            index += 1
            gr = PlanningGraph.expand(gr)
            plan = self._extract(gr, g, index)
            if plan:
                return self._layered_plan
            elif gr.fixed_point:
                try:
                    props_mutex = self._mutex[gr.num_of_levels-1]
                except KeyError:
                    props_mutex = None
                if props_mutex:
                    if n == len(props_mutex):
                        # this means that it has stabilised
                        return None
                    else:
                        n = len(props_mutex)

    def _extract(self, gr: Graph, g: set, index: int) -> Optional[Plan]:
        if index == 0:
            return Plan()
        return self._search(gr, g, Plan(), index)

    def _search(self, gr: Graph, g: set, plan: Plan, index: int):
        if g == set():
            new_goals = set()
            for action in plan.plan:
                for proposition in action.precondition_pos:
                    if 'adjacent' not in proposition:
                        new_goals.add(proposition)

            extracted_plan = self._extract(gr, new_goals, index-1)
            if extracted_plan is None:
                return None
            else:
                self._layered_plan[index-1] = extracted_plan
                self._layered_plan[index] = plan
                return plan
        else:
            # select any p in g
            proposition = g.pop()

            # compute resolvers
            resolvers = []
            for action in gr.act[index]:
                if proposition in action.effect_pos:
                    if plan.plan:
                        mutex = False
                        for action2 in plan.plan:
                            if (action, action2) in \
                                    gr.act_mutexes[index]:
                                mutex = True
                                break
                        if not mutex:
                            resolvers.append(action)
                    else:
                        resolvers.append(action)

            # no resolvers
            if not resolvers:
                return None

            # choose non-deterministically and backtrack if failed
            while resolvers:
                resolver = resolvers.pop()
                plan.append(resolver)
                plan_result = self._search(gr, g - resolver.effect_pos,
                                           plan, index)
                if plan_result is not None:
                    return plan_result
                else:
                    plan.remove(resolver)
                    g.add(proposition)
            return None
