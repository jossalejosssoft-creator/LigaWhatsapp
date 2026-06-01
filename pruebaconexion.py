import socket
import sys

host = "kodama.proxy.rlwy.net"
port = 30185

print (f"probando conexion a  {host} : {port} ...")
sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.settimeout(5)


result = sock.connect_ex((host,port))

if result == 0:
    print ("puesrto 5432 abierto. railway responde")
else :
    print("timeout. firewall o red bloqueando el puerto")

sock.close()