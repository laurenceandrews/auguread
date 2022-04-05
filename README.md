# Auguread
Software Engineering Major Group Project

Book Club

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

## Deployed version
Link (will be deployed by 15th April): https://auguread.herokuapp.com/

**Access credentials**

Example users will be provided by 15th April alongside the working deployed website.

Club Owner

- Email:
- Password:

Club Member

- Email:
- Password:

Club Applicant

- Email:
- Password:

Standard User

- Email:
- Password:

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
If an error like `django.db.utils.OperationalError: table "{table_name}" already exists` occurs, migrate using the command:

```
$ python manage.py migrate --fake clubs
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


**_For more information, please refer to the [Developer's Manual file](https://github.com/tinybuddha/sick-legends/blob/main/Developer's%20Manual.md)._**
