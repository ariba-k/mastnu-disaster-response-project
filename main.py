from __future__ import annotations

import math
import random
from collections import defaultdict
from enum import Enum
from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx


class Activity:
    class ActivityType(Enum):
        TECHNICAL = 1
        RESCUE = 2
        MEDICAL = 3

    type: ActivityType = None
    duration: tuple[int, int]

    def __init__(self, p_type: ActivityType = None):
        self.type = p_type

    def generate_activity_duration(self):
        activity_duration = generate_random_window(activity_times[self.type])
        self.duration = activity_duration


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
        # FIXME: Does this return what I think it does? This does not calc Euclidean
        self.distances[loc2.number] = math.dist(self.coords, loc2.coords)

    def generate_location_duration(self, loc2: Location) -> None:
        for activity_type, speed in boat_speeds.items():
            distance = self.distances[loc2.number]
            min_speed, max_speed, step = speed
            random_speed_range = generate_random_window((int(min_speed), int(max_speed), step))
            min_duration, max_duration = (distance / random_speed_range[0]), (distance / random_speed_range[1])
            self.durations[loc2.number][activity_type] = (min_duration, max_duration)


def create_graph(locations: list[Location]):
    G = nx.DiGraph()
    intra_edge_activity_pairs = set()
    for location in locations:
        activity_count = len(location.activities)
        for idx, activity in enumerate(location.activities):
            activity.generate_activity_duration()

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


def draw_graph(G, dim):
    ncols, nrows = dim
    fig, ax = plt.subplots()

    # Define the positions in a grid layout
    pos = {(location_number, activity_type): (coords[1] + 0.5 * (activity_type.value - 2), nrows - coords[0])
           for location_number, coords in [(loc.number, loc.coords) for loc in locations_list]
           for activity_type in Activity.ActivityType}

    node_colors = [color_map[node[1]] for node in G.nodes]

    edge_colors = nx.get_edge_attributes(G, 'color').values()
    nx.draw(G, pos, with_labels=False, node_size=500, node_color=node_colors, edge_color=edge_colors,
            font_size=10, font_weight="bold")

    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=activity_type.name, markersize=10,
                                  markerfacecolor=color_map[activity_type])
                       for activity_type in Activity.ActivityType]

    avg_location_distance = sum(loc1.distances[loc2.number] for loc1 in locations_list for loc2 in locations_list if
                                loc1.number != loc2.number) / (num_locations * (num_locations - 1))

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
    tempList: list[int] = sorted([time1, time2])
    return tempList[0], tempList[1]


# ===== MEMBER VARIABLES =====
m_difficulty_modifier: float = 1.0  # Varies between zero and 1
m_base_speed: float = 5.0

num_locations: int = 2
points_list: list[tuple[int, int]] = []
locations_list: list[Location] = []

# Technical Boat Params
# Min, and Max times plus time step in minutes

activity_times = {Activity.ActivityType.TECHNICAL: (30, 40, 1),
                  Activity.ActivityType.MEDICAL: (15, 20, 1),
                  Activity.ActivityType.RESCUE: (10, 15, 1)}

boat_speeds = {Activity.ActivityType.TECHNICAL: (m_base_speed * 0.5, m_base_speed * 1.5, 1),
               Activity.ActivityType.MEDICAL: (m_base_speed * 1, m_base_speed * 2, 1),
               Activity.ActivityType.RESCUE: (m_base_speed * 2, m_base_speed * 3, 1)}

color_map = {Activity.ActivityType.TECHNICAL: "skyblue",
             Activity.ActivityType.RESCUE: "lightgreen",
             Activity.ActivityType.MEDICAL: "salmon"}

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
            loc1.calculate_distance_between_locations(loc2)
            loc1.generate_location_duration(loc2)


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

    edge_colors = [edge[2]['color'] for edge in G.edges(data=True)]

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


G = create_graph(locations_list)
draw_mastnu(G)

print_edges(G)
draw_graph(G, (cols, rows))
