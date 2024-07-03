### README.md for AdEye Detection Project

````markdown
# AdEye Detection System

## Overview

This Ad Detection System is designed to automatically detect specific advertisements in video streams using feature matching algorithms. The system is capable of processing live video feeds, identifying predefined ad signatures, and recording video segments when ads are detected.

## Features

- **Real-Time Ad Detection:** Detects advertisements in real-time video streams.
- **High Accuracy:** Uses ORB for feature matching to ensure high accuracy.
- **Video Recording:** Records segments of the video stream when advertisements are detected.
- **Persistent Streaming:** Handles long-duration video streams without interruption.
- **Configurable Parameters:** Allows users to set detection thresholds, match confidence, and other parameters.

## Installation

### Prerequisites

- Python 3.9 or higher but to be more precise use python 3.11 for the sake of dlib version used in this app.
- OpenCV with contrib modules
- NumPy
- Requests
- Flask
- Dlib

### Tutorial Steps

1. Project Setup:

   - Create MySQL Database
   - Initialize the Virtual Environment
   - Install the Project Dependencies

2. Writing the Project Code:

   - Writing the Main Files
   - Writing the Applications Files
   - Send Requests Using Postman

## Project Setup

### #1 Create MySQL Database

**Target**: Create a new database with a new user.

> 💡 _Tip: First create a test database with the same names & passwords below, then you can create a real database with the names & passwords you want!_

We will create a database called "**testdb**" and user "**testuser**" with password "**testpass**".

1. In Windows Terminal, Run the MySQL Server

   ```bash
   ~ sudo service mysql start
   ➜ * Starting MySQL 14 database server
   # 14 is the MySQL Server Version
   ```

   > 📝 _Important Note: We need to run the MySQL server every time we start coding!_

2. Activate the MySQL Shell

   ```bash
   ~ sudo -u mysql
   ➜ mysql=#
   ```

3. Create a New Database

   ```mysql
   <!-- create database DBNAME; -->
   mysql=# create database testdb;
   ➜ CREATE DATABASE
   ```

4. Create a Database User, then Grant Privileges to it

   ```mysql
   <!-- create user USERNAME with encrypted password 'PASSWORD'; -->
   mysql=# create user testuser with encrypted password 'testpass';
   ➜ CREATE ROLE

   <!-- grant all privileges on database DBNAME to USERNAME; -->
   mysql=# grant all privileges on database testdb to testuser;
   ➜ GRANT
   ```

5. Exit the Shell

   ```mysql
   mysql=# \q
   ```

6. Connect to the New Database

   ```bash
   ~ mysql -U testuser -h 127.0.0.1 -d testdb
   Password for user testuser: testpass
   ➜ testdb=>
   ```

7. Check the Connection

   ```mysql
   testdb=> \conninfo
   ➜ You are connected to database "testdb" as user "testuser" on host "127.0.0.1" at port "5432".
   <!-- We need this information later for the env file -->
   ```

Now that our new MySQL database is up and running, let's move on to the next step!

### #2 Initialize the Virtual Environment

- **What is the Virtual Environment?**

  > A virtual environment is a tool that helps separate dependencies required by different projects by creating isolated python virtual environments for them. This is one of the most important tools that most Python developers use.

  > virtualenv is used to manage Python packages for different projects. Using virtualenv allows you to avoid installing Python packages globally which could break system tools or other projects.

We'll create a virtual environment and activate it using the following commands

```bash
# virtualenv -p python3 ProjectName
~ virtualenv -p python3 Flask-SQLAlchemy-MySQL
➜ created virtual environment

cd Flask-SQLAlchemy-MySQL

source bin/activate
```

### #3 Install the Project Dependencies

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Jonah2016/ad_eye_.git
   cd ad_eye
   ```
````

2. After creating and activating the virtualenv, let's start with installing the project's dependencies

```bash
pip install python-dotenv flask flask-sqlalchemy Flask-Migrate flask_validator psycopg2-binary
```

3. Then make a folder called src which will contain the project codes

```bash
mkdir src && cd $_
```

4. The Last step before starting with the code, create a requirements file using this command:

```bash
python -m pip freeze > requirements.txt
```

### #4 Usage

### Configuration

Edit the `config.py` and `.env` files to set up the video server URL, database endpoints, and other system configurations.

### Running the Detector

To start the ad detection process without debug mode, use the following command:

Now our basic app is ready to go! We can run the server in the terminal by using one of the following commands:

```bash
# To Run the Server in Terminal
flask run

# To Run the Server with specific host and port
# flask run -h HOSTNAME -p PORTNUMBER
flask run -h 127.0.0.2 -p 5001

# To Run the Server with Automatic Restart When Changes Occur
FLASK_DEBUG=1 flask run
```

You can open your browser at <http://127.0.0.1:5000> and see the result!

### Adding Test Images

- Go to Recorded page, upload the file and enter the necessary parameters and select the respective channels to search through.
- Click "Create Recorded Query"

### Monitoring Outputs

- Check the 'Report' page select the query to retrieve the details report.

- Check the "Statuses" page to retrieve the current status of the project.

- Check the `app/static/detected_frames` and `app/static/recorded_frames` directories for outputs, including detected frames and recorded video clips.

## Contributing

Contributions to the Ad Detection System are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Project Maintainer:** [Your Name](mailto:your.email@example.com)
- **Project Link:** [https://github.com/yourusername/ad-detection-system](https://github.com/yourusername/ad-detection-system)

## Acknowledgments

- Thanks to the OpenCV community for providing the tools necessary for this project.

```

### Explanation
1. **Overview**: Describes what the system does and its key features.
2. **Installation**: Detailed steps on how to set up and get the project running.
3. **Usage**: Instructions on how to use the system after installation.
4. **Contributing**: How others can contribute to the project.
5. **License**: Information about the project's licensing.
6. **Contact**: How to reach out to the maintainer or get more help.
7. **Acknowledgments**: Credits to any third-party resources or contributors.

You can customize this template further to match your project's specific requirements and details. This README should provide a good starting point for anyone looking to understand or contribute to your project.
```

```

```
