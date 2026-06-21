import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
from dotenv import load_dotenv

from groq import Groq



load_dotenv()
app = Flask(__name__)

# variables de entorno
DATABASE_URL = os.environ['DATABASE_URL']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
#MUSE_API_KEY = os.environ.get('MUSE_API_KEY', 'MOCK')

#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ai_to_sql(pregunta_usuario):
    """
    Convierte lenguaje natural a SQL
    """

   
        
    # aqui va el codigo real con muse spark - lo activamos cuando tengas la key
    # por ahora no se ejecuta por que estamos en MOCK

    prompt = f"""Eres un experto en PostgrSQL para una liga de futbol infantil en Mexico. Convierte esta pregunta a SQL
    Tablas disponibles: equipos (id_equipo,nombre_equipo,grupo,id_categoria)
            jugadores (id_jugador,nombre,id_equipo)
            categorias(id_categorias, nombre_categoria)

    id_categoria en la tabla equipos es la llave foranea que la relaciona con la tabla categorias
    id_equipo en la tabla jugadores es la llave foranea que la relaciona con la tabla equipos     

    Devuelve solo el SQL, sin explicaciones ni markdown
    Usa ILIKE '%texto%' para buscar equipos sin importar mayusculas
    si no entiendes la pregunta regresa: SELECT 'No entendi la pregunta' as mensaje;

    pregunta: {pregunta_usuario}
    SQL:
    """
    
    
    try:

        resp= client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user", "content":prompt}],
            temperature= 0,
            max_tokens=200
        )
        sql = resp.choices[0].message.content.strip()
        sql = sql.replace("```sql","").replace("```","").strip()
        print(f"Pregunta: {pregunta_usuario} | SQL: {sql}")
        return sql
    except Exception as e:
        print(f"Error OpenAI detallado: {type(e).__name__}: {e}")
        return "SELECT 'Error conectando con la IA' as error"

def ejecutar_sql(query):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(query)

        # si no hay resultados que devolver
        if cur.description is None:
            conn.commit()
            cur.close()
            conn.close()
            return "Consulta ejecutada"
        
        columnas = [desc[0] for desc in cur.description]
        filas = cur.fetchall()
        cur.close()
        conn.close()

        if not filas:
            return "No hay datos para mostrar"
        
        # Formatear respuesta para whatsapp
        respuesta = ""
        for fila in filas[:15]: # Max 15 filas para no saturar whastapp
            linea = " | ".join(str(campo) for campo in fila)
            respuesta += linea + "\n"
        return respuesta.strip()
    except Exception as e:
        return f"Error en BD: {str(e)}"

    
@app.route("/whatsapp", methods = ['POST'])
def whatsapp():
    mensaje_entrante = request.values.get('Body','').strip()
    numero_usuario = request.values.get('From','')

    print (f"Mensaje de {numero_usuario}:{mensaje_entrante}")

    sql = ai_to_sql(mensaje_entrante)
    print(f"SQL generado: {sql}")

    resultado = ejecutar_sql(sql)
    print(f"Resultado: {resultado}")

    resp = MessagingResponse()
    resp.message(resultado)

    return str(resp)
@app.route("/", methods=['GET'])
def home():
    return "Bot Liga WhatsApp activo. MODO: " + ("MOCK" if MUSE_API_KEY == 'MOCK' else "PROD")

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port=int(os.environ.get('PORT',5000)))