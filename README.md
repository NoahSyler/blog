**This program was used in a lab for my server administration course. The following it a description of the source**

Note: the images are not present, and the links are broken. This will be fixed in the next commit.

**Web Server Deployment**

**Noah Syler**

# Abstract

The purpose of this lab was to gain experience managing web and application servers, as well as the application's connection to database servers. This was accomplished by actually deploying a developing and deploying a website. In this case, and Ubuntu server was used, running as a AWS EC2 machine. On that Ubuntu server was an Nginx reverse proxy, which passed dynamic requests to Gunicorn (which stands for 'Green Unicorn,' often pronounced as 'G-Unicorn'). Nginx handled the static files on its own. Gunicorn ran the Django application that I wrote to handle the dynamic requests.

# Table of Contents

_**[Abstract 1](#_Toc138702610)**_

_**[Introduction 3](#_Toc138702611)**_

**[Web Server 3](#_Toc138702612)**

**[Web Application Server 3](#_Toc138702613)**

**[WSGI 3](#_Toc138702614)**

_**[Experimental Procedure 4](#_Toc138702615)**_

**[Prepping Django 4](#_Toc138702616)**

**[Ubuntu 4](#_Toc138702617)**

**[Configuring the Web and Application servers 5](#_Toc138702618)**

**[MySQL 7](#_Toc138702619)**

_**[Conclusion 19](#_Toc138702622)**_

_**[Works Cited 20](#_Toc138702623)**_

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
- See Picture 19: Admin Login for the final product's admin page, which can only be accessed by port 8088, and Picture 18: Blog Index Page for the final blog site, which is accessed by port 80.
  - During the presentation, my admin page would not load. I discovered that this was due to a setting in my settings.py file called 'CSRF\_TRUSTED\_ORIGINS.' I am not sure, however, why it worked the day before, and then stopped working for the presentation.
  - From this Admin page, the content can be managed (Picture 14: Admin Page Overview, Picture 15: Admin Page View for Single Table).
  - Also see Picture 20: Admin Denied Access Through Port 80 and Picture 21: Site Denied Access Through Port 8088

## Ubuntu

- Created an EC2 instance in AWS with the following settings (Picture 1: Ubuntu AWS initialization):
  - Ubuntu 22.04
  - 25 GB storage
  - micro instance type
  - SSH, HTTP, HTTPS traffic allowed
- Connected to instance with the following command:
  - ssh -i "my\_web\_server\_secret\_key.pem" ubuntu@ec2-44-208-26-70.compute-1.amazonaws.com
- Created a new key pair for the user I will add with the following command on the client (Picture 5: New RSA Key):
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
- After doing this, I opened another terminal on the client, and tested the connection (Picture 2: Initial Ubuntu Connection).
  - ssh -i id\_rsa nsyler@44.208.26.70
- It worked, so I exited out of the other terminal.

## Configuring the Web and Application servers

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
- Set up the configuration for the Gunicorn socket (Picture 3: Gunicorn Config)
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

- Next, I needed to configure Nginx to be able to pass requests to Gunicorn (Picture 4: Nginx Config).
  - sudo vi /etc/nginx/sites-available/my\_site
  - sudo ufw delete allow 8000
  - sudo ufw allow 'Nginx Full'
- I was able to check Nginx for errors with the following command:
  - sudo tail -F /var/log/nginx/error.log
- The folder holding the application root directory and virtual environment root directory is django\_site. The application root directory is stored at ~/home/nsyler/django\_site/my\_site (Picture 9: Application Directory and Nginx var logs)
- The access log files for Nginx can be viewed at /var/log/nginx/access.log (Picture 9: Application Directory and Nginx var logs)
- The error log files for Nginx can be viewed at /var/log/nginx/error.log (Picture 9: Application Directory and Nginx var logs)
- The Nginx process logs can be viewed with journalctl -u nginx (Picture 10: Gunicorn and Nginx Process Logs)
- The application logs for gunicorn can be viewed with journalctl -u gunicorn (Picture 10: Gunicorn and Nginx Process Logs)
- The socket logs for gunicorn can be viewed with journalctl -u gunicorn.socket (Picture 11: Gunicorn Socket Logs)

## MySQL

- I installed the MySQL Client on my machine for database management and the development environment.
  - brew install mysql
  - pip3 install mysql
  - mysql —version to check the installation

- I then created the database in Amazon RDS (Relational Database Services).
  - The options for this are located my default RDS options group (Picture 12: MySQL Options).
- This allowed me to configure parts of the remote database before launching it, including adding an administrative user. However, If someone would like to add an administrator with AWS doing it for them, they could use the following command:
  - CREATE USER 'new\_user'@'localhost' IDENTIFIED BY 'password';
- I would use [https://dev.mysql.com/doc/refman/8.0/en/creating-accounts.html](https://dev.mysql.com/doc/refman/8.0/en/creating-accounts.html) for further information.

- Connected to the MySQL database, and adding a database for the application:
  - mysql -h mysql-dbms.crcyl8xm8erl.us-east-1.rds.amazonaws.com -P 3306 -u adminnsyler -p
  - CREATE DATABASE Blog
- From here, running python3 manage.py makemigrations and python3 manage.py migrate added my designed schema for this app to the database, after setting my hooks in the app's configuration (Picture 13: Models Displaying Schema Configuration).
- The easiest way to start and stop this MySQL Remote Database is through the RDS menu in AWS (Picture 16: AWS MySQL).
- MySQL login, users, and schema snippet: Picture 17: MySQL Info

![](RackMultipart20230721-1-vmnkbr_html_dfb5c81a7775c4e3.png)

_Picture 1: Ubuntu AWS initialization_

![](RackMultipart20230721-1-vmnkbr_html_9af81c901f1c3145.png)

_Picture 2: Initial Ubuntu Connection_

![](RackMultipart20230721-1-vmnkbr_html_72493faaf539e8a1.png)

_Picture 3: Gunicorn Config_

![](RackMultipart20230721-1-vmnkbr_html_6e594e6bdf86dafb.png)

_Picture 4: Nginx Config_

![](RackMultipart20230721-1-vmnkbr_html_4b16a6ef3cb04033.png)

_Picture 5: New RSA Key_

![](RackMultipart20230721-1-vmnkbr_html_4a96b7d26785cc28.png)

_Picture 6: New User Ubuntu_

![](RackMultipart20230721-1-vmnkbr_html_ebfdc161ce99141e.png)

_Picture 7: Public Key added to Ubuntu_

![](RackMultipart20230721-1-vmnkbr_html_d2deffc0ddc6d7a.png)

_Picture 8: Uploading Program with SFTP_

![](RackMultipart20230721-1-vmnkbr_html_4f115290e332233d.png)

_Picture 9: Application Directory and Nginx var logs_

![](RackMultipart20230721-1-vmnkbr_html_c3d2e55f1b2d240d.png)

_Picture 10: Gunicorn and Nginx Process Logs_

![](RackMultipart20230721-1-vmnkbr_html_2346811b045b7ad2.png)

_Picture 11: Gunicorn Socket Logs_

![](RackMultipart20230721-1-vmnkbr_html_c8cfc8844672ca89.png)

_Picture 12: MySQL Options_

![](RackMultipart20230721-1-vmnkbr_html_ec3839947c2b1a8e.png)

_Picture 13: Models Displaying Schema Configuration_

![](RackMultipart20230721-1-vmnkbr_html_89bf9f559ba3f9d5.png)

_Picture 14: Admin Page Overview_

![](RackMultipart20230721-1-vmnkbr_html_8819b7f5195e9157.png)

_Picture 15: Admin Page View for Single Table_

![](RackMultipart20230721-1-vmnkbr_html_db46798ac1b0eb04.png)

_Picture 16: AWS MySQL_

![](RackMultipart20230721-1-vmnkbr_html_13f7ffb27144c8bb.png)

_Picture 17: MySQL Info_

![](RackMultipart20230721-1-vmnkbr_html_f9a15c0e3a3b750e.png)

_Picture 18: Blog Index Page_

# ![](RackMultipart20230721-1-vmnkbr_html_ba0d09f9da9099ec.png)

_Picture 19: Admin Login_

![](RackMultipart20230721-1-vmnkbr_html_d45be1dac3458ca0.png)

_Picture 20: Admin Denied Access Through Port 80_

# ![](RackMultipart20230721-1-vmnkbr_html_28b8b2e91726c500.png)

_Picture 21: Site Denied Access Through Port 8088_

# Conclusion

The internet protocols have truly revolutionized how we connect to the world. The consistency the protocols bring allow users to receive information from around the world. By adhering the http or https protocol, client side browsers can make requests to various servers, and these servers are given tremendous flexibility in how they process the requests. All they have to do is send the response back via https. Whether they are serving static files as a simple webserver, or dynamic files as an application server, or efficiently spreading the load between a variety of different servers, clients and servers are able to communicate everywhere. This is an amazing feat.

# Works Cited

| [1] | Mozilla, "What is a web server?," MDN Web Docs, [Online]. Available: https://developer.mozilla.org/en-US/docs/Learn/Common\_questions/Web\_mechanics/What\_is\_a\_web\_server. [Accessed 26 June 2023]. |
| --- | --- |
| [2] | Real Python, "Web Applications & Frameworks," [Online]. Available: https://docs.python-guide.org/scenarios/web/. [Accessed 26 June 2023]. |
