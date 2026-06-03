import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# vartiables de entorno
DATABASE_URL = os.environ['DATABASE_URL']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
MUSE_API_KEY = os.environ.get('MUSE_API_KEY', 'MOCK')


def ai_to_sql(pregunta_usuario):
    """
    Convierte lenguaje natural a SQL
    MODO MOCK: devuelve queries de ejemplo para que pruebes el flujo sin API key
    """

    if MUSE_API_KEY == 'MOCK':
        # queries de ejemplo para probar
        pregunta = pregunta_usuario.lower()
        if 'equipos' in pregunta :
            return "SELECT nombre_equipo FROM equipos ORDER BY nombre_equipo DESC LIMIT 10;"
        elif 'jugador' in pregunta or 'jugadores' in pregunta:
             return "SELECT id_jugador, nombre FROM jugadores ORDER BY nombre DESC LIMIT 15;"
        else:
            return  "SELECT 'Escribe: tabla infantil, tabla juvenil o goleadores' as mensaje;"
        
    # aqui va el codigo real con muse spark - lo activamos cuando tengas la key
    # por ahora no se ejecuta por que estamos en MOCK

    prompt = f

    """
    Eres un experto en PostgrSQL. Convierte esta pregunta a SQL
    Tablas: tabla_infantil (equipo,pj,pg,pe,pp,gf,gc,dg,puntos)
            tabla_juvenil (equipo,pj,pg,pe,pp,gf,gc,dg,puntos)
            goleadores(jugador, equipo, goles)

    pregunta: {pregunta_usuario}
    Devuelve solo el SQL, sin explicaciones ni markdown
    """
    headers = {
        "Authorization": f"Bearer {MUSE_API_KEY}",
        "Content-Type": "application/json"

    }
    data  = {
        "model": "muse-spark",
        "messages": [{"role":"user", "content":prompt}],
        "temperature": 0.1
    }
    
    try:
        res = request.post(
            "https://api.llama.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
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
@app.route("/", methods['GET'])
def home():
    return "Bot Liga WhatsApp activo. MODO: " + ("MOCK" if MUSE_API_KEY == 'MOCK' else "PROD")

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port=int(os.environ.get('PORT',5000)))