
import random
from numpy import ndarray
import numpy as np
from enum import Enum

from boats import Boat


"""
1. Implement increased movement cost for state based on obstacle density
    -How to assess density?
    -

"""

class State:
    class StateType(Enum):
        OPEN = 1
        BLOCKER = 2
        START_POINT = 3
        RESCUE_GOAL = 4
        MEDICAL_GOAL = 5
        TECHNICAL_GOAL = 6

    # A list of the various Types present at this location (Can be open and a goal, for example)
    types: list[StateType] = None

    objectivesResolved: list[tuple[StateType, bool]] = []
    movementCost: int = None


    def __init__(self, p_stateTypes: list[StateType], p_moveCost: int = 1):
        self.types = p_stateTypes
        self.movementCost = p_moveCost

        # Checks whether this state is one of the goal states, then adds the present objectives to a tuple of the form (StateType, bool) representing whether it has been resolved
        for type in self.types:
            if (type == State.StateType.RESCUE_GOAL) or (type == State.StateType.MEDICAL_GOAL) or (type == State.StateType.TECHNICAL_GOAL):
                self.objectivesResolved.append( (type, False) )


class GridSquare:
    state: State = None
    boat: Boat = None

    def __init__(self, p_state: State=None, p_boat: Boat=None):
        if p_state is None:
            raise Exception('Provided state cannot be None')

        self.state = p_state
        self.boat = p_boat

class StatesGrid:

    numColumns: int = None
    numRows: int = None
    numBlockers: int = None

    numRescueGoals: int = None
    numMedicalGoals: int = None
    numTechnicalGoals: int = None

    numStartPoints: int = None

    def __init__(self, p_numCols: int=None, p_numRows: int=None, p_numBlockers: int=None, p_numRescueGoals: int=None, p_numMedicalGoals: int=None, p_numTechnicalGoals: int=None, p_numStartPoints: int=None):
        if p_numCols is None:
            raise Exception('p_width cannot be None')
        if p_numRows is None:
            raise Exception('p_height cannot be None')
        if p_numBlockers is None:
            raise Exception('p_numBlockers cannot be None')
        if p_numRescueGoals is None:
            raise Exception('p_numRescueGoals cannot be None')
        if p_numMedicalGoals is None:
            raise Exception('p_numMedicalGoals cannot be None')
        if p_numTechnicalGoals is None:
            raise Exception('p_numTechnicalGoals cannot be None')
        if p_numStartPoints is None:
            raise Exception('p_numStartPoints cannot be None')

        self.numColumns = p_numCols
        self.numRows = p_numRows
        self.numBlockers = p_numBlockers
        self.numRescueGoals = p_numRescueGoals
        self.numMedicalGoals = p_numMedicalGoals
        self.numTechnicalGoals = p_numTechnicalGoals
        self.numStartPoints = p_numStartPoints


    def generateNewRandomGrid(self) -> ndarray[GridSquare]:
        finalGrid: ndarray = ndarray(shape=(self.numRows, self.numColumns), dtype=GridSquare)

        raise NotImplementedError()

        # for i in range(self.numRows):
        #     for j in range(self.numColumns):
        #         finalGrid[i, j] =

