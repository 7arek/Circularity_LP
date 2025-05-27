def find_fischetti_separator(DG, component, b):
    """
    From Fischetti, et al. (2017).
    Code from "Political districting to optimize the Polsby-Popper compactness score with application to voting rights"
    """

    neighbors_component = {i: False for i in DG.nodes}
    for i in nx.node_boundary(DG, component, None):
        neighbors_component[i] = True

    visited = {i: False for i in DG.nodes}
    child = [b]
    visited[b] = True

    while child:
        parent = child
        child = []
        for i in parent:
            if not neighbors_component[i]:
                for j in DG.neighbors(i):
                    if not visited[j]:
                        child.append(j)
                        visited[j] = True

    C = [i for i in DG.nodes if neighbors_component[i] and visited[i]]
    return C