"""
Problem Statement:

There are 3 boats performing a complex rescue operation. Groups of people spread across a flooded map dotted with randomly
placed/clustered obstacles. The people need help in a timely manner, some needing immediate medical attention, some trapped
beneath rubble, others are in need of immediate evacuation, and some are a combination of all of these.

The goal here is to organize our 3 boats (a technical boat to clear debris, a medical boat for treatment, and a rescue boat
for evacuation) such that all disaster victims are optimally freed, aided, and evacuated in the shortest time possible.
This task includes interdependent tasks like clearing debris to access trapped victims in need of medical aid, etc.


"""

from state import State, StatesGrid

# ==== STEPS ====

# Create boats

# Create 3 StatesSims, each with increasing complexity and difficulty