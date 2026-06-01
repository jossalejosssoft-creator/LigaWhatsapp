import os
import pyodbc
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
#print(os.getenv("ACCESS_PATH"))

#print(pyodbc.drivers())

# Conexion Access
ACCESS_PATH = os.getenv("ACCESS_PATH")
conn_access = pyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}}; DBQ={ACCESS_PATH};")

# Conexion PostgreSQL Railway

conn_pg  = psycopg2.connect(
	host=os.getenv("PGHOST"),
	port=os.getenv("PGPORT"),
	database=os.getenv("PGDATABASE"),
	user=os.getenv("PGUSER"),
	password=os.getenv("PGPASSWORD") 
)

cur_access = conn_access.cursor()
cur_pg = conn_pg.cursor()

def crear_esquema():
    cur_pg.execute("""
    CREATE TABLE IF NOT EXISTS equipos(
                   id_equipo SERIAL PRIMARY KEY,
                   nombre_equipo VARCHAR(100),
                   grupo INT,
                   id_categoria INT

                   );
                   
    CREATE TABLE IF NOT EXISTS jugadores(
                   id_jugador SERIAL PRIMARY KEY,
                   nombre VARCHAR(100),
                   grupo INT,
                   id_categoria INT

                   );

    CREATE TABLE IF NOT EXISTS categorias(
                   id_categoria SERIAL PRIMARY KEY,
                   nombre_categoria VARCHAR(100)

                   );

    CREATE TABLE IF NOT EXISTS equipos2(
                   id_equipo BIGINT PRIMARY KEY,
                   nombre_equipo VARCHAR(100),
                   grupo VARCHAR(100)
                   );
                   
                   
                   """)
    conn_pg.commit()
    print("Esquema posatrgess listo")

def migrar_tabla(tabla_access, tabla_pg, columnas_access, columnas_pg):
    cur_pg.execute (f"TRUNCATE TABLE {tabla_pg} RESTART IDENTITY CASCADE;")
    cur_access.execute (f"SELECT {','.join(columnas_access)} FROM {tabla_access}")
    rows = cur_access.fetchall()
    if rows:
        args_str = ','.join(cur_pg.mogrify(f"({','.join(['%s']*len(columnas_pg))})",row).decode('utf-8')for row in rows)
        cur_pg.execute(f"INSERT INTO {tabla_pg} ({','.join(columnas_pg)}) VALUES {args_str}")
    conn_pg.commit()
    print(f" {tabla_pg.capitalize()}: {len(rows)} registros sincronizados")

def main():
    print ("Iniciando sincronizacion Access -> PostgreSQL...")
    crear_esquema()
    migrar_tabla ("Equipos", "equipos2", ["IdEquipo", "NombreEquipo", "Grupo", "IdCategoria"], ["id_equipo", "nombre_equipo", "grupo", "id_categoria"])
    migrar_tabla ("Equipos", "equipos2", ["IdEquipo", "NombreEquipo", "Grupo", "IdCategoria"], ["id_equipo", "nombre_equipo", "grupo", "id_categoria"])
    migrar_tabla ("Jugadores", "jugadores", ["IdJugador", "Nombre"], ["id_jugador", "nombre"])
    migrar_tabla ("Categorias", "categorias", ["IdCategoria", "NombreCategoria"], ["id_categoria", "nombre_categoria"])
    # migrar_tabla ("Jugadores", "jugadores", ["IdJugador", "Nombre"], ["id_jugador", "nombre"])

    print ("Sincronizacion completa")
    cur_access.close()
    cur_pg.close()
    conn_access.close()
    conn_pg.close()

if __name__ == "__main__":
    main()