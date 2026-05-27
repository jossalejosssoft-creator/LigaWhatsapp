import os
import pyobdc
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Conexion Access
ACCESS_PATH = os.getenv("ACCESS_PATH")
conn_access = pyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb *.accdb)}}; DBQ={ACCESS_PATH};")


# Conexion PostgreSQL Railway

conn_pg  = psycopg2.connect (
	host=os.getenv("PGHOST")
	port=os.getenv("PGPORT")
	database=os.getenv("PGDATABASE")
	user=os.getenv("PGUSER")
	password=os.getenv("PGPASSWORD") 
)



@!@#$%%^&*("ACCESS_PATH")

-=_+]][{{}
""

