############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 1 Starter Code
## v1.1
##
## Changes: 
## v1.1: removed the hfn paramete from dfs. Updated solve_puzzle() accordingly.
############################################################

from typing import List
import heapq
from heapq import heappush, heappop
import time
import argparse
import math # for infinity

#from optional import Optional

from board import *

def is_goal(state):
    """
    Returns True if the state is the goal state and False otherwise.

    :param state: the current state.
    :type state: State
    :return: True or False
    :rtype: bool
    """
    # if we are at goal state, then all storage points in the Board of the state
    # are filled with the boxes
    if sorted(state.board.boxes) == sorted(state.board.storage):
        return True
    return False


def get_path(state):
    """
    Return a list of states containing the nodes on the path 
    from the initial state to the given state in order.

    :param state: The current state.
    :type state: State
    :return: The path.
    :rtype: List[State]
    """
    path = []
    state_to_add = state
    while True:
        path.append(state_to_add)
        state_to_add = state_to_add.parent
        if state_to_add is None:
            break
    if path is not None:
        path.reverse()
    
    return path

def check_valid(loc, state, dir):
    '''
    Returns 1 if loc is empty
    Returns 2 if loc has a box but can be moved
    Returns -1 if there is an obstacle/box that cannot be moved
    '''
    if loc in state.board.obstacles:
        return -1
    if loc in state.board.robots:
        return -1
    if loc in state.board.boxes:
        # check location in dir to see if there is wall or another box
        new_loc = []
        if dir is 'up':
            new_loc = [loc[0], loc[1]-1]
        elif dir is 'down':
            new_loc = [loc[0], loc[1]+1]
        elif dir is 'left':
            new_loc = [loc[0]-1, loc[1]]
        elif dir is 'right':
            new_loc = [loc[0]+1, loc[1]]
        new_loc_tup = (new_loc[0], new_loc[1])
        if new_loc_tup in state.board.obstacles:
            return -1
        elif new_loc_tup in state.board.boxes:
            return -1
        elif new_loc_tup in state.board.robots:
            return -1
        else:
            return 2
    
    return 1

def get_successors(state):
    """
    Return a list containing the successor states of the given state.
    The states in the list may be in any arbitrary order.

    :param state: The current state.
    :type state: State
    :return: The list of successor states.
    :rtype: List[State]
    """

    # any robot can move up, down, left, right
    
    successors = []
    fixed_state = state
    dirs = ['up', 'down', 'left', 'right']
    for i in range(len(fixed_state.board.robots)):
        robot = state.board.robots[i]
        for dir in dirs:

            new_loc_list = []
            box_loc_list = []
            if dir is 'up':
                new_loc_list = [robot[0], robot[1]-1]
                box_loc_list = [robot[0], robot[1]-2]
            elif dir is 'down':
                new_loc_list = [robot[0], robot[1]+1]
                box_loc_list = [robot[0], robot[1]+2]
            elif dir is 'left':
                new_loc_list = [robot[0]-1, robot[1]]
                box_loc_list = [robot[0]-2, robot[1]]
            elif dir is 'right':
                new_loc_list = [robot[0]+1, robot[1]]
                box_loc_list = [robot[0]+2, robot[1]]
            new_loc = (new_loc_list[0], new_loc_list[1]) 
            box_loc = (box_loc_list[0], box_loc_list[1])
            is_valid = check_valid(new_loc, state, dir)
            
            if is_valid is 1 or is_valid is 2:
                # loc is valid, create new state and just move the robot loc
                new_board = Board(state.board.name, state.board.width, state.board.height, state.board.robots.copy(), state.board.boxes.copy(), state.board.storage.copy(), state.board.obstacles)

                # update robot location to new coords
                new_board.robots[i] = new_loc

                if is_valid is 2:
                    # need to move box according to direction
                    box_index = state.board.boxes.index(new_loc)
                    new_board.boxes[box_index] = box_loc

                successor = State(new_board, state.hfn, 0, state.depth + 1, state)
                successor.f = state.f - state.hfn(state.board) + successor.hfn(successor.board) + 1
                successors.append(successor)
    return successors


def dfs(init_board):
    """
    Run the DFS algorithm given an initial board.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial board.
    :type init_board: Board
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """
    # initialize starting state
    # get_successors(starting state)
    # append all the states to an ongoing frontier
    # get last one from it 
    # check if its goal state if so return
    # and run dfs on it

    init_state = State(init_board, heuristic_zero, 0, 0, None)
    visited = set()
    stk = [init_state]

    while len(stk) > 0:
        curr_state = stk.pop()
        curr_state_board = curr_state.board.__str__()

        if curr_state_board not in visited:
            if is_goal(curr_state):
                path = get_path(curr_state)
                return (path, len(path))
            successors = get_successors(curr_state)
            for suc in successors:
                stk.append(suc)
            visited.add(curr_state_board)
    return ([], -1)

