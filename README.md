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

viz.py: Contains most code used for visualizations and graphs.
mastnu.py: Contains the implementation of the MaSTNU framework, and all the code responsible for scheduling a given test and handing back a response.
main.py: 