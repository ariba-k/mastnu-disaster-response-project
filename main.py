"""
1. Define State Class
1.b Define the two types of boats (Rescue and resupply)
2. Define grid of states
3. Determine optimal placement for resupply boat
4. Invoke path finder to hand back the best path between every unique combination of two points of interest
5. Instantiate Shashank's MaSTNU class. Add all nodes, and introduce edges by converting each path
    into nodes and edges, the edges being primarily contingent links (the upper bound being the
    path distance returned in #3, and the lower bound being the ideal distance if the agent were
    able to travel in a straight line there)

6. There are different types of Nodes: Travel/location nodes, Rescue nodes, resupply

    Travel - Happens at location, takes time to get there
    Rescue - Happens at location, takes time to load/unload people
    Resupply - Happens at location (initially undetermined), takes
                time to resupply, also invoked by resource constraints
                (Passenger capacity, fuel level, etc.)

    Each node of a type has a linear constraint (like the location or the cargo value it happens at)
    and a duration window [min, max] over which it could happen. For travel nodes, they happen at a
    location (you travel to that location) and it takes you some time to get there. Resupply and
    rescue both also happen at a location, and have some duration associated with each as well,
    but resupply has the added constraint of being performed at particular cargo values

7. Check whether MaSTNU could be decomposed to all agents; check dynamic controllability

Shashank - incorporating MaSTNU code from Pset here
Carter - Defining states, state grid, and boats
Ariba - Incorporate path finder

"""
