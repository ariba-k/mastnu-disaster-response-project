from enum import Enum


class Boat:

    class BoatType(Enum):
        RESCUE = 1
        MEDICAL = 2
        TECHNICAL = 3

    # The type of boat
    type: BoatType = None

    # Current coordinates (row, column)
    coordinates: tuple[int, int] = None

    # Movement speed - Num. Squares per action
    move_speed: int = None

    cargoCap: int = None
    currentCargo: int = None

    def __init__(self, p_boatType: BoatType=None, p_coordinates: tuple[int, int]=None, p_moveSpeed: int=1, p_cargoCap: int=2, p_currCargo: int=0):

        if p_boatType is None:
            raise Exception('Provided boat type cannot be None')
        if p_coordinates is None:
            raise Exception('Provided coordinates cannot be None')


        self.type = p_boatType
        self.coordinates = p_coordinates
        self.move_speed = p_moveSpeed
        self.cargoCap = p_cargoCap
        self.currentCargo = p_currCargo


    def move(self):
        raise NotImplementedError()

    def performRescue(self):
        # Cannot rescue if not a rescue boat
        raise NotImplementedError()

    def performMedicalAction(self):
        # Cannot perform medical action if not medical boat
        raise NotImplementedError()

    def performDebrisRemoval(self):
        # Cannot remove debris if not technical
        raise NotImplementedError()