from __future__ import annotations

import logging
import math
import random
from collections import defaultdict
from enum import Enum
from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx
from networkx import DiGraph
from logging import Logger

import os, sys
sys.path.insert(0, os.path.join(sys.path[0], sys.path[0] + '/scheduling'))

# from scheduler.solve_decoupling import solve_decoupling_milp
# from scheduler.utils.dc_checking.temporal_network import (
#     SimpleContingentTemporalConstraint, SimpleTemporalConstraint,
#     TemporalNetwork)
# from scheduler.utils.decouple_milp import NONE
# from scheduler.utils.networks import MaSTNU

from dc_checking.temporal_network import TemporalNetwork, SimpleTemporalConstraint, SimpleContingentTemporalConstraint
#  from dc_checker.dc_be import DCCheckerBE

from networks import MaSTNU
from solve_decoupling import solve_decoupling #, solve_decoupling_milp, preprocess_networks
# from decouple_milp import NONE, MIN_TIME_SPAN, MAX_FLEXIBILITY, MAX_FLEXIBILITY_NAIVE, MAX_FLEXIBILITY_NEG_CKJ, MIN_LB_TIME_SPAN, MIN_LB_UB_TIME_SPAN, MIN_BIJ

import time as Time
from time import time

"""
1. Num of difficulties: 
2. Qualities of each of level of difficulty
3. Other products from each level of difficulty (plots, graphs, etc)

======== REPORT GUIDELINES ========
The entire final report should be comprised of a 1 page summary
and a ~4 page report.
In total, your final report should include:
1. Cover page
2. Summary of motivation and problem statement. (1 page)
3. Abstract
4. Motivation
5. Problem statement
6. Background
7. Method
8. Any notable implementation details
9. Evaluation, analytical and/or empirical
10. Demonstration, including your simulation demonstration during Grand Challenge
11. Discussion, including any surprises that discovered, any major insights you gained along the way
and lessons learned
12. Conclusion

"""

def scheduleTest(p_test: TestObject = None, output_stats: bool = False) -> bool:
    """
    Shashank put a call to your MaSTNU code here
    """
    if p_test is None:
        raise Exception('p_test cannot be None')

    # draw_mastnu(p_test.netx_graph)

    ext_conts = []
    ext_reqs = []
    agent2network = {}

    for n in p_test.netx_graph.nodes():
        agent = n[1].name
        if agent not in agent2network:
            event = "{}-{}".format(agent, n[0])
            agent2network[agent] = TemporalNetwork()
            agent2network[agent].add_constraint(SimpleTemporalConstraint('z', event, lb=0, name='ref_preceding_{}'.format(agent)))
            agent2network[agent].add_event('z')
    for edge in p_test.netx_graph.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            # if edge[2]['color'] == 'b':
            #     ext_reqs.append(SimpleTemporalConstraint(**getTemporalConstraintData(edge)))
            # if edge[2]['color'] == 'k':
            #     ext_conts.append(SimpleContingentTemporalConstraint(**getTemporalConstraintData(edge)))
            ext_reqs.append(SimpleTemporalConstraint(**getTemporalConstraintData(edge)))
        else:
            agent = edge[0][1].name
            # if edge[2]['color'] == 'b':
            #     agent2network[agent].add_constraint(SimpleTemporalConstraint(**getTemporalConstraintData(edge)))
            # if edge[2]['color'] == 'k':
            #     agent2network[agent].add_constraint(SimpleContingentTemporalConstraint(**getTemporalConstraintData(edge)))
            agent2network[agent].add_constraint(SimpleContingentTemporalConstraint(**getTemporalConstraintData(edge)))

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')
    # try:
    #     # decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True)
    #     decoupling, stats = solve_decoupling(mastnu, output_stats=True)
    # except:
    #     return False
    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True)
    if decoupling is None:
        print("none found.")
        return False

    if output_stats:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    print("decoupling found.")
    # draw_mastnu(p_test.netx_graph)
    return True

def getTemporalConstraintData(e: tuple):
    return {"s": "{}-{}".format(e[0][1].name, e[0][0]),
            "e": "{}-{}".format(e[1][1].name, e[1][0]),
            "lb": e[2]['duration'][0],
            "ub": e[2]['duration'][0],
            "name": "{}{}-{}{}".format(e[0][1].name, e[0][0], e[1][1].name, e[1][0])}

class TestObject:
    locations: list[Location] = None
    netx_graph: DiGraph = None
    map_size: int = None
    succeeded: bool = None
    test_time: float = None

    def __init__(self, p_locations: list[Location] = None, p_netx_graph: DiGraph = None, p_map_size: int = None):
        if p_locations is None:
            raise Exception('p_locations cannot be None')
        if p_netx_graph is None:
            raise Exception('p_netx_graph cannot be None')
        if p_map_size is None:
            raise Exception('p_map_size cannot be None')

        self.locations = p_locations
        self.netx_graph = p_netx_graph
        self.map_size = p_map_size


