# Open Data Management System (ODMS)

- [Design document](https://nikitas-docs.gitbook.io/open-data-management-system-design-document/)  

## 1. Context  
**Development team:**  
- Nikita Petrykin – backend developer / team lead  
- Danylo Yaremenko is a frontend developer  

**Brief description of the system:**  
The Open Data Management System is a digital platform that allows you to collect, store, manage and publish large open access data sets.  

The main requirements for such systems are:
1. Data Collection: ODMS provides tools to automate the process of collecting data from various sources, including other databases, websites, etc.
2. Data storage: ODMS provides safe and secure storage of open data, ensuring its availability for further use and analysis.
3. Data management: ODMS allows organizations to manage their data, including updating it, correcting errors, deleting outdated data, and setting data access policies.
4. Data Publishing: ODMS allows organizations to publish their data in user-friendly formats. These can be CSV files, JSON, XML, or other formats supported by many software.

ODMS also have data visualization capabilities, providing the ability to construct charts, graphs, and other visual representations of data to help better understand and analyze that data.  

## 2. How to build  
Since the system is under development, you can test it on your computer. For this:  
1. Clone the repository from the main branch and go to `publicdb/` directory:
```bash
$ git clone https://github.com/nikitosikvn1/django-odms-project.git
$ cd publicdb/
```
2. Next, you need to export the environment variables. You can do it manually or create an `.env` file:  
```bash
$ export SECRET_KEY="dyla9#jef!lsiy47#=4#gew1+v#!+d-u$llpem%qn(5(z5cmdc"
$ export NAMEDB="pdapp"
$ export USERDB="testuser"
$ export PASSWORDDB="testpassdb1234!"
$ export REDIS_PASSWD = "testpassred1234!"
```  
OR `.env` file:
```env
SECRET_KEY = "dyla9#jef!lsiy47#=4#gew1+v#!+d-u$llpem%qn(5(z5cmdc"
NAMEDB = "pdapp"
USERDB = "testuser"
PASSWORDDB = "testpassdb1234!"
REDIS_PASSWD = "testpassred1234!"
```
3. Make sure you have docker and docker-compose installed. You can download it from the [official site](https://www.docker.com/).  Start services:  
```bash
$ docker-compose up
```
4. If the build and run went without problems, then you can follow the link `http://127.0.0.1:8000/`. (Note that you won't see any content on the site since the database is empty)  
5. You can create test entries to test the system. To do this, you need to open a new terminal window and run:  
```bash
$ docker-compose exec django_app python manage.py migrate
$ docker-compose exec django_app python manage.py createsuperuser
```
6. Now go to `http://127.0.0.1:8000/admin/` and enter the credentials you provided when creating the superuser. Here you can create several categories, datasets and dataset files. (When creating dataset files, you need to upload a CSV table with data. In the first row you need to specify labels, in the second - values)  
7. Now on the main page you can see the created datasets and their associated files. I think you will understand what to do next.  

## 3. How to run tests  
If you have started docker-compose services, then just run:
```bash
$ docker-compose exec django_app python manage.py test -v 2
```
Where the -v flag takes a value from 1 to 4 and controls the output of debug information.