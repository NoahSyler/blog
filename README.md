###### This program was used in a lab for my server administration course. The following contains is my lab report, detailing how the server was launched.


# Abstract

The purpose of this lab was to gain experience managing web and application servers, as well as the application's connection to database servers. This was accomplished by actually deploying a developing and deploying a website. In this case, and Ubuntu server was used, running as a AWS EC2 machine. On that Ubuntu server was an Nginx reverse proxy, which passed dynamic requests to Gunicorn (which stands for 'Green Unicorn,' often pronounced as 'G-Unicorn'). Nginx handled the static files on its own. Gunicorn ran the Django application that I wrote to handle the dynamic requests.

# Table of Contents

[Abstract](#abstract)

[Introduction](#introduction)

- [Web Server](#web-server)

- [Web Application Server](#web-application-server)

- [WSGI](#wsgi)

[Experimental Procedure](#experimental-procedure)

- [Prepping Django](#prepping-django)

- [Ubuntu](#ubuntu)

- [Configuring the Web and Application Servers](#configuring-the-web-and-application-servers)

- [MySQL](#mysql)

[Conclusion](#conclusion)

[Works Cited](#works-cited)

# Introduction

## Web Server

The most basic website is a static site. This means that the client (a user's browser), receives files as they are to view. An example of this could be an html file consisting of a blog post. In this scenario, the blog post may contain pictures or CSS, but not much more. There would be no way to like, comment, or save the blog post. Rather, a user will simply navigate the site, probably with built-in anchor tags, to request and view the server's static files. Popular examples of these include Nginx and Apache [1].

## Web Application Server

A web application server can handle static files and much more. It is dynamic, meaning the server can update files based before serving them to the client. They files served for the given page can change, hence they are dynamic. Some examples of these include Apache Tomcat and Microsoft IIS [1].

## WSGI

WSGI stands for Web Server Gateway Interface. It is standard interface that stands between a web server and a Python web framework. Unlike tradition web application servers, these are fundamentally built to run Python applications behind a web server. An exception to this would be uWSGI, which can not only run on its own, but also support other language frameworks. Apache has the package available called mod\_wsgi, other options include Gunicorn and Waitress. A very common combination for websites using Python in the back-end is Nginx and Gunicorn [2].

# Experimental Procedure

## Prepping Django

- In my settings.py file, I pointed the program to look for static files in the 'staticfiles' folder.
- Ran the command python3 manage.py collectstatic, which copied all of the needed static files to that folder.
- Ran python3 manage.py makemigrations and python3 manage.py migrate to make sure all of the migrations from the project were up to date.
- Created a virtual environment with python3 -m pip venv django\_my\_site. This is something I probably should have done sooner.
- I added the required packages needed to this environment with pip.
- The benifit of using the virtual environment is that only the packages downloaded for the project are available.
- Now, I ran python3 -m freeze \> requirements.txt. This conveniently created a text file outlining the dependencies of the project.
- See [Picture 19: Admin Login](#picture19) for the final product's admin page, which can only be accessed by port 8088, and [Picture 18: Blog Index Page](#picture18) for the final blog site, which is accessed by port 80.
  - During the presentation, my admin page would not load. I discovered that this was due to a setting in my settings.py file called 'CSRF\_TRUSTED\_ORIGINS.' I am not sure, however, why it worked the day before, and then stopped working for the presentation.
  - From this Admin page, the content can be managed ([Picture 14: Admin Page Overview](#picture14), [Picture 15: Admin Page View for Single Table](#picture15)).
  - Also see [Picture 20: Admin Denied Access Through Port 80](#picture20) and [Picture 21: Site Denied Access Through Port 8088](#picture21)

## Ubuntu

- Created an EC2 instance in AWS with the following settings ([Picture 1: Ubuntu AWS initialization](#picture1)):
  - Ubuntu 22.04
  - 25 GB storage
  - micro instance type
  - SSH, HTTP, HTTPS traffic allowed
- Connected to instance with the following command:
  - ssh -i "my\_web\_server\_secret\_key.pem" ubuntu@ec2-44-208-26-70.compute-1.amazonaws.com
- Created a new key pair for the user I will add with the following command on the client ([Picture 5: New RSA Key](#picture5)):
  - ssh-keygen
- In the Linux terminal, I created a new user with the following command:
  - sudo adduser nsyler, then entered the password and other information for the user
- Added nsyler to the sudo group:
  - sudo usermod -aG sudo nsyler
- Verified this was successful with id nsyler
- switched user to nsyler with sudo su nsyler
- I saved the ssh key pair for nsyler with the following commands:
  - mkdir .ssh
  - chmod 700 .ssh
  - touch .ssh/authorized\_keys
  - vi .ssh/authorized\_keys
- I then pasted my public rsa key, hit esc, the :wq to write and quit.
- After doing this, I opened another terminal on the client, and tested the connection ([Picture 2: Initial Ubuntu Connection](#picture2)).
  - ssh -i id\_rsa nsyler@44.208.26.70
- It worked, so I exited out of the other terminal.

## Configuring the Web and Application Servers

  - sudo apt-get update
  - sudo apt-get upgrade
  - sudo apt-get install nginx
  - mkdir ~/django-site && mkdir
  - sudo apt install python3-venv
  - python3 -m venv django\_site/django\_venv

- In a separate terminal, I connected to the server with sftp
  - sftp -i "id\_rsa" nsyler@44.208.26.70
  - cd django\_site
  - lcd /Users/noahsyler/Documents/CompSci
  - put -r my\_site
- Now that the program files are uploaded, I activated the virtual environment:
  - source ../django\_venv/bin/activate
- Then installed Gunicorn:
  - pip install -r my\_site/requirements.txt
- I had trouble getting an updated version of mysqlclient to download, and had to also run the following command:
  - sudo apt-get install python3-dev default-libmysqlclient-dev build-essential libffi-dev

- Next, I needed to configure Gunicorn.
  - sudo touch gunicorn.conf
  - sudo vi gunicorn.conf

- Created a directory to save the logs
  - sudo mkdir /var/log/gunicorn
- Started Gunicorn to ensure it could work on its own.
  - gunicorn --bind 0.0.0.0:8000 my\_site.wsgi
- To exit the virtual environment, I entered:
  - deactivate
- Created a systemd socket to listen and start Gunicorn when needed.
  - sudo nano /etc/systemd/system/gunicorn.socket
- Set up the configuration for the Gunicorn socket ([Picture 3: Gunicorn Config](#picture3))
  - sudo vi /etc/systemd/system/gunicorn.service
- Verified the socket file was able to start:
  - sudo systemctl status gunicorn.socket
- Checked for the existence of the Gunicorn sock file:
  - file /run/gunicorn.sock
- Checked the journalctl file for errors:
  - sudo journalctl -u gunicorn.socket
- I tested my ability to use the socket internally with a curl command:
  - curl --unix-socket /run/gunicorn.sock localhost
- Checked Gunicorn for errors:
  - sudo systemctl status gunicorn
- I initially had some syntax errors in my configuration file. After updating the file, I used the following command:
  - sudo systemctl daemon-reload
  - sudo systemctl restart gunicorn

- Next, I needed to configure Nginx to be able to pass requests to Gunicorn ([Picture 4: Nginx Config](#picture4)).
  - sudo vi /etc/nginx/sites-available/my\_site
  - sudo ufw delete allow 8000
  - sudo ufw allow 'Nginx Full'
- I was able to check Nginx for errors with the following command:
  - sudo tail -F /var/log/nginx/error.log
- The folder holding the application root directory and virtual environment root directory is django\_site. The application root directory is stored at ~/home/nsyler/django\_site/my\_site ([Picture 9: Application Directory and Nginx var logs](#picture9))
- The access log files for Nginx can be viewed at /var/log/nginx/access.log ([Picture 9: Application Directory and Nginx var logs](#picture9))
- The error log files for Nginx can be viewed at /var/log/nginx/error.log ([Picture 9: Application Directory and Nginx var logs](#picture9))
- The Nginx process logs can be viewed with journalctl -u nginx ([Picture 10: Gunicorn and Nginx Process Logs](#picture10))
- The application logs for gunicorn can be viewed with journalctl -u gunicorn ([Picture 10: Gunicorn and Nginx Process Logs](#picture10))
- The socket logs for gunicorn can be viewed with journalctl -u gunicorn.socket ([Picture 11: Gunicorn Socket Logs](#picture11))

## MySQL

- I installed the MySQL Client on my machine for database management and the development environment.
  - brew install mysql
  - pip3 install mysql
  - mysql —version to check the installation

- I then created the database in Amazon RDS (Relational Database Services).
  - The options for this are located my default RDS options group ([Picture 12: MySQL Options](#picture12)).
- This allowed me to configure parts of the remote database before launching it, including adding an administrative user. However, If someone would like to add an administrator with AWS doing it for them, they could use the following command:
  - CREATE USER 'new\_user'@'localhost' IDENTIFIED BY 'password';
- I would use [https://dev.mysql.com/doc/refman/8.0/en/creating-accounts.html](https://dev.mysql.com/doc/refman/8.0/en/creating-accounts.html) for further information.

- Connected to the MySQL database, and adding a database for the application:
  - mysql -h mysql-dbms.crcyl8xm8erl.us-east-1.rds.amazonaws.com -P 3306 -u adminnsyler -p
  - CREATE DATABASE Blog
- From here, running python3 manage.py makemigrations and python3 manage.py migrate added my designed schema for this app to the database, after setting my hooks in the app's configuration ([Picture 13: Models Displaying Schema Configuration](#picture13)).
- The easiest way to start and stop this MySQL Remote Database is through the RDS menu in AWS ([Picture 16: AWS MySQL](#picture16)).
- MySQL login, users, and schema snippet: [Picture 17: MySQL Info](#picture17)

<a name='picture1'>![Picture1](https://github.com/NoahSyler/blog/assets/99105291/ec051bd1-3991-454a-9de8-6949cef38bcb)</a>

_Picture 1: Ubuntu AWS initialization_

<a name='picture2'>![Picture2](https://github.com/NoahSyler/blog/assets/99105291/e808f5d4-12fa-42f2-99a6-835f75382e2a)</a>

_Picture 2: Initial Ubuntu Connection_

<a name='picture4'>![Picture3](https://github.com/NoahSyler/blog/assets/99105291/179d5457-ae73-4ae9-97fd-5408bdcdf91e)</a>

_Picture 3: Gunicorn Config_

<a name='picture4'>![Picture4](https://github.com/NoahSyler/blog/assets/99105291/4fab86b9-6b4d-41f9-8957-685bea089ac5)</a>

_Picture 4: Nginx Config_

<a name='picture5'>![Picture5](https://github.com/NoahSyler/blog/assets/99105291/2afaa198-680b-4f47-b205-0bc3536cfde8)</a>

_Picture 5: New RSA Key_

<a name='picture6'>![Picture6](https://github.com/NoahSyler/blog/assets/99105291/5f14d4ce-5e6f-4b57-8ce0-d967d3eabf7c)</a>

_Picture 6: New User Ubuntu_

<a name='picture7'>![Picture7](https://github.com/NoahSyler/blog/assets/99105291/24568eb4-24c0-493a-a5f3-fd9b7d6b2144)</a>

_Picture 7: Public Key added to Ubuntu_

<a name='picture8'>![Picture8](https://github.com/NoahSyler/blog/assets/99105291/c4483ee4-279c-43a0-ad90-d823d264823e)</a>

_Picture 8: Uploading Program with SFTP_

<a name='picture9'>![Picture9](https://github.com/NoahSyler/blog/assets/99105291/947796e6-eb09-4d63-b96e-64736632ecee)</a>

_Picture 9: Application Directory and Nginx var logs_

<a name='picture10'>![Picture10](https://github.com/NoahSyler/blog/assets/99105291/3160acb4-78dc-4968-b5f9-15c93fc10b6e)</a>

_Picture 10: Gunicorn and Nginx Process Logs_

<a name='picture11'>![Picture11](https://github.com/NoahSyler/blog/assets/99105291/455d7f14-5bd8-4dda-a1c9-9ecbf6ec24d8)</a>

_Picture 11: Gunicorn Socket Logs_

<a name='picture12'>![Picture12](https://github.com/NoahSyler/blog/assets/99105291/0c763f60-9787-4b9f-97dc-cf6f076e6b68)</a>

_Picture 12: MySQL Options_

<a name='picture13'>![Picture13](https://github.com/NoahSyler/blog/assets/99105291/12a0e3fc-97bc-4df4-8eb1-3d4c72a1ae88)</a>

_Picture 13: Models Displaying Schema Configuration_

<a name='picture14'>![Picture14](https://github.com/NoahSyler/blog/assets/99105291/807326aa-5bf4-4d73-9fac-a5bb31899775)</a>

_Picture 14: Admin Page Overview_

<a name='picture15'>![Picture15](https://github.com/NoahSyler/blog/assets/99105291/ba39bd55-e037-4a8b-9166-c6c55b3f632e)</a>

_Picture 15: Admin Page View for Single Table_

<a name='picture16'>![Picture16](https://github.com/NoahSyler/blog/assets/99105291/a7175916-3dc3-4258-b5a1-b2571fc96f11)</a>

_Picture 16: AWS MySQL_

<a name='picture17'>![Picture17](https://github.com/NoahSyler/blog/assets/99105291/b728e992-1f41-493e-b707-281c18ca8d7c)</a>

_Picture 17: MySQL Info_

<a name='picture18'>![Picture18](https://github.com/NoahSyler/blog/assets/99105291/67414c3a-025e-45d8-a902-4a12abe65fdd)</a>

_Picture 18: Blog Index Page_

<a name='picture19'>![Picture19](https://github.com/NoahSyler/blog/assets/99105291/fbdd818b-eb00-471d-8d1b-bb3f9af3bf07)</a>

_Picture 19: Admin Login_

<a name='picture20'>![Picture20](https://github.com/NoahSyler/blog/assets/99105291/75e80413-d5ad-4f9c-8b5d-03ee3b6fadc6)</a>

_Picture 20: Admin Denied Access Through Port 80_

<a name='picture21'>![Picture21](https://github.com/NoahSyler/blog/assets/99105291/b2343515-ab5e-4b5e-9f36-86d4fa3f742a)</a>

_Picture 21: Site Denied Access Through Port 8088_

# Conclusion

The internet protocols have truly revolutionized how we connect to the world. The consistency the protocols bring allow users to receive information from around the world. By adhering the http or https protocol, client side browsers can make requests to various servers, and these servers are given tremendous flexibility in how they process the requests. All they have to do is send the response back via https. Whether they are serving static files as a simple webserver, or dynamic files as an application server, or efficiently spreading the load between a variety of different servers, clients and servers are able to communicate everywhere. This is an amazing feat.

# <a name="works-cited">Works Cited</a>

| [1] | Mozilla, "What is a web server?," MDN Web Docs, [Online]. Available: https://developer.mozilla.org/en-US/docs/Learn/Common\_questions/Web\_mechanics/What\_is\_a\_web\_server. [Accessed 26 June 2023]. |
| --- | --- |
| [2] | Real Python, "Web Applications & Frameworks," [Online]. Available: https://docs.python-guide.org/scenarios/web/. [Accessed 26 June 2023]. |

