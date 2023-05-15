from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Dict
import math
from networkx import DiGraph
import random


def generate_random_window(p_specs: tuple[int, int, int]) -> tuple[int, int]:
    start, stop, step = p_specs
    time1 = random.randrange(start=start, stop=stop, step=step)
    time2 = random.randrange(start=start, stop=stop, step=step)
    tempList: list[int] = list((time1, time2))
    tempList.sort()
    return tempList[0], tempList[1]


class Activity:
    class ActivityType(Enum):
        TECHNICAL = 1
        RESCUE = 2
        MEDICAL = 3

    type: ActivityType = None
    duration: tuple[int, int]

    def __init__(self, p_type: ActivityType, activity_times):
        self.type = p_type
        self.duration = self.generate_activity_duration(activity_times)

    def generate_activity_duration(self, activity_times):
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

    def fill_location_with_random_activities(self, activity_times):
        """
        This method should generate a random list of activities and set that as the object's 'activities' field
        :return:
        """
        activity_types = list(Activity.ActivityType)
        num_activities = random.randint(1, len(activity_types))

        # Randomly sample the specified number of activity types without replacement
        selected_activity_types = random.sample(activity_types, num_activities)

        # Create activities with the selected activity types and assign them to the location
        self.activities = [Activity(activity_type, activity_times) for activity_type in selected_activity_types]

    def calculate_distance_between_locations(self, loc2: Location) -> None:
        self.distances[loc2.number] = math.dist(self.coords, loc2.coords)

    def generate_location_duration(self, loc2: Location, boat_speeds) -> None:
        for activity_type, speed in boat_speeds.items():
            distance = self.distances[loc2.number]
            min_speed, max_speed, step = speed
            random_speed_range = generate_random_window((int(min_speed), int(max_speed), step))
            max_duration, min_duration = (distance / random_speed_range[0]), (distance / random_speed_range[1])
            self.durations[loc2.number][activity_type] = (min_duration, max_duration)


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
