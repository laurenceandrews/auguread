# Auguread
Software Engineering Major Group Project

Book Club

## Deployed version
Link:

**Access credentials**

Club owner
Username:
Password:

Club member
Username:
Password:

Club applicant
Username:
Password:

Standard user
Username:
Password:

## Team Sick Legends
The authors of the software are:
- Laurence Andrews
- Surya Brunton
- Giorgia Mocan
- Yasameen Mohammed
- Marc (Moishi Netzer) Netzer
- Iki (Niki) Norgren
- Aria Rub
- Clara Zard

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

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`

- [django-scheduler](https://django-scheduler.readthedocs.io/en/latest/), specifically the Calendar, Event and Rule models


**For more information, please refer to the Developer's-Manual.md**
