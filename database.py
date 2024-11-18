import mysql.connector
from flask import g
import mysql.connector
from credentials import HOST, USER, PASSWORD, DATABASE

def connect_to_database():
  mydb = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE,
  )
  return mydb

def get_database():
  if not hasattr(g, 'databasename_db'):
    g.databasename_db = connect_to_database()
  return g.databasename_db


