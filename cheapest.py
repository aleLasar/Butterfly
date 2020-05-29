import math
import os
import sys
from threading import Timer
import time

PI = 3.141592
RRR = 6378.388


class Node():

    def __init__(self, name, latitude, longitude):
        self._name = name
        self._visited = False
        self._latitude = latitude
        self._longitude = longitude

    def __gt__(self, other):
        return self._name > other._name

    def __lt__(self, other):
        return self._name < other._name

    def __le__(self, other):
        return self._name <= other._name

    def __ge__(self, other):
        return self._name >= other._name

    def __eq__(self, other):
        return self._name == other._name

    def __ne__(self, other):
        return self._name != other._name

    def __repr__(self):
        return str(self._name+1)

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def visited(self):
        return self._visited

    def set_visited(self, visited):
        self._visited = visited

    def latitude(self):
        return self._latitude

    def latitude_rad(self):
        deg = int(self._latitude)
        rounded = self._latitude - deg
        return PI * (deg + 5.0 * (rounded / 3.0)) / 180.0

    def set_latitude(self, latitude):
        self._latitude = latitude

    def longitude(self):
        return self._longitude

    def longitude_rad(self):
        deg = int(self._longitude)
        rounded = self._longitude - deg
        return PI * (deg + 5.0 * (rounded / 3.0)) / 180.0

    def set_longitude(self, longitude):
        self._longitude = longitude


class Edge():

    def __init__(self, src, dest, weight):
        self._nodes = src, dest
        self._weight = weight
        self._label = None

    def __gt__(self, other):
        return self._weight > other._weight

    def __lt__(self, other):
        return self._weight < other._weight

    def __le__(self, other):
        return self._weight <= other._weight

    def __ge__(self, other):
        return self._weight >= other._weight

    def __eq__(self, other):
        return self._weight == other._weight

    def __ne__(self, other):
        if other == None:
            return True
        else:
            return self._weight != other._weight

    def __str__(self):
        return self._weight

    def weight(self):
        return self._weight

    def nodes(self):
        return self._nodes

    def label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def opposite(self, node):
        if node == self._nodes[0]:
            return self._nodes[1]
        if node == self._nodes[1]:
            return self._nodes[0]
        return None


# %%
class UnionFind():

    def __init__(self, n):
        self._parents = [None] * n
        for i in range(0, n):
            self._parents[i] = i

    def find(self, x, depth=0):
        if (x != self._parents[x]):
            return self.find(self._parents[x], depth+1)
        return x, depth

    def union(self, x, y):
        set_x, depth_x = self.find(x)
        set_y, depth_y = self.find(y)
        if(set_x == set_y):
            return
        if(depth_x > depth_y):
            self._parents[set_y] = set_x
        else:
            self._parents[set_x] = set_y

# %%


class Graph():

    def __init__(self, n):
        self._matrix = [[None] * n] * n
        self._nodes = [None] * n

    def add_node(self, name, latitude, longitude):
        if not self.is_node_present(name):
            node = Node(name, latitude, longitude)
            self._nodes[name] = node
            return node
        else:
            return self._nodes[name]

    def add_edge(self, src, dest, weight):
        edge = Edge(src, dest, weight)
        self._matrix[src.name()][dest.name()] = edge
        self._matrix[dest.name()][src.name()] = edge

    def matrix(self):
        return self._matrix

    def nodes(self):
        return self._nodes

    def is_node_present(self, name):
        if self._nodes[name] is None:
            return False
        else:
            return True

    def num_vertici(self):
        return len(self._nodes)

    def remove_edge(self, edge):
        self._matrix[edge.nodes()[0].name()][edge.nodes()[1].name()] = None
        self._matrix[edge.nodes()[1].name()][edge.nodes()[0].name()] = None

    def geo_distance(self, src, dest):
        q1 = math.cos(src.longitude_rad() - dest.longitude_rad())
        q2 = math.cos(src.latitude_rad() - dest.latitude_rad())
        q3 = math.cos(src.latitude_rad() + dest.latitude_rad())
        return int(RRR * math.acos(0.5*((1.0+q1)*q2 - (1.0-q1)*q3)) + 1.0)

    def euclide_distance(self, src, dest):
        x = abs(src.latitude() - dest.latitude())
        y = abs(src.longitude() - dest.longitude())
        return int(math.sqrt(math.pow(x, 2)+math.pow(y, 2)))


