# Developer's Manual
Software Engineering Major Group Project

Book Club

Team Sick Legends

## Required Software Installation Instructions  
The following instructions are tailored to the Linux OS. All commands should be run in a Terminal window.
1. Install a code editor. Atom can be installed from Ubuntu Software. Alternative installation instructions can be found at [Installing Atom](https://flight-manual.atom.io/getting-started/sections/installing-atom/).
2. Install python. Ubuntu 20.04 comes with Python 3 preinstalled.
To verify this, enter the following command:
```
$ python3 --version
```

This should print out a version number.
Alternatively, python installation instructions can be found at [Download Python](https://www.python.org/downloads/).

3. Install pip.
```
$ sudo apt-get update
$ sudo apt-get -y install python3-pip
$ pip3 --version
```

If the installation was successful, this should return the version number of pip3.
Alternative installation instructions can be found at [Installation - pip documentation v22.1.dev0](https://pip.pypa.io/en/latest/installation/).

4. Install Virtualenv.
```
$ sudo pip3 install virtualenv
$ virtualenv --version
```

If the installation was successful, this should return the version number of Virtualenv.

5. Install Git.
```
$ sudo apt-get update
$ sudo apt install git
```

To configure git, use the following commands:
```
$ git config --global user.name "insert your name here"
$ git config --global user.email "insert your email here"
```

You can verify your current configuration with the command:
```
$ git config --list
```

Alternative installation instructions can be found at [Install Git | Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/install-git).  

6. Install django.
```
$ python -m pip install Django
```

Alternative installation instructions can be found at [Quick install guide | Django documentation](https://docs.djangoproject.com/en/4.0/intro/install/).  

## Project Installation Instructions
The following instructions are tailored to the Linux OS. To install and run the software in its current state, the following steps should be carried out.
1. Clone the remote repo.
```
$ git clone https://github.com/tinybuddha/sick-legends
```

The code base can be accessed at https://github.com/tinybuddha/sick-legends.

2. Set up and activate a local development environment. From the root of the project:
```
$ virtualenv venv
$ source venv/bin/activate
```

3. Install all required packages:

```
$ pip3 install -r requirements.txt
```

To view a list of all installed packages, run the command:
```
$ pip3 freeze
```

4. Migrate the database:

```
$ python3 manage.py migrate
```

If an error like `django.db.utils.OperationalError: table "{table_name}"
already exists` occurs, migrate using the command:
```
python manage.py migrate --fake clubs
```
5. Seed the development database with:

```
$ python3 manage.py seed
```

6. Run all tests with:
```
$ python3 manage.py test
```

## Running the Project Locally
The following instructions are tailored to the Linux OS. After completing all installation instructions, the software can be run on the local server using the following commands:
1. Run the software on the local server:
```
$ python manage.py runserver
```

2. Visit http://localhost:8000/

## Test Coverage
First, verify that the terminal is navigated to the project’s directory and the virtual environment has been activated (see above for commands)

Next, verify that a version of the coverage is installed in the requirements using the command below to install all requirements (as previously):
```
$ pip3 install -r requirements.txt
```

The developer may also view all the installed requirements with:
```
$ pip3 freeze
```

1. Run all tests with:
```
$ coverage run manage.py test
```

2. Generate a coverage report in the terminal using:
```
$ coverage report
```

3. Or create an html page with:
```
$ coverage html
```

4. Open the html page on a MacOS device using:
```
$ open htmlcov/index.html
```

5. Note: If a Virtual Machine is being used to run the software such as Ubuntu and Firefox is used to open the html page then use the following command instead:
```
$ firefox htmlcov/index.html &
```

## DjangoSchedule
DjangoSchedule is used in the project to handle scheduling and displaying club meetings.

DjangoSchedule is specified in requirements.txt and can be installed by running the following command in the virtual environment:
```
$ pip3 install -r requirements.txt
```

Django Scheduler relies on jQuery to provide its user interface.  All requirements for DjangoSchedule have been included in the static files.

The Auguread site allows club owners to create one-time events. DjangoSchedule provides support for recurring events. To enable this and other features, please use the guidance found in [DjangoSchedule's documentation](https://django-scheduler.readthedocs.io/en/latest/index.html).

## Recommender Evaluation
To evaluate the book-to-user recommender:
1. Firstly, ensure that you are currently in the /sick-legends/ folder
2. Traverse to the book to user recommender folder:
```
$ cd clubs/book_to_user_recommender
```
3. Run the python script for the evaluator:
```
$ python book_to_user_evaluator.py
```

## Tailwind Styling
Tailwind is used in this project in order to make styling components easy and to allow changing styling for specific elements rapidly allowing for a fast iterative approach to styling and ui/ux design.

We created our site as a Responsive-First site, making the user experience feel smooth and intuitive throughout the site. Being mobile optimised has greatly influenced the design decisions that were made to make sure that in a world where most of the user base will be accessing the site through mobile devices users will feel welcomed and will enjoy using the site.

Tailwind is included in the requirements file of the project. To update the styling, activate the virtual environment and install the package by running the command:
```
$ pip3 install -r requirements.txt
```

Tailwind generates the css classes file on-the-fly in a file at the path:
```
> theme/static/css/dist/styles.css
```
This file is essentially where Tailwind saves the custom css classes so that users who don’t have Tailwind installed still see all the stylings that Tailwind offers.

In order to generate new classes in the templates, you will need to install the node runtime.
It is highly recommended to use **nvm** in order to do so.

- For Linux-based users follow the [following guide](https://github.com/nvm-sh/nvm#installing-and-updating)

- For Windows-based users follow the [following guide](https://github.com/coreybutler/nvm-windows#installation--upgrades)

It is recommended to go ahead and install the Latest Version of node and not the LTS (Long Term Support) version

Given node has different paths whether on Windows or Linux developers must change the following variable in settings.py to one of the following
```
NPM_BIN_PATH = r"/usr/local/bin/npm" # Linux

# OR

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd" # Windows
```

After doing so you can proceed with the following command to install Tailwind in your project
```
$ python manage.py tailwind install
```

In order to generate the Tailwind classes, the developer must then start up the tailwind watcher by using the following command
```
$ python manage.py tailwind start
```

Note that Tailwind will hot-reload whenever changes are saved.