class Activity:
    class ActivityType(Enum):
        TECHNICAL = 1
        RESCUE = 2
        MEDICAL = 3

    type: ActivityType = None
    duration: tuple[int, int]

    def __init__(self, p_type: ActivityType = None):
        self.type = p_type
        self.duration = self.generate_activity_duration()

    def generate_activity_duration(self):
        activity_duration: tuple[int, int] = generate_random_window(activity_times[self.type])
        return activity_duration


class Location:
    number: int = None
    activities: list[Activity] = None
    coords: tuple[int, int] = None

    # Entries are of the form:  {Location#: Distance}
    distances: dict[int, float] = None
    # Entries are of the form: {Location#: {ActivityType: Duration}}
    durations: Dict[int, Dict[Activity.ActivityType, tuple[float, float]]] = None

    def __init__(self, p_number: int, p_activities: list[Activity] = None, p_coords: tuple[int, int] = None):
        self.number = p_number
        self.activities = p_activities or []
        self.coords = p_coords
        self.distances = {}
        self.durations = defaultdict(dict)

    def fill_location_with_random_activities(self):
        """
        This method should generate a random list of activities and set that as the object's 'activities' field
        :return:
        """
        activity_types = list(Activity.ActivityType)
        num_activities = random.randint(1, len(activity_types))

        # Randomly sample the specified number of activity types without replacement
        selected_activity_types = random.sample(activity_types, num_activities)

        # Create activities with the selected activity types and assign them to the location
        self.activities = [Activity(activity_type) for activity_type in selected_activity_types]

    def calculate_distance_between_locations(self, loc2: Location) -> None:
        self.distances[loc2.number] = math.dist(self.coords, loc2.coords)

    def generate_location_duration(self, loc2: Location) -> None:
        for activity_type, speed in boat_speeds.items():
            distance = self.distances[loc2.number]
            min_speed, max_speed, step = speed
            random_speed_range = generate_random_window((int(min_speed), int(max_speed), step))
            max_duration, min_duration = (distance / random_speed_range[0]), (distance / random_speed_range[1])
            self.durations[loc2.number][activity_type] = (min_duration, max_duration)


def create_graph(locations: list[Location]):
    G = nx.DiGraph()
    intra_edge_activity_pairs = set()
    for location in locations:
        activity_count = len(location.activities)
        for idx, activity in enumerate(location.activities):

            # Set the 'type' attribute for each node based on the activity type
            node_attributes = {'activity': activity, 'type': activity.type}
            G.add_node((location.number, activity.type), **node_attributes)

            # Connect activities within the same location (intra-edges)
            if idx < activity_count - 1:
                next_activity = location.activities[idx + 1]
                activity_pair = (activity.type, next_activity.type)
                if activity_pair not in intra_edge_activity_pairs:
                    intra_edge_duration = activity.duration
                    G.add_edge((location.number, activity.type), (location.number, next_activity.type),
                               edge_type='intra', color='b', duration=intra_edge_duration)
                    intra_edge_activity_pairs.add(activity_pair)

            for other_location in locations:
                # Connect activities of the same type between locations in ascending order (inter-edges)
                if other_location.number > location.number:
                    # Finds the next activity with the same type as the current activity
                    other_activity = next((a for a in other_location.activities if a.type == activity.type), None)
                    if other_activity is not None:
                        inter_edge_duration = location.durations[other_location.number][activity.type]
                        # Add the activity duration to the inter-edge duration
                        inter_edge_duration = (inter_edge_duration[0] + activity.duration[0],
                                               inter_edge_duration[1] + activity.duration[1])
                        G.add_edge((location.number, activity.type), (other_location.number, other_activity.type),
                                   edge_type='inter', color='k', duration=inter_edge_duration)

    return G


def draw_graph(G, dim, p_num_locations: int = None, p_locations: list[Location] = None):
    ncols, nrows = dim
    fig, ax = plt.subplots()

    # Define the positions in a grid layout
    pos = {(location_number, activity_type): (coords[1] + 0.5 * (activity_type.value - 2), nrows - coords[0])
           for location_number, coords in [(loc.number, loc.coords) for loc in p_locations]
           for activity_type in Activity.ActivityType}

    node_colors = [color_map[node[1]] for node in G.nodes]

    edge_colors = nx.get_edge_attributes(G, 'color').values()
    nx.draw(G, pos, with_labels=False, node_size=500, node_color=node_colors, edge_color=edge_colors,
            font_size=10, font_weight="bold")

    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=activity_type.name, markersize=10,
                                  markerfacecolor=color_map[activity_type])
                       for activity_type in Activity.ActivityType]

    avg_location_distance = sum(loc1.distances[loc2.number] for loc1 in locations_list for loc2 in locations_list if
                                loc1.number != loc2.number) / (p_num_locations * (p_num_locations - 1))

    radius_scaling_factor = 0.25

    for loc in locations_list:
        # Draw a circle around activities within a location
        circle_radius = avg_location_distance * radius_scaling_factor
        circle = plt.Circle((loc.coords[1], nrows - loc.coords[0]), circle_radius, fill=False,
                            color=f'C{loc.number % 10}', linestyle='dashed', linewidth=1)
        ax.add_artist(circle)

        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', linestyle='None', label=f'Location {loc.number}', markersize=10,
                       markerfacecolor=f'C{loc.number % 10}', markeredgewidth=0))

        # Draw a black dot at the center of the location coordinates
        ax.plot(loc.coords[1], nrows - loc.coords[0], marker='o', markersize=5, color='black')

    plt.legend(handles=legend_elements, loc='best', title='Activity Types & Locations')

    plt.show()


def generate_random_window(p_specs: tuple[int, int, int]) -> tuple[int, int]:
    start, stop, step = p_specs
    time1 = random.randrange(start=start, stop=stop, step=step)
    time2 = random.randrange(start=start, stop=stop, step=step)
    tempList: list[int] = list((time1, time2))
    tempList.sort()
    return tempList[0], tempList[1]


def print_edges(G):
    intra_edges = []
    inter_edges = []

    for edge in G.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            intra_edges.append(edge)
        elif edge[2]['edge_type'] == 'inter':
            inter_edges.append(edge)

    print("\nIntra-edges:")
    for edge in intra_edges:
        print(edge, "Duration:", edge[2]['duration'])

    print("\nInter-edges:")
    for edge in inter_edges:
        print(edge, "Duration:", edge[2]['duration'])

    print(f"Nodes: {G.nodes}")


def draw_mastnu(G):
    fig, ax = plt.subplots()

    node_colors = [color_map[node[1]] for node in G.nodes]

    # Sort nodes by agent and action to ensure vertical and sequential ordering
    sorted_nodes = sorted(G.nodes, key=lambda node: (node[0], node[1].value))

    locations = set(node[0] for node in sorted_nodes)

    # Assign y-coordinates to agents vertically
    agent_positions = {agent: idx for idx, agent in enumerate(sorted(locations))}

    # Assign x-coordinates to actions sequentially across the graph
    action_positions = {}
    action_index = 0
    for node in sorted_nodes:
        if node[1] not in action_positions:
            action_positions[node[1]] = action_index
            action_index += 1

    pos = {node: (agent_positions[node[0]], action_positions[node[1]]) for node in sorted_nodes}

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, alpha=0.8)

    intra_edges = []
    inter_edges = []

    for edge in G.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            intra_edges.append(edge)
        elif edge[2]['edge_type'] == 'inter':
            inter_edges.append(edge)

    nx.draw_networkx_edges(G, pos, edgelist=intra_edges, edge_color='blue', width=2.0, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edgelist=inter_edges, edge_color='black', width=2.0, alpha=0.8)

    labels = {(location_number, activity_type): f"{activity_type.name}\n({location_number})"
              for location_number, activity_type in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=5, font_color='b')

    ax.set_xlabel('Actions')
    ax.set_ylabel('Agents')

    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=activity_type.name, markersize=10,
                                  markerfacecolor=color_map[activity_type])
                       for activity_type in Activity.ActivityType]
    plt.legend(handles=legend_elements, loc='best', title='Activity Types')

    plt.tight_layout()
    plt.show()


def generateListOfLocations(p_mapSize: int = None, p_numLocations: int = None, p_tests: set[TestObject] = None) -> list[
    Location]:
    tempLocationsList: list[Location] = []
    for i in range(1, p_numLocations + 1):

        # Generates random points until one is made that isn't already in the list of points
        rand_point: tuple[int, int] = ()
        while True:
            rand_row: int = random.randrange(0, p_mapSize)
            rand_col: int = random.randrange(0, p_mapSize)
            rand_point = (rand_row, rand_col)

            if not (rand_point in [location.coords for location in tempLocationsList]):
                break
        temp_location: Location = Location(p_number=i, p_coords=rand_point)
        temp_location.fill_location_with_random_activities()
        tempLocationsList.append(temp_location)

    for loc1 in tempLocationsList:
        for loc2 in tempLocationsList:
            if loc1.number != loc2.number:
                loc1.calculate_distance_between_locations(loc2)
                loc1.generate_location_duration(loc2)

    return tempLocationsList


def generateTest(p_mapSize: int = None, p_numLocations: int = None) -> TestObject:
    if p_mapSize is None:
        raise Exception('p_mapSize cannot be None')
    if p_mapSize < 10:
        raise Exception('p_mapSize must be at least 10x10')
    if p_numLocations is None:
        raise Exception('p_numLocations cannot be None')

    finalTest: TestObject = None

    # Generate list of locations
    locationsList: list[Location] = generateListOfLocations(p_mapSize=p_mapSize, p_numLocations=p_numLocations)
    G = create_graph(locationsList)
    finalTest = TestObject(p_locations=locationsList, p_netx_graph=G, p_map_size=p_mapSize)
    return finalTest



# ===== MEMBER VARIABLES =====
logging.basicConfig(level=logging.DEBUG, )
m_logger: Logger = Logger(name='main_logger', level=logging.DEBUG)
m_base_speed: float = 2.0

points_list: list[tuple[int, int]] = []
locations_list: list[Location] = []

# Technical Boat Params
# Min, and Max times plus time step in minutes
activity_times = {Activity.ActivityType.TECHNICAL: (30, 40, 1),
                  Activity.ActivityType.MEDICAL: (15, 20, 1),
                  Activity.ActivityType.RESCUE: (10, 15, 1)}

boat_speeds = {Activity.ActivityType.TECHNICAL: (m_base_speed * 0.5, m_base_speed * 3.5, 1),
               Activity.ActivityType.MEDICAL: (m_base_speed * 1, m_base_speed * 4, 1),
               Activity.ActivityType.RESCUE: (m_base_speed * 2, m_base_speed * 5, 1)}
color_map = {Activity.ActivityType.TECHNICAL: "skyblue",
             Activity.ActivityType.RESCUE: "lightgreen",
             Activity.ActivityType.MEDICAL: "salmon"}

# ===== TEST QUANTITIES =====
# A list of quantities of locations
m_nums_locations: list[int] = list(range(2, 20, 1))
# A list of map sizes
m_map_sizes: list[int] = list(range(10, 20, 1))
# Number of tests per difficulty level
m_num_tests_per_difficulty: int = 2
# The number of tests that will be performed based on the numbers of locations and map sizes to be assessed
m_num_tests: int = len(m_nums_locations) * len(m_map_sizes) * m_num_tests_per_difficulty
m_num_tests_succeeded: int = 0

m_num_tests_to_sample: int = 5
m_test_numbers_to_sample: list[int] = random.choices(population=range(1, m_num_tests, 1),
                                                     k=m_num_tests_to_sample)
m_all_tests: set[TestObject] = set()
m_sampled_tests: set[TestObject] = set()

# ===== MAIN SCRIPT BODY =====
currTestNum: int = 1
sampleTest: bool = False

logging.info(F'BEGINNING {m_num_tests} TESTS\nEst. Time: {m_num_tests * 0.00903:.5f} seconds')
Time.sleep(3)

totalStartTime: float = time()
for mapSize in m_map_sizes:
    for numLocations in m_nums_locations:
        for i in range(0, m_num_tests_per_difficulty, 1):
            logging.info(msg=f'[{mapSize}x{mapSize} MAP] [{numLocations} LOCS] [TEST {currTestNum}]: Beginning test...')
            if currTestNum in m_test_numbers_to_sample:
                sampleTest = True
                logging.info(msg='** SAMPLING TEST **')
            else:
                sampleTest = False

            testStartTime: float = time()
            tempTest: TestObject = generateTest(p_mapSize=mapSize, p_numLocations=numLocations)
            testSucceeded: bool = scheduleTest(p_test=tempTest)
            testOutcomes: list = [False, True]
            # testSucceeded: bool = random.choice(testOutcomes)
            testEndTime: float = time()
            testTime: float = (testEndTime - testStartTime)

            tempTest.succeeded = testSucceeded
            tempTest.test_time = testTime
            m_all_tests.add(tempTest)
            logging.info(msg=f'Test complete. {testTime:.4f} seconds elapsed\n')

            if testSucceeded:
                m_num_tests_succeeded += 1

            if sampleTest:
                m_sampled_tests.add(tempTest)

            currTestNum += 1

totalEndTime: float = time()
logging.info(
    msg=f'==== ALL TESTS COMPLETE ====\nTests Run: {currTestNum}  \nTotal Time: {(totalEndTime - totalStartTime):.4f} seconds')

print(m_all_tests)
print(m_num_tests_succeeded)
# for test in m_sampled_tests:
#     graph = test.netx_graph
#     print_edges(graph)