"""
Problem Statement:

There are 3 boats performing a complex rescue operation. Groups of people spread across a flooded map dotted with randomly
placed/clustered obstacles. The people need help in a timely manner, some needing immediate medical attention, some trapped
beneath rubble, others are in need of immediate evacuation, and some are a combination of all of these.

The goal here is to organize our 3 boats (a technical boat to clear debris, a medical boat for treatment, and a rescue boat
for evacuation) such that all disaster victims are optimally freed, aided, and evacuated in the shortest time possible.
This task includes interdependent tasks like clearing debris to access trapped victims in need of medical aid, etc.

"""
import math
import random

import networkx
import numpy

from numpy import ndarray
import numpy as np
import networkx as nx
from enum import Enum
import matplotlib.pyplot as plt


class Activity:
    #     Consider making this a NetworkX Node object

    class ActivityType(Enum):
        TECHNICAL = 1
        RESCUE = 2
        MEDICAL = 3

    #     Type
    type: ActivityType = None

    # Duration
    duration: tuple[int, int]

    #     Links
    # TODO: What to do with this?

    def __init__(self, p_type: ActivityType = None):
        self.type = p_type


class Location:
    number: int = None
    activities: list[Activity] = None
    coords: tuple[int, int] = None

    # Entries are of the form:  {Location#: Distance}
    distances: dict[int, float] = None
    # Entries are of the form:  {Location#: Duration}
    durations: dict[int, tuple[float, float]] = None

    def __init__(self, p_number: int, p_activities: list[Activity] = None, p_coords: tuple[int, int] = None):
        self.number = p_number
        self.activities = p_activities or []
        self.coords = p_coords
        self.distances = {}

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

    @staticmethod
    def calculate_distance_between_locations(p_point1: tuple[int, int], p_point2: tuple[int, int]) -> float:
        # FIXME: Does this return what I think it does?
        return math.dist(p_point1, p_point2)

    @staticmethod
    def calculate_duration_from_distance(distance: float) -> tuple[float, float]:
        # Replace with randomly generated number
        min_speed, max_speed = 5, 10

        min_duration = distance / max_speed
        max_duration = distance / min_speed

        return min_duration, max_duration


def create_graph(locations: list[Location]):
    G = nx.DiGraph()
    for location in locations:
        activity_count = len(location.activities)
        for idx, activity in enumerate(location.activities):
            duration: tuple[int, int] = None
            match activity.type:
                case Activity.ActivityType.TECHNICAL:
                    duration = generateRandomWindow(m_technical_activity_time_range)
                case Activity.ActivityType.MEDICAL:
                    duration = generateRandomWindow(m_medical_activity_time_range)
                case Activity.ActivityType.RESCUE:
                    duration = generateRandomWindow(m_rescue_activity_time_range)
                case default:
                    pass
            activity.duration = duration

            G.add_node((location.number, activity.type), activity=activity)

            # Connect activities within the same location (intra-edges)
            if idx < activity_count - 1:
                next_activity = location.activities[idx + 1]
                # connectionstyle="arc3,rad=0.1"
                u_of_edge = (location.number, activity.type)
                v_of_edge = (location.number, next_activity.type)
                G.add_edge(u_of_edge, v_of_edge,
                           edge_type='intra', color='b')

                G.edges[u_of_edge, v_of_edge].update({m_edge_time_attribute_name:duration})

            for other_location in locations:
                # Connect activities of the same type between locations in ascending order (inter-edges)
                if other_location.number > location.number:
                    # Finds the next activity with the same type as the current activity
                    other_activity = next((a for a in other_location.activities if a.type == activity.type), None)
                    if other_activity is not None:
                        duration = location.durations[other_location.number]

                        G.add_edge((location.number, activity.type), (other_location.number, other_activity.type),
                                   edge_type='inter', color='k', duration=duration)
                        break
    return G


