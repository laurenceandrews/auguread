# Team Sick Legends
SEG - Major Group Project

## Team Members
The authors of the software are:
- Laurence Andrews
- Surya Brunton
- Giorgia Mocan
- Yasameen Mohammed
- Marc (Moishi Netzer) Netzer
- Iki (Niki) Norgren
- Aria Rub
- Clara Zard

This file must include the following:

- The title of the project and the name of the software.
- A list of all significant parts of the source code written by others that you employed directly or relied on
heavily when writing this software and the locations of this source material.  Think of this as the "reference list" for your source code.
- The location where the software or software component is deployed and sufficient information to access it. The latter includes access credentials
for the different types of user who may employ the software.

Your README.md files may include other content if you wish.  For example, it may include a short description of the software and any other content you deem relevant.  This is not required, however.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```
Install bower components:

```
$ python manage.py bower install
```

Migrate the database:

```
$ python3 manage.py migrate
```
Collect static files:

```
$ python manage.py collectstatic
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

- [django-scheduler](https://django-scheduler.readthedocs.io/en/latest/), specifically the Calendar, Event and Rule models 
