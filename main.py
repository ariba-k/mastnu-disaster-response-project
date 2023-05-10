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

from numpy import ndarray
import numpy as np
from enum import Enum


class Activity:
    #     Consider making this a NetworkX Node object

    class ActivityType(Enum):
        TECHNICAL = 1
        RESCUE = 2
        MEDICAL = 3

    #     Type
    type: ActivityType = None

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

    def __init__(self, p_number: int, p_activities: list[Activity]=None, p_coords: tuple[int, int]=None):
        self.number = p_number
        self.activities = p_activities
        self.coords = p_coords

    def fillLocationWithRandomActivities(self):
        """
        This method should generate a random list of activities and set that as the object's 'activities' field
        :return:
        """
    @staticmethod
    def calculateDistanceBetweenPoints(p_point1: tuple[int, int], p_point2: tuple[int, int]) -> float:
        # FIXME: Does this return what I think it does?
        return math.dist(p_point1, p_point2)

numLocations: int = 2
pointsList: list[tuple[int, int]] = []
locationsList: list[Location] = []

# ==== STEPS TO LOOP FOR EACH SIMULATION ====
# Create nxn grid
rows = 10*numLocations
cols = rows

# Create Locations at random points
for i in range(1, numLocations):
    # Generates random points until one is made that isn't already in the list of points
    randPoint: tuple[int, int]
    while True:
        randRow: int = random.randrange(0, rows)
        randCol: int = random.randrange(0, rows)
        randPoint = (randRow, randCol)

        if not (randPoint in pointsList):
            pointsList.append(randPoint)
            break

    tempLocation: Location = Location(p_number=i, p_coords=randPoint)
    tempLocation.fillLocationWithRandomActivities()
    locationsList.append(tempLocation)




# Calculate distances between all pairs of locations, store on each location

# Use distances to calculate time bounds [min, max] between locations

# For each location, generate the activities for the location. A random amount in some range dictated by the "difficulty" of
# this particular test. At most one of each type:
#     Randomly determine (within a range) the durations of each activity of each type

# Link together all the activities at the location (determining the order in which they must happen)

# Link together subsequent activities of the same type, representing the nodes for each type of boat