def a_star(init_board, hfn):
    """
    Run the A_star search algorithm given an initial board and a heuristic function.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial starting board.
    :type init_board: Board
    :param hfn: The heuristic function.
    :type hfn: Heuristic (a function that consumes a Board and produces a numeric heuristic value)
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """

    init_state = State(init_board, hfn, 0, 0, None)
    visited = set()
    min_heap = []
    heappush(min_heap, (hfn(init_state.board), init_state))

    while len(min_heap) > 0:
        curr_state = heappop(min_heap)[1]
        curr_state_board = curr_state.board.__str__()

        if curr_state_board not in visited:
            if is_goal(curr_state):
                path = get_path(curr_state)
                return (path, len(path)-1)
            
            successors = get_successors(curr_state)
            for successor in successors:
                heappush(min_heap, (successor.f, successor))
            visited.add(curr_state_board)
            
    return ([], -1)

def heuristic_basic(board):
    """
    Returns the heuristic value for the given board
    based on the Manhattan Distance Heuristic function.

    Returns the sum of the Manhattan distances between each box 
    and its closest storage point.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """

    # first find the closest storage locations to each box coord, then calculate manhattan distances
    total = 0
    closest = {}

    for i in range(len(board.boxes)):
        box = board.boxes[i]
        min_dist = 2**31
        closest[str(i)] = min_dist
        for storage in board.storage:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < closest[str(i)]:
                # calculate manhattan distance and store it
                closest[str(i)] = dist
        
    for key, val in closest.items():
        total = total + val

    return total

def heuristic_advanced(board):
    """
    An advanced heuristic of your own choosing and invention.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    # first find the closest storage locations to each box coord, then calculate manhattan distances
    total = 0
    closest = {}

    for i in range (len(board.boxes)):
        box = board.boxes[i]
        min_dist = 2**31
        closest[str(i)] = min_dist
        for storage in board.storage:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < closest[str(i)]:
                # calculate manhattan distance and store it
                closest[str(i)] = dist
    
    # now add to the distances if we have walls around box
    for i in range(len(board.boxes)):
        box = board.boxes[i]
        surroundings = [(box[0], box[1]-1), (box[0], box[1]+1), (box[0]-1, box[1], box[0]+1, box[1])]
        for loc in surroundings:
            if loc in board.obstacles:
                closest[str(i)] = closest[str(i)] + 1

    for key, val in closest.items():
        total = total + val

    return total


def solve_puzzle(board: Board, algorithm: str, hfn):
    """
    Solve the given puzzle using the given type of algorithm.

    :param algorithm: the search algorithm
    :type algorithm: str
    :param hfn: The heuristic function
    :type hfn: Optional[Heuristic]

    :return: the path from the initial state to the goal state
    :rtype: List[State]
    """

    print("Initial board")
    board.display()

    time_start = time.time()

    if algorithm == 'a_star':
        print("Executing A* search")
        path, step = a_star(board, hfn)
    elif algorithm == 'dfs':
        print("Executing DFS")
        path, step = dfs(board)
    else:
        raise NotImplementedError

    time_end = time.time()
    time_elapsed = time_end - time_start

    if not path:

        print('No solution for this puzzle')
        return []

    else:

        print('Goal state found: ')
        path[-1].board.display()

        print('Solution is: ')

        counter = 0
        while counter < len(path):
            print(counter + 1)
            path[counter].board.display()
            print()
            counter += 1

        print('Solution cost: {}'.format(step))
        print('Time taken: {:.2f}s'.format(time_elapsed))

        return path


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The file that contains the solution to the puzzle."
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=['a_star', 'dfs'],
        help="The searching algorithm."
    )
    parser.add_argument(
        "--heuristic",
        type=str,
        required=False,
        default=None,
        choices=['zero', 'basic', 'advanced'],
        help="The heuristic used for any heuristic search."
    )
    args = parser.parse_args()

    # set the heuristic function
    heuristic = heuristic_zero
    if args.heuristic == 'basic':
        heuristic = heuristic_basic
    elif args.heuristic == 'advanced':
        heuristic = heuristic_advanced

    # read the boards from the file
    board = read_from_file(args.inputfile)

    # solve the puzzles
    path = solve_puzzle(board, args.algorithm, heuristic)

    # save solution in output file
    outputfile = open(args.outputfile, "w")
    counter = 1
    for state in path:
        print(counter, file=outputfile)
        print(state.board, file=outputfile)
        counter += 1
    outputfile.close()