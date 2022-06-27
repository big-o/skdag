from collections.abc import Mapping, Sequence

import networkx as nx
from skdag.dag._dag import DAG, DAGStep

__all__ = ["DAGBuilder"]


class DAGBuilder:
    def __init__(self, n_jobs=None):
        self.graph = nx.DiGraph()
        self.n_jobs = n_jobs

    def add_step(self, name, est, deps=None):
        self._validate_name(name)
        if isinstance(deps, Sequence):
            deps = {dep: None for dep in deps}

        if deps is not None:
            self._validate_deps(deps)
        else:
            deps = {}

        step = DAGStep(name, est, deps=deps)
        self.graph.add_node(name, step=step)

        for dep in deps:
            # Since node is new, edges will never form a cycle.
            self.graph.add_edge(dep, name)

        self._validate_graph()

        return self

    def _validate_name(self, name):
        if not isinstance(name, str):
            raise KeyError(f"step names must be strings, got '{type(name)}'")

        if name in self.graph.nodes:
            raise KeyError(f"step with name '{name}' already exists")

    def _validate_deps(self, deps):
        if not isinstance(deps, Mapping) or not all(
            [isinstance(dep, str) for dep in deps]
        ):
            raise ValueError(
                "deps parameter must be a map of labels to indices, "
                f"got '{type(deps)}'."
            )

        missing = [dep for dep in deps if dep not in self.graph]
        if missing:
            raise ValueError(f"unresolvable dependencies: {', '.join(sorted(missing))}")

    def _validate_graph(self):
        if not nx.algorithms.dag.is_directed_acyclic_graph(self.graph):
            raise TypeError("Workflow is not a DAG.")

    def make_dag(self):
        self._validate_graph()
        # Give the DAG a read-only view of the graph.
        return DAG(graph=self.graph.copy(as_view=True), n_jobs=self.n_jobs)

    def _repr_html_(self):
        return self.make_dag()._repr_html_()