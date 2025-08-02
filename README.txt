Set up the database:

1.Download PostgreSQL: https://www.postgresql.org/download/
2.Install PostgreSQL. During the installation make sure that both PostgreSQL Server and pgAdmin are checked
3.You will be asked to set a password for the superuser account (which is named postgres, for this project,
the password used during development was superuser. You should use the same password to ensure it matches the app's configuration.
4. Open pgAdmin
5. Connect to the server. After pgAdmin opens, it will ask for the superuser password you created during installation
6. Create the database. In the browser tree on the left, right click on database, select create and then database, 
in the database field enter the name "users" to match the app configuration and save it
7. Right click on the "users" database and select Query Tool
8. Load the SQL script that is present in the project directory by clicking the Open File icon in the tool bar
9. Execute the script by clicking the Execute button in the tool bar

Set up App:

1. Open the project directory with a IDE for python programming, i recommend PyCharm that is what i used
2. Open the built in terminal if the IDE does not have one open cmd or powershell and navigate to the project directory
3. Create a python environment with the following command "python -m venv .venv"
4. Activate the environment with the following command: ".\.venv\Scripts\activate" for cmd and ".venv\Scripts\Activate.ps1" for powershell, "source .venv/bin/activate" for macOS and Linux
5. Install required packages by running the command: "pip install -r requirements.txt"
6. Run app by using: "flask run"
7. Open browser and access: "http://127.0.0.1:5000"