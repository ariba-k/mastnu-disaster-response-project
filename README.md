# READ ME: mastnu-disaster-response-project
Ariba Khan, Carter Godin, Shahsank Swaminathan
___
INSTRUCTIONS FOR USE
----------------
It is assumed that the user has a basic understanding of the use of python and pip via command line, and the setup of a pyton virtual environment. 
1. Clone the repository to your directory of choice, open with your chosen IDE (testing done in PyCharm, cannot guarantee functionality for others)\
2. Open a python terminal and (if necessary) navigate to your new project directory
3. Configure your python virtual environment and activate it in the terminal window
4. Once your venv is active and you are in the proper directory, use the command, "pip install -r requirements.txt". This command will install all required dependencies for the code from the requirements file via pip.
5. Once the dependencies are installed, the 'main.py' script may be run as-is. no environment variables or parameters need to be further specified.
___
SUMMARY OF CODE FUNCTIONALITY
----
The code is broken into 3 primary files, each handling a distinct element of the implementation's functionality.

1. viz.py: Contains most code used for visualizations and graphs.
2. mastnu.py: Contains the implementation of the MaSTNU framework, and all the code responsible for scheduling a given test and handing back a response.
3. main.py: Contains the bulk of the connective code for the project. 
   1. Classes:
      1. TestObject:
         Contains info about Locations involved, whether the test succeeded, and other parameters of the test such as map size and the time taken to run
      2. Location: 
         Defines a 'location' on the disaster relief map. Represents a location, its coordinates on the map, and the activities to be done there (ie debris removal, rescue, etc), as well as the distances between this location and all others
      3. Activity: 
         Contains an Enum to describe the type of activity, fields to store each the type and duration of the activity, and a method to randomly generate the activity's duration based on its type
   2. Script:
        Responsible for generating tests, calling the scheduler, assessing results, and generating plots.