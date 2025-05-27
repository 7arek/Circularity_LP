import math

import gurobipy as gp
from gurobipy import GRB
import networkx as nx

from mip_contiguity import find_fischetti_separator

"""
Code based on "Political districting to optimize the Polsby-Popper compactness score with application to  voting
rights"
"""


def build_single_district_mip(DG : nx.DiGraph, root: int | None = None):
    """
    Builds a MISOCP model for a single district in a directed graph DG, with the goal of maximizing the Polsby-Popper score.
    :param DG: Directed graph representing the districting problem, where nodes have 'node_weight' and 'boundary_perim' attributes,
                and edges have 'shared_perim' attribute.
    :param root: Optional root node for the district, used to ensure contiguity. If None, no specific root is enforced.
    :return: A Gurobi model object representing the districting problem.
    """

    ##################################
    # CREATE MODEL AND MAIN VARIABLES
    ##################################

    m = gp.Model()

    # x[i] equals one when node i is selected in the district
    m._x = m.addVars(DG.nodes, name='x', vtype=GRB.BINARY)

    # y[u,v] equals one when arc (u,v) is cut because u (but not v) is selected in the district
    m._y = m.addVars(DG.edges, name='y', vtype=GRB.BINARY)

    ###########################
    # ADD MAIN CONSTRAINTS
    ###########################

    # add constraints saying that edge {u,v} is cut if u (but not v) is selected in the district
    m.addConstrs(m._x[u] - m._x[v] <= m._y[u, v] for u, v in DG.edges)

    ###########################
    # ADD OBJECTIVE
    ###########################

    # z is inverse Polsby-Popper score for the district
    m._z = m.addVar(name='z')

    # objective is to minimize the inverse Polsby-Popper score
    m.setObjective(m._z, GRB.MINIMIZE)

    ###################################
    # ADD POLSBY-POPPER CONSTRAINTS
    ###################################

    # A = area of the district
    m._A = m.addVar(name='A')

    # P = perimeter of the district
    m._P = m.addVar(name='P')

    # add SOCP constraint relating inverse Polsby-Popper score z to area and perimeter
    m.addConstr(m._P * m._P <= 4 * math.pi * m._A * m._z)

    # add constraint on area A
    m.addConstr(m._A == gp.quicksum(DG.nodes[i]['node_weight'] * m._x[i] for i in DG.nodes))

    # add constraint on perimeter P
    m.addConstr(m._P == gp.quicksum(DG.edges[u, v]['shared_perim'] * m._y[u, v] for u, v in DG.edges)
                + gp.quicksum(
        DG.nodes[i]['boundary_perim'] * m._x[i] for i in DG.nodes if DG.nodes[i]['boundary_node']))

    m.update()

    ###################################
    # ADD DISTRICT SIZE CONSTRAINT
    ###################################

    m.addConstr(gp.quicksum(m._x[i] for i in DG.nodes) >= 1)

    ###################################
    # ADD CONTIGUITY CONSTRAINTS
    ###################################

    m._callback = None
    m._numCallbacks = 0
    m._numLazyCuts = 0

    m.Params.LazyConstraints = 1
    m._DG = DG
    m._root = root # TODO i dont know if its okay that we use root=None
    m._callback = cut_callback

    ###################################
    # SOLVE PARAMETERS
    ###################################

    m.Params.MIPGap = 0.00
    m.Params.FeasibilityTol = 1e-7
    m.Params.IntFeasTol = 1e-7
    m.update()

    return m


def cut_callback(m, where):
    """
    Callback function to add lazy cuts for the single district MISOCP model.
    This function is triggered internally during the MIP solution process to enforce contiguity constraints.

    :param m: Gurobi model object representing the districting problem.
    :param where: Callback trigger point, indicating the type of callback event.
    :return: None
    """


    if where == GRB.Callback.MIPSOL:
        m._numCallbacks += 1
        DG = m._DG
        xval = m.cbGetSolution(m._x)

        ##########################################
        # ADD CUT FOR COMPLEMENT
        ##########################################

        # vertices assigned to this district
        S = [v for v in DG.nodes if xval[v] > 0.5]

        # what shall we deem as the "root" of this district? call it b
        b = m._root  # possibly None

        # for each component that doesn't contain b, add a cut
        for component in sorted(nx.strongly_connected_components(DG.subgraph(S)), key=len, reverse=True):

            # what is the maximum population node in this component?
            maxp = max(DG.nodes[v]['node_weight'] for v in component)
            mpv = [v for v in component if DG.nodes[v]['node_weight'] == maxp][0]

            # if no root 'b' has been selected yet, pick one
            if b is None:
                # find some vertex "b" that has largest population in this component
                b = mpv

            if b in component:
                continue

            # find some vertex "a" that has largest population in this component
            a = mpv

            # get minimal a,b-separator
            C = find_fischetti_separator(DG, component, b)

            # add lazy cut
            m.cbLazy(m._x[a] + m._x[b] <= 1 + gp.quicksum(m._x[c] for c in C))
            m._numLazyCuts += 1

    return