def cheapest_insertion(G: Graph):
    visited_edge = {}
    matrix = G.matrix()
    nodes = list(G.nodes())
    edges_sol = list()
    weight_sol = 0
    zero_n = nodes.pop(0)
    local_min = float("inf")
    local_edge = [None]*3
    local_node = None

    for opposite, edge in enumerate(matrix[zero_n.name()]):        
        if edge.weight() < local_min:
            local_min = edge.weight()
            local_node = nodes[opposite]
            local_edge[0] = edge

    nodes.remove(local_node)
    weight_sol += local_min * 2
    edges_sol.append(local_edge[0])

    while len(nodes) != 0:
        local_min = float("inf")
        local_edge = [None]*3
        local_node = None

        for k in range(len(nodes)):
            for idx, val in enumerate(edges_sol):
                ik, jk, ij = [None]*3
                if (nodes[k].name(), val.nodes()[0].name()) in visited_edge:
                    ik = visited_edge[(nodes[k].name(), val.nodes()[0].name())]
                else:
                    ik = matrix[nodes[k].name()][val.nodes()[0].name()]

                if ((nodes[k].name(), val.nodes()[1].name())) in visited_edge:
                    jk = visited_edge[(nodes[k].name(), val.nodes()[1].name())]
                else:
                    jk = matrix[nodes[k].name()][val.nodes()[1].name()]

                ij = val

                if ik != None and jk != None and ij != None:
                    to_minimized = ik.weight() + jk.weight() - ij.weight()
                    if to_minimized < local_min:
                        local_min = to_minimized
                        local_node = nodes[k]
                        local_edge = ik, jk, val

        nodes.remove(local_node)
        weight_sol += local_edge[0].weight() + \
            local_edge[1].weight() - local_edge[2].weight()
        edges_sol.append(local_edge[0])
        edges_sol.append(local_edge[1])
        edges_sol.remove(local_edge[2])

    return weight_sol


def read_file(filename):
    file = open(filename, "r")
    type = ""
    vertici = 0

    while True:
        line = file.readline()
        line = line.replace(" :", ":")
        if "NODE_COORD_SECTION" in line:
            break
        label, value = list(line.split(maxsplit=1))
        if "EDGE_WEIGHT_TYPE" in label:
            type = value
        if "DIMENSION" in label:
            vertici = int(value)

    graph = Graph(vertici)

    for line in file:
        if "EOF" in line:
            break
        if "GEO" in type:
            tripla = list(map(float, line.split()))
        else:
            tripla = list(map(int, map(round, map(float, line.split()))))
        graph.add_node(int(tripla[0])-1, tripla[1], tripla[2])
    nodes = graph.nodes()
    for index_src in range(len(nodes)):
        for index_dest in range(index_src+1, len(nodes)):
            src = nodes[index_src]
            dest = nodes[index_dest]
            if "GEO" in type:
                graph.add_edge(src, dest, graph.geo_distance(src, dest))
            else:
                graph.add_edge(src, dest, graph.euclide_distance(src, dest))
    file.close()
    return graph


def errore(soluzione, ottimo):
    return str((soluzione-ottimo)/ottimo)


def main(folder):
    ottimi_file = open(folder+"/"+"ottimi.txt", "r")
    ottimi = {}
    for line in ottimi_file:
        graph, ottimo = list(line.split(":"))
        ottimi[graph] = int(ottimo)
    ottimi_file.close()
    with os.scandir(folder) as it:
        for i, entry in enumerate(it):
            if "berlin52.tsp" in entry.name:
                ottimo = ottimi[entry.name]
                graph = read_file(folder+"/"+entry.name)
                start = time.time()
                dist = cheapest_insertion(graph)
                time_exec = time.time() - start
                test = entry.name.replace(".tsp", ".out")
                result = open(folder+"/"+test, "a")
                result.write("\nCheapest_Insertion - soluzione: " +
                             str(dist)+" tempo: "+str(time_exec) + " errore: "+errore(dist, ottimo)+" %")
                result.close()


if __name__ == "__main__":
    sys.setrecursionlimit(999999999)
    #main("tsp_dataset", int(sys.argv[0]))
    main("tsp_dataset")