def draw_graph(G, dim):
    ncols, nrows = dim
    fig, ax = plt.subplots()

    # Define the positions in a grid layout
    pos = {(location_number, activity_type): (coords[1] + 0.5 * (activity_type.value - 2), nrows - coords[0])
           for location_number, coords in [(loc.number, loc.coords) for loc in locations_list]
           for activity_type in Activity.ActivityType}

    # Draw the nodes in different colors based on activity type
    color_map = {Activity.ActivityType.TECHNICAL: "skyblue", Activity.ActivityType.RESCUE: "lightgreen",
                 Activity.ActivityType.MEDICAL: "salmon"}
    node_colors = [color_map[node[1]] for node in G.nodes]

    edge_colors = nx.get_edge_attributes(G, 'color').values()
    # Draw the nodes with smaller size
    nx.draw(G, pos, with_labels=False, node_size=500, node_color=node_colors, edge_color=edge_colors,
            font_size=10, font_weight="bold")

    # Create a legend for the activity names
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=activity_type.name, markersize=10,
                                  markerfacecolor=color_map[activity_type])
                       for activity_type in Activity.ActivityType]

    avg_location_distance = sum(loc1.distances[loc2.number] for loc1 in locations_list for loc2 in locations_list if
                                loc1.number != loc2.number) / (num_locations * (num_locations - 1))

    radius_scaling_factor = 0.25

    # Draw circles and location labels
    for loc in locations_list:
        # Draw a circle around activities within a location
        circle_radius = avg_location_distance * radius_scaling_factor
        circle = plt.Circle((loc.coords[1], nrows - loc.coords[0]), circle_radius, fill=False,
                            color=f'C{loc.number % 10}', linestyle='dashed', linewidth=1)
        ax.add_artist(circle)

        # Add a legend for the location numbers
        legend_elements.append(
            plt.Line2D([0], [0], marker='o', color='w', linestyle='None', label=f'Location {loc.number}', markersize=10,
                       markerfacecolor=f'C{loc.number % 10}', markeredgewidth=0))

    plt.legend(handles=legend_elements, loc='best', title='Activity Types & Locations')

    plt.show()


def print_edges(G):
    intra_edges = []
    inter_edges = []

    for edge in G.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            intra_edges.append(edge)
        elif edge[2]['edge_type'] == 'inter':
            inter_edges.append(edge)

    print("Intra-location edges:")
    for edge in intra_edges:
        print(edge)

    print("\nInter-location edges:")
    for edge in inter_edges:
        print(edge)

def generateRandomWindow(p_specs: tuple[int, int, int]) -> tuple[int, int]:
    start, stop, step = p_specs
    time1 = random.randrange(start=start, stop=stop, step=step)
    time2 = random.randrange(start=start, stop=stop, step=step)
    tempList: list[int] = sorted([time1, time2])
    return tempList[0], tempList[1]

# ===== MEMBER VARIABLES =====
m_edge_time_attribute_name: str = 'duration'
m_difficulty_modifier: float = 1.0  # Varies between zero and 1
m_base_speed: float = 1.0

num_locations: int = 10
points_list: list[tuple[int, int]] = []
locations_list: list[Location] = []

# Technical Boat Params
# Min, and Max times plus time step in minutes
m_technical_activity_time_range: tuple[int, int, int] = (30, 40, 1)
m_technical_speed: float = m_base_speed*0.5

# Medical Boat Params
m_medical_activity_time_range: tuple[int, int, int] = (15, 20, 1)
m_medical_speed: float = m_base_speed*1

# Rescue Boat Params
m_rescue_speed: float = m_base_speed*2
m_rescue_activity_time_range: tuple[int, int, int] = (10, 15, 1)


# ==== STEPS TO LOOP FOR EACH SIMULATION ====
# Create nxn grid
rows = 10 * num_locations
cols = rows

# Create Locations at random points
for i in range(1, num_locations + 1):
    # Generates random points until one is made that isn't already in the list of points
    rand_point: tuple[int, int]
    while True:
        rand_row: int = random.randrange(0, rows)
        rand_col: int = random.randrange(0, rows)
        rand_point = (rand_row, rand_col)

        if not (rand_point in points_list):
            points_list.append(rand_point)
            break

    temp_location: Location = Location(p_number=i, p_coords=rand_point)
    temp_location.fill_location_with_random_activities()
    locations_list.append(temp_location)

for loc1 in locations_list:
    for loc2 in locations_list:
        if loc1.number != loc2.number:
            distance = Location.calculate_distance_between_locations(loc1.coords, loc2.coords)
            loc1.distances[loc2.number] = distance
            duration = calculate_duration_from_distance(distance)
            loc1.durations[loc2.number] = duration



def print_edges(G):
    intra_edges = []
    inter_edges = []

    for edge in G.edges(data=True):
        if edge[2]['edge_type'] == 'intra':
            intra_edges.append(edge)
        elif edge[2]['edge_type'] == 'inter':
            inter_edges.append(edge)

    print("\nInter-location edges:")
    for edge in inter_edges:
        print(edge, "Duration:", edge[2]["duration"])

    print("\nInter-location edges:")
    for edge in inter_edges:
        print(edge)


G = create_graph(locations_list)
print(G)
print(G.nodes)
print_edges(G)
draw_graph(G, (cols, rows))

# Calculate distances between all pairs of locations, store on each location

# Use distances to calculate time bounds [min, max] between locations

# For each location, generate the activities for the location. A random amount in some range dictated by the
# "difficulty" of this particular test. At most one of each type: Randomly determine (within a range) the durations
# of each activity of each type

# Link together all the activities at the location (determining the order in which they must happen)

# Link together subsequent activities of the same type, representing the nodes for each type of boat
