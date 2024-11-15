import mysql.connector #DATABASE TEAM: to install: (pip install mysql-connector-python)
from flask import g
import mysql.connector

#DATABASE TEAM: here I tried to connect to mysql, but haven't done that properly

#DATABASE TEAM: this can be all changed, it is for now to let me start the web page
#Please get some basic database ready so I can start debugging the webpage
#for now the sign up takes only username and password

def connect_to_Database():
  sql = mysql.connect('path') #DATABASE TEAM: here proper path needs to be stored
  sql.row_factory = mysql.Row
  return mysql

##### this part I'm not sure if we need it
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
)
####
def get_database():
  if not hasattr(g, 'databasename_db'):
    g.databasename_db = connect_to_Database()
  return g.databasename_db

print(mydb)

