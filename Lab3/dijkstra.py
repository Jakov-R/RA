import math
import sys

import networkx as nx
import matplotlib.pyplot as plt

plt.rcParams["font.size"] = 15

unvisited = []
path = []
dict = {}

start_node = int(sys.argv[1])
end_node = int(sys.argv[2])
sleep_time = int(sys.argv[3])


def find_smallest_cost(G, unvisited):
    #print('Dobio sam:', unvisited)
    node_id = -1
    min_cost = math.inf
    for node in G.nodes:
        if (node not in unvisited):
            continue
        cost = G.nodes[node]['value']
        #print('Node %d has cost %.0f' % (node, cost))
        if (cost < min_cost):
            min_cost = cost
            node_id = node
    return node_id

def update(G, anchor_id, node_id):
    global dict
    global start_node
    plt.clf()

    #update the given node
    GG = G.copy()
    #color to red
    GG.nodes[anchor_id]['color'] = 'lightcoral'
    GG.nodes[node_id]['color'] = 'red'
    GG.edges[(anchor_id, node_id)]['color'] = 'red'
    GG.edges[(anchor_id, node_id)]['width'] = 5
    #value to x
    if (node_id != start_node):
        current_cost = G.nodes[node_id]['value']
        anchor_cost = G.nodes[anchor_id]['value']
        w = G.get_edge_data(anchor_id, node_id)['weight']
        new_cost = anchor_cost + w
        #print('Current cost of %d is %.0f' % (node_id, current_cost))
        #print('%.0f + %.0f = %.0f' % (anchor_cost, w, new_cost))
        if (new_cost < current_cost):
            GG.nodes[node_id]['value'] = new_cost
            G.nodes[node_id]['value'] = new_cost
            dict[node_id] = anchor_id

    draw(GG, anchor_id)
    plt.pause(sleep_time)

def draw(G, anchor_id):
    global unvisited
    plt.rcParams["figure.figsize"] = (20, 6)

    # DRAWING THE GRAPH
    pos = nx.get_node_attributes(G, 'pos')
    color_map = list(nx.get_node_attributes(G, 'color').values())
    colors = list(nx.get_edge_attributes(G, 'color').values())
    weights = nx.get_edge_attributes(G, 'weight')
    widths = list(nx.get_edge_attributes(G, 'width').values())

    nx.draw(G, pos=pos, node_color=color_map, node_size=400, edge_color=colors, width=widths, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)

    for node in G.nodes:
        if (node == 'Ispis'):
            continue
        text = G.nodes[node]['value']
        x = G.nodes[node]['pos'][0] - 0.2
        y = G.nodes[node]['pos'][1] + 0.25
        if (node == 4):
            x -= 0.4
        if (node in [6, 7]):
            x += 0.4
            y -= 0.05
        plt.text(x, y, text)

    text = 'Unvisited\n'
    for v in unvisited:
        text += str(v) + '(' + str(G.nodes[v]['value']) + ') '
    text += '\n\n'
    text += 'Trenutni čvor:\n' + str(anchor_id) + '\nSusjedni čvorovi:\n'
    for v in G.neighbors(anchor_id):
        if (v not in unvisited):
            continue
        text += str(v) + ' '
    plt.text(17, 5, text)

    plt.draw()

def final_draw(G):
    plt.clf()
    plt.rcParams["figure.figsize"] = (20, 6)

    for i in range(len(path)-1):
        first = path[i]
        second = path[i+1]
        edge = (first, second)
        G.edges[edge]['color'] = 'red'
        G.edges[edge]['width'] = 5

    # DRAWING THE GRAPH
    pos = nx.get_node_attributes(G, 'pos')
    color_map = list(nx.get_node_attributes(G, 'color').values())
    colors = list(nx.get_edge_attributes(G, 'color').values())
    weights = nx.get_edge_attributes(G, 'weight')
    widths = list(nx.get_edge_attributes(G, 'width').values())

    nx.draw(G, pos=pos, node_color=color_map, node_size=400, edge_color=colors, width=widths, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)

    for node in G.nodes:
        if (node == 'Ispis'):
            continue
        text = G.nodes[node]['value']
        x = G.nodes[node]['pos'][0] - 0.2
        y = G.nodes[node]['pos'][1] + 0.25
        if (node == 4):
            x -= 0.4
        if (node in [6, 7]):
            x += 0.4
            y -= 0.05
        plt.text(x, y, text)

    text = 'Najkraći put od ' + str(start_node) + ' do ' + str(end_node) + ':\n'
    for v in path:
        text += str(v) + ' '

    plt.text(20, 7, text)

    plt.show()

def main():
    global unvisited
    global path
    global end_node
    #init
    G = nx.Graph()

    #ADDING NODES
    G.add_node(0, pos=(0, 3), color='lavender', value=math.inf)
    G.add_node(1, pos=(4, 6), color='lavender', value=math.inf)
    G.add_node(2, pos=(8, 6), color='lavender', value=math.inf)
    G.add_node(3, pos=(12, 6), color='lavender', value=math.inf)
    G.add_node(4, pos=(8, 3), color='lavender', value=math.inf)
    G.add_node(5, pos=(16, 3), color='lavender', value=math.inf)
    G.add_node(6, pos=(4, 0), color='lavender', value=math.inf)
    G.add_node(7, pos=(8, 0), color='lavender', value=math.inf)
    G.add_node(8, pos=(12, 0), color='lavender', value=math.inf)
    G.add_node('Ispis', pos=(25, 8), color='white', value=math.inf)

    G.nodes[start_node]['color'] = 'lightblue'
    G.nodes[start_node]['value'] = 0
    G.nodes[end_node]['color'] = 'lightgreen'

    #ADDING EDGES
    G.add_edge(0, 1, weight=4, color='black', width=2)
    G.add_edge(0, 6, weight=7, color='black', width=2)
    G.add_edge(1, 2, weight=9, color='black', width=2)
    G.add_edge(1, 6, weight=11, color='black', width=2)
    G.add_edge(1, 7, weight=20, color='black', width=2)
    G.add_edge(2, 3, weight=6, color='black', width=2)
    G.add_edge(2, 4, weight=2, color='black', width=2)
    G.add_edge(3, 4, weight=10, color='black', width=2)
    G.add_edge(3, 5, weight=5, color='black', width=2)
    G.add_edge(4, 5, weight=15, color='black', width=2)
    G.add_edge(4, 7, weight=1, color='black', width=2)
    G.add_edge(4, 8, weight=5, color='black', width=2)
    G.add_edge(5, 8, weight=12, color='black', width=2)
    G.add_edge(6, 7, weight=1, color='black', width=2)
    G.add_edge(7, 8, weight=3, color='black', width=2)

    unvisited = list(G.nodes).copy()
    unvisited.remove('Ispis')

    #find the smallest cost vertex
    while (True):
        i = find_smallest_cost(G, unvisited)
        #print("Smallest cost is", i)
        unvisited.remove(i)
        for n in G.neighbors(i):
            if (n not in unvisited):
                continue
            update(G, i, n)
        if (len(unvisited) == 0):
            node = end_node
            while (node != start_node):
                path.append(node)
                node = dict[node]
            path.append(start_node)
            path = path[::-1]
            final_draw(G)
            plt.pause(math.inf)

main()