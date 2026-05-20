from builtins import range, set
import re
import random
from collections import deque

actions           = ["U", "D", "L", "R"]
goal      = [[1, 2, 3], [4, 0, 5], [6, 7, 8]]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def to_tuple(state):
    tuple_state = []
    for row in state:
        tuple_state.append(tuple(row))
    return tuple(tuple_state)


def move(state, action):
    r, c = find_zero(state)
    ns = [row[:] for row in state]
    if   action == "U" and r > 0: ns[r][c], ns[r-1][c] = ns[r-1][c], ns[r][c]
    elif action == "D" and r < 2: ns[r][c], ns[r+1][c] = ns[r+1][c], ns[r][c]
    elif action == "L" and c > 0: ns[r][c], ns[r][c-1] = ns[r][c-1], ns[r][c]
    elif action == "R" and c < 2: ns[r][c], ns[r][c+1] = ns[r][c+1], ns[r][c]
    return ns


def _count_inversions(state):
    flat = [x for row in state for x in row if x != 0]
    return sum(flat[i] > flat[j]
               for i in range(len(flat))
               for j in range(i + 1, len(flat)))


def is_solvable(initial_state, goal_state=None):
    if goal_state is None:
        goal_state = goal
    return _count_inversions(initial_state) % 2 == _count_inversions(goal_state) % 2


def parse_state(text):
    nums = list(map(int, re.findall(r'\d+', text)))
    if len(nums) != 9:
        raise ValueError(f"Cần đúng 9 số, nhận được {len(nums)}")
    if sorted(nums) != list(range(9)):
        raise ValueError("Cần đủ các số từ 0 đến 8, không trùng lặp")
    return [nums[i*3:(i+1)*3] for i in range(3)]


def random_state(goal_state=None):
    if goal_state is None:
        goal_state = goal
    nums = list(range(9))
    while True:
        random.shuffle(nums)
        state = [nums[i*3:(i+1)*3] for i in range(3)]
        if is_solvable(state, goal_state) and state != goal_state:
            return state

class Node:

    def __init__(self, state, parent=None, cost=0, action=""):
        self.state  = state
        self.parent = parent
        self.cost   = cost
        self.action = action

def bfs(initial_state, goal_state=None):
    if goal_state is None:
        goal_state = goal
    
    root = Node(initial_state)

    if root.state == goal_state:
        return root

    frontier = deque([root])
    explored = set()
    frontier_states = {to_tuple(initial_state)}

    while frontier:
        node = frontier.popleft()
        node_tuple = to_tuple(node.state)
        frontier_states.discard(node_tuple) # Lưu lại các giá trị đang có trong frontier để tránh thêm trùng lặp
        explored.add(node_tuple)

        for action in actions:
            child_state = move(node.state, action)
            child_tuple = to_tuple(child_state)
            if child_tuple not in explored and child_tuple not in frontier_states:
                child = Node(child_state, node, node.cost + 1, action)
                if child_state == goal_state:
                    return child
                frontier.append(child)
                frontier_states.add(child_tuple)

    return None

def dfs(initial_state, goal_state=None):
    if goal_state is None:
        goal_state = goal

    root = Node(initial_state)

    if root.state == goal_state:
        return root

    frontier = [root]
    frontier_states = {to_tuple(initial_state)}
    explored = set()

    while frontier:
        node = frontier.pop()
        node_tuple = to_tuple(node.state)
        frontier_states.discard(node_tuple)
        explored.add(node_tuple)
        
        for action in actions:
            child_state = move(node.state, action)

            if child_state == node.state:
                continue  # Không tạo node con nếu trạng thái không thay đổi

            child = to_tuple(child_state)
            if child not in explored and child not in frontier_states:
                child_node = Node(child_state, node, node.cost + 1, action)
                if child_state == goal_state:
                    return child_node
                frontier.append(child_node)
                frontier_states.add(child)
    return None
# Dùng cho IDS
def ids(initial_state,goal_state=None):
    CUTOFF = "cutoff"
    if goal_state is None:
        goal_state = goal
    t = 0
    while True:
        result = depth_limited_search(initial_state, goal_state, limit=t)
        if result != CUTOFF:
            return result
        t += 1

def depth_limited_search(initial_state, goal_state=None, limit=0):
    if goal_state is None:
        goal_state = goal
    
    found_cutoff = False
    root = Node(initial_state)
    if root.state == goal_state:
        return root
    frontier = [root]

    while frontier:
        node = frontier.pop()
        if node.state == goal_state:
            return node
        if node.cost >= limit:
            found_cutoff = True
            continue
        if is_cycle(node):
            continue
        for action in actions:
            child_state = move(node.state, action)
            child_node = Node(child_state, node, node.cost + 1, action)
            if child_node.state == goal_state:
                return child_node
            frontier.append(child_node)

    return "cutoff" if found_cutoff else None

def is_cycle(node):
    current = node.parent
    while current:
        if current.state == node.state:
            return True
        current = current.parent
    return False

def get_path(node):
    path = []
    while node.parent is not None:
        path.append((node.action, node.state))
        node = node.parent
    path.append(("Start", node.state))
    path.reverse()
    return path