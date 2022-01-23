class Graph:
    def __init__(self) -> None:
        self.nodes = {}

    def add_node(self, n, neighbors, capacity):
        new_node = False
        if n not in self.nodes:
            self.nodes[n] = Node(n, neighbors, capacity)
            new_node = True

        for n_i in range(len(neighbors)):
            neighbor = neighbors[n_i]
            neighbor_c = capacity[n_i]

            # Neighbor is a new node
            if neighbors[n_i] not in self.nodes.keys():
                self.nodes[neighbor] = Node(neighbor, [n], [neighbor_c])

            # Neighbor was already intialized- only need to add the edge between them
            if not new_node and neighbors[n_i] not in self.nodes[n].neighbors:
                self.nodes[n].add_neighbor(neighbor, neighbor_c)
                self.nodes[neighbor].add_neighbor(n, neighbor_c)

    def mincut_maxflow(self):
        """
        Linked List implementation of the Edmonds-Karp algorithm
        Solves the MinCut-MaxFlow algorithm
        """

        while self.bfs():
            df = float('inf')
            # Find the bottleneck
            for n in range(len(self.path[:-1])):
                from_node = self.path[n]
                to_node = self.path[n+1]
                edge = self.nodes[to_node].edges[from_node]

                df = min(df, edge.c-edge.flow)

            # Augmentation Stage - Add the flow along the new path
            for n in range(len(self.path[:-1])):
                from_node = self.path[n]
                to_node = self.path[n+1]

                self.nodes[to_node].edges[from_node].flow += df
                self.nodes[from_node].edges[to_node].flow += df

    def bfs(self):
        """
        Breadth-First Search
        Returns true if there is a path from t->s
        """
        queue = [1]
        self.nodes[1].visited = True

        while queue:
            node = self.nodes[queue.pop(0)]

            for n_i in node.neighbors:
                n = self.nodes[n_i]
                if not n.visited:
                    edge = node.edges[n_i]
                    if edge.c > edge.flow:
                        n.visited = True
                        n.parent = node.val
                        if n.val == 0:
                            return self.finish_search(True)
                        else:
                            queue.append(n_i)

        return self.finish_search(False)

    def finish_search(self, found_path):
        """
        If the BFS found a path, retrace it
        Reset all the "visited" flags
        """
        if found_path:
            self.path = [0]
            node = self.nodes[0]

            while node.val != 1:
                parent = node.parent
                self.path.append(parent)
                node = self.nodes[parent]
        else:
            self.path = []

        for node in self.nodes.keys():
            self.nodes[node].visited = False
            self.nodes[node].parent = None
        return found_path

class Node:
    def __init__(self, val_, neighbors_, c_) -> None:
        self.val = val_
        self.neighbors = neighbors_
        self.edges = {}

        for n in range(len(neighbors_)):
            e = Edge(c_[n], 0)
            self.edges[neighbors_[n]] = e
            
        self.parent = None
        self.visited = False

    def add_neighbor(self, n, c):
        if n != self.val:
            e = Edge(c, 0)
            self.edges[n] = e
            self.neighbors.append(n)

    def calc_flow(self):
        f = 0
        for e in self.edges.values():
            f += e.flow
        return f

    def __repr__(self) -> str:
        return '(Node) val:%d, flow:%.2f'%(self.val, self.calc_flow())

class Edge:
    def __init__(self, c_, flow_) -> None:
        self.c = c_
        self.flow = flow_

    def __repr__(self) -> str:
        return '(Edge) c:%.2f, flow:%.2f'%(self.c, self.flow)

if __name__ == "__main__":

    # Simple MinCut-MaxFlow example
    g = Graph()

    g.add_node(0, [2, 5], [8, 3])
    g.add_node(1, [3, 4], [2, 5])
    g.add_node(2, [0, 3], [8, 9])
    g.add_node(3, [1, 2, 5], [2, 9, 7])
    g.add_node(4, [1, 5], [5, 4])
    g.add_node(5, [0, 3, 4], [3, 7, 4])

    g.mincut_maxflow()

    print('1')