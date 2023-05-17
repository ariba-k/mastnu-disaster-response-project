import logging
import random

import networkx as nx
from logging import Logger

import os
import sys

import time as Time
from time import time
from viz import process_data, scatter_plot_3D, heat_map, sensitivity_analysis
from viz import draw_graph, draw_mastnu
from objects import TestObject, Location, Activity

sys.path.insert(0, os.path.join(sys.path[0], sys.path[0] + '/scheduling'))

from scheduling.dc_checking.temporal_network import TemporalNetwork, SimpleTemporalConstraint, SimpleContingentTemporalConstraint

from scheduling.networks import MaSTNU
from scheduling.solve_decoupling import solve_decoupling


def scheduleTest(p_test: TestObject = None, output_stats: bool = False) -> bool:
    """
    Shashank put a call to your MaSTNU code here
    """
    if p_test is None:
        raise Exception('p_test cannot be None')

    ext_conts = []
    ext_reqs = []
    agent2network = {}

    for n in p_test.netx_graph.nodes():
        agent = n[1].name
        if agent not in agent2network:
            event = "{}-{}".format(agent, n[0])
            agent2network[agent] = TemporalNetwork()
            agent2network[agent].add_constraint(
                SimpleTemporalConstraint('z', event, lb=0, name='ref_preceding_{}'.format(agent)))
            agent2network[agent].add_event('z')
    for edge in p_test.netx_graph.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            ext_reqs.append(SimpleTemporalConstraint(**getTemporalConstraintData(edge)))
        else:
            agent = edge[0][1].name
            agent2network[agent].add_constraint(SimpleContingentTemporalConstraint(**getTemporalConstraintData(edge)))

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')

    try:
        decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True)
        if decoupling is None:
            print("none found.")
            return False

        if output_stats:
            print(decoupling.pprint())
            print(decoupling.pprint_proof(ext_reqs, ext_conts))
            print("Objective value: {}".format(decoupling.objective_value))

        print("decoupling found.")
        return True
    except:
        return False




def getTemporalConstraintData(e: tuple):
    return {"s": "{}-{}".format(e[0][1].name, e[0][0]),
            "e": "{}-{}".format(e[1][1].name, e[1][0]),
            "lb": e[2]['duration'][0],
            "ub": e[2]['duration'][0],
            "name": "{}{}-{}{}".format(e[0][1].name, e[0][0], e[1][1].name, e[1][0])}


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
        temp_location.fill_location_with_random_activities(activity_times)
        tempLocationsList.append(temp_location)

    for loc1 in tempLocationsList:
        for loc2 in tempLocationsList:
            if loc1.number != loc2.number:
                loc1.calculate_distance_between_locations(loc2)
                loc1.generate_location_duration(loc2, boat_speeds)

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
logging.basicConfig(level=logging.INFO)
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

m_nums_locations: list[int] = list(range(2, 10, 1))  # Increase upper bound (second param) if solution not found
# A list of map sizes
m_map_sizes: list[int] = list(range(10, 20, 1))  # Increase upper bound (second param) if solution not found
# Number of tests per difficulty level
m_num_tests_per_difficulty: int = 4
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

logging.info(F'BEGINNING {m_num_tests} TESTS\nEst. Time: {m_num_tests * 0.1:.5f} seconds')
Time.sleep(3)

totalStartTime: float = time()
lastSuccess = None
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
            testEndTime: float = time()
            testTime: float = (testEndTime - testStartTime)

            tempTest.succeeded = testSucceeded
            tempTest.test_time = testTime
            m_all_tests.add(tempTest)
            logging.info(msg=f'Test complete. {testTime:.4f} seconds elapsed\n')

            if testSucceeded:
                lastSuccess = tempTest
                m_num_tests_succeeded += 1

            if sampleTest:
                m_sampled_tests.add(tempTest)

            currTestNum += 1

totalEndTime: float = time()
logging.info(
    msg=f'==== ALL TESTS COMPLETE ====\nTests Run: {currTestNum}  \nTotal Time: {(totalEndTime - totalStartTime):.4f} seconds')

results = process_data(m_all_tests)
print(m_num_tests_succeeded)
scatter_plot_3D(results)
heat_map(results)
sensitivity_analysis(results, num_fixed_vals=5)

draw_graph(lastSuccess.netx_graph, lastSuccess.map_size, len(lastSuccess.locations), lastSuccess.locations, color_map)
draw_mastnu(lastSuccess.netx_graph, color_map)
