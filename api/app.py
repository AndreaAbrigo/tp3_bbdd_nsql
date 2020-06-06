import os
import redis
from flask import Flask, request
from flask import render_template
import re
import json
from urllib import urlopen

app = Flask(__name__)


url = 'http://ipinfo.io/json'
response = urlopen(url)
geo = json.load(response)
ubi=geo['loc']


def connect_db():
    conexion = redis.StrictRedis(os.environ['DB_PORT_6379_TCP_ADDR'], port=6379, db=0)
    return conexion

def obtener_ubicacion():
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    geo = json.load(response)
    ubi=geo['loc']
    return(ubi)
    
@app.route('/')
def todo():
    return render_template('/todo.html')

@app.route('/prueba')
def prueba():
    ubicacion=obtener_ubicacion()
    return ubicacion
    

@app.route('/cargarGrupo')
def cargarGrupo():
    conexion = connect_db()
    ubicacion=obtener_ubicacion()
    coordenadas=ubicacion.split(",")
    latitud=coordenadas[0]
    longitud=coordenadas[1]
    conexion.geoadd('cervecerias', '-58.233851', '-32.480258', 'Drakkar', '-58.237062', '-32.484577','Bigua', '-58.238009', '-32.480966','Tractor', '-58.235332', '-32.479629','7 colinas', '-58.232669', '-32.481815', 'Ambar', longitud, latitud, 'here')
    conexion.geoadd('universidades', '-58.2333326', '-32.479067', 'UADER FCyT', '-58.2320773','-32.4806146','UCU', '-58.2593929', '-32.4826601', 'UNER Salud', '-58.2379138', '-32.4838185','UNER Rectorado', '-58.2343733', '-32.4925787', 'UTN', longitud, latitud, 'here')
    conexion.geoadd('farmacias', '-58.2327425', '-32.4849769', 'Alberdi', '-58.2327425','-32.4849769', 'Argentina', '-58.2327425', '-32.4849769', 'Popular','-58.2327425', '-32.4849769', 'Central', '-58.2327425', '-32.4849769', 'Don Bosco', '-58.2327425', '-32.4849769', 'Ramirez', longitud, latitud, 'here')
    conexion.geoadd('emergencias', '-58.2322039', '-32.4830237', 'Vida', '-58.2356908', '-32.4831685', 'Alerta', '-58.2312003', '-32.4832777', 'Clinica', '-58.2389064', '-32.479766', 'Cooperativa', longitud, latitud, 'here')
    conexion.geoadd('supermercados', '-58.2360203', '-32.4839382','Supremo', '-58.2341428', '-32.4872144', 'GranRex', '-58.2411165', '-32.4877664', 'Dia', '-58.240505', '-32.4828247', 'Estrella','-58.240505', '-32.4828247', 'Guri', '-58.240505', '-32.4828247', 'RT',  '-58.240505', '-32.4828247','Impulso', longitud, latitud, 'here')
    return "hecho"

@app.route('/cargarLugar', methods=["POST"])
def cargarLugar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        titulo = request.form['titulo']
    temp = len(nombre)
    titulo = nombre[:temp - 1]
    return render_template('/cargarLugar.html', nombre=nombre, titulo=titulo)

@app.route('/nuevoLugar', methods=["POST"])
def nuevoLugar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        titulo = request.form['titulo']
        lugar = request.form['lugar']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
    conexion = connect_db()
    conexion.geoadd(nombre, longitud, latitud, lugar)
    return render_template('/cargado.html', nombre=nombre, lugar=lugar)

@app.route('/listarLugares', methods=["POST"])
def listarLugares():
    conexion = connect_db()
    aux = []
    lug = []
    lugares = []
    ubicacion=obtener_ubicacion()
    coordenadas=ubicacion.split(",")
    latitud=coordenadas[0]
    longitud=coordenadas[1]
    if request.method == 'POST':
        nombre = request.form['nombre']
    aux = str(conexion.georadius(nombre,longitud,latitud,'100','km'))
    aux=aux.replace("[",'')
    aux=aux.replace("]",'')
    aux=aux.replace("'", '')
    aux=aux.replace("b", '')
    aux=aux.lstrip()
    lugares = aux.split(",")
    for lugar in lugares:
        lug.append(lugar.lstrip())
    titulo = nombre.capitalize()
    return render_template('/listarLugares.html',lugares=lug, nombre=nombre, titulo=titulo)

@app.route('/lugaresCerca', methods=["POST"])
def lugaresCerca():
    lug = []
    if request.method == 'POST':
        nombre = request.form['nombre']
    conexion = connect_db()
    ubicacion=obtener_ubicacion()
    coordenadas=ubicacion.split(",")
    latitud=coordenadas[0]
    longitud=coordenadas[1]
    aux = str(conexion.georadius(nombre,longitud,latitud,'5','km')) 
    aux=aux.replace("[",'')
    aux=aux.replace("]",'')
    aux=aux.replace("'", '')
    aux=aux.replace("b", '')
    lugares = aux.split(",")
    for lugar in lugares:
        lug.append(lugar.lstrip())
    titulo = nombre.capitalize()
    return render_template('/lugaresCerca.html',lugares=lug, nombre=nombre, titulo=titulo)

@app.route('/devolverDistancia', methods=["POST"])
def devolverDistancia():
    if request.method == 'POST':
        nombre = request.form['nombre']
        lugar = request.form['lugar']
    aux = []
    conexion = connect_db()
    aux = str(conexion.geodist(nombre,"here", lugar, 'm'))
    return render_template('/devolverDistancia.html', dato = aux, lugar = lugar, nombre=nombre)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
