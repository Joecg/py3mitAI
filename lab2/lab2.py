# Fall 2012 6.034 Lab 2: Search
#
# Your answers for the true and false questions will be in the following form.  
# Your answers will look like one of the two below:
#ANSWER1 = True
#ANSWER1 = False

# 1: True or false - Hill Climbing search is guaranteed to find a solution
#    if there is a solution
ANSWER1 = False

# 2: True or false - Best-first search will give an optimal search result
#    (shortest path length).
#    (If you don't know what we mean by best-first search, refer to
#     http://courses.csail.mit.edu/6.034f/ai3/ch4.pdf (page 13 of the pdf).)
ANSWER2 = False

# 3: True or false - Best-first search and hill climbing make use of
#    heuristic values of nodes.
ANSWER3 = True

# 4: True or false - A* uses an extended-nodes set.
ANSWER4 = True

# 5: True or false - Breadth first search is guaranteed to return a path
#    with the shortest number of nodes.
ANSWER5 = True

# 6: True or false - The regular branch and bound uses heuristic values
#    to speed up the search for an optimal path.
ANSWER6 = False

# Import the Graph data structure from 'search.py'
# Refer to search.py for documentation
from search import Graph

## Optional Warm-up: BFS and DFS
# If you implement these, the offline tester will test them.
# If you don't, it won't.
# The online tester will not test them.

def bfs(graph, start, goal):
    if start == goal: return [start]
    queue = [[start]]
    while len(queue) != 0:
        considered_path = queue[0]
        queue = queue[1:]
        if considered_path[-1] == goal: return considered_path
        connected_nodes = graph.get_connected_nodes(considered_path[-1])
        queue_addition = [considered_path + [connected_node]
                          for connected_node in connected_nodes
                          if not connected_node in considered_path]
        queue = queue + queue_addition
    return []

## Once you have completed the breadth-first search,
## this part should be very simple to complete.
def dfs(graph, start, goal):
    if start == goal: return [start]
    stack = [[start]]
    while len(stack) != 0:
        considered_path = stack[0]
        stack = stack[1:]
        if considered_path[-1] == goal: return considered_path
        connected_nodes = graph.get_connected_nodes(considered_path[-1])
        stack_addition = [considered_path + [connected_node]
                          for connected_node in connected_nodes
                          if not connected_node in considered_path]
        stack = stack_addition + stack
    return []

## Now we're going to add some heuristics into the search.  
## Remember that hill-climbing is a modified version of depth-first search.
## Search direction should be towards lower heuristic values to the goal.
def hill_climbing(graph, start, goal):
    if start == goal: return [start]
    stack = [[start]]
    while len(stack) != 0:
        considered_path = stack[0]
        stack = stack[1:]
        if considered_path[-1] == goal: return considered_path
        connected_nodes = graph.get_connected_nodes(considered_path[-1])
        stack_addition = [considered_path + [connected_node]
                          for connected_node in connected_nodes
                          if not connected_node in considered_path]
        stack = sorted(stack_addition,
                       key = lambda x: graph.get_heuristic(x[-1], goal),
                       reverse = False) + stack
    return []

## Now we're going to implement beam search, a variation on BFS
## that caps the amount of memory used to store paths.  Remember,
## we maintain only k candidate paths of length n in our agenda at any time.
## The k top candidates are to be determined using the 
## graph get_heuristic function, with lower values being better values.
def beam_search(graph, start, goal, beam_width):
    if start == goal: return [start]
    queue = [[start]]
    while len(queue) != 0:
        extending_length = len(queue[0])
        extending_paths = [path for path in queue
                           if len(path) == extending_length]
        queue = queue[len(extending_paths):]
        queue_add_candidates = []
        for path in extending_paths:
            if path[-1] == goal: return path
            next_nodes = [node for node in
                          graph.get_connected_nodes(path[-1])
                          if not node in path]
            queue_add_candidates = (queue_add_candidates +
                                    [path + [node]
                                     for node in next_nodes])
        sort_candidates = sorted(queue_add_candidates,
                                 key = lambda x:graph.get_heuristic(x[-1],
                                                                    goal),
                                 reverse = False)
        q_add = sort_candidates[:beam_width]
        queue = q_add + queue
    return []

## Now we're going to try optimal search.  The previous searches haven't
## used edge distances in the calculation.

## This function takes in a graph and a list of node names, and returns
## the sum of edge lengths along the path -- the total distance in the path.
def path_length(graph, node_names):
    if len(node_names) == 1: return 0
    if not graph.is_valid_path(node_names):
        raise ValueError('Argument path not continuous.')
    total_length = 0
    prev_node = node_names[0]
    for node in node_names[1:]:
        edge_len = graph.get_edge(prev_node, node).length
        total_length += edge_len
        prev_node = node
    return total_length

def branch_and_bound(graph, start, goal):
    if start == goal: return [start]
    agenda = [[start]]
    while len(agenda) != 0:
        considered_path = agenda[0]
        agenda = agenda[1:]
        if considered_path[-1] == goal: return considered_path
        connected_nodes = graph.get_connected_nodes(considered_path[-1])
        agenda_addition = [considered_path + [connected_node]
                           for connected_node in connected_nodes
                           if not connected_node in considered_path]
        agenda = sorted(agenda_addition + agenda,
                        key = lambda x: path_length(graph, x),
                        reverse = False)
    return []

def a_star(graph, start, goal):
    if start == goal: return [start]
    agenda = [[start]]
    extended_set = set()
    while len(agenda) != 0:
        considered_path = agenda[0]
        extended_set.add(considered_path[-1])
        agenda = agenda[1:]
        if considered_path[-1] == goal: return considered_path
        connected_nodes = graph.get_connected_nodes(considered_path[-1])
        agenda_addition = [considered_path + [connected_node]
                           for connected_node in connected_nodes
                           if ((not connected_node in considered_path)
                               and (not connected_node in extended_set))]
        agenda = sorted(agenda_addition + agenda,
                        key = lambda x: (path_length(graph, x) +
                                         graph.get_heuristic(x[-1], goal)),
                        reverse = False)
    return []

## It's useful to determine if a graph has a consistent and admissible
## heuristic.  You've seen graphs with heuristics that are
## admissible, but not consistent.  Have you seen any graphs that are
## consistent, but not admissible?

def is_admissible(graph, goal):
    for node in graph.nodes:
        heuristic = graph.get_heuristic(node, goal)
        distance = path_length(graph, a_star(graph, node, goal))
        if heuristic > distance: return False
    return True

def is_consistent(graph, goal):
    pairs = [(n1, n2) for n1 in graph.nodes for n2 in graph.nodes]
    checked_pairs = []
    for pair in pairs:
        if set(pair) in checked_pairs: continue
        checked_pairs.append(set(pair))
        h1 = graph.get_heuristic(pair[0], goal)
        h2 = graph.get_heuristic(pair[1], goal)
        distance = path_length(graph, branch_and_bound(graph,
                                                       pair[0],
                                                       pair[1]))
        if abs(h1 - h2) > distance: return False
    return True

HOW_MANY_HOURS_THIS_PSET_TOOK = ' '
WHAT_I_FOUND_INTERESTING = ' '
WHAT_I_FOUND_BORING = ' '
