#!/usr/bin/env python
# -*- coding: utf-8 -*-

def eliminarAcentos(cadena):
     d = {'\xc1':'A',
         '\xc9':'E',
         '\xcd':'I',
         '\xd3':'O',
         '\xda':'U',
         '\xdc':'U',
         '\xd1':'N',
         '\xc7':'C',
         '\xed':'i',
         '\xf3':'o',
         '\xf1':'n',
         '\xe7':'c',
         '\xba':'',
         '\xb0':'',
         #'\x3a':'',
         '\xb4':'',
         '\xe1':'a',
         '\xe2':'a',
         '\xe3':'a',
         '\xe4':'a',
         '\xe5':'a',
         '\xe8':'e',
         '\xe9':'e',
         '\xea':'e',
         '\xeb':'e',
         '\xec':'i',
         '\xed':'i',
         '\xee':'i',
         '\xef':'i',
         '\xf2':'o',
         '\xf3':'o',
         '\xf4':'o',
         '\xf5':'o',
         '\xf0':'o',
         '\xf9':'u',
         '\xfa':'u',
         '\xfb':'u',
         '\xfc':'u',
         '\xe5':'a'}

     nueva_cadena = cadena
     for c in d.keys():
         nueva_cadena = nueva_cadena.replace(c,d[c])

     auxiliar = nueva_cadena.encode('utf-8')
     return nueva_cadena


import socket
import sys

informe = sys.argv[1]
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
# print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    # Send data
    message = eliminarAcentos(informe)
    #print (message)
    #print (bytes(message,'utf-8'))
    #print ('<b>sending</b> "%s"' % message)
    sock.sendall(bytes(message,'utf-8'))
    # Look for the response
    data = sock.recv(4096)
    print (data.decode('utf-8'))

finally:
    # print ('closing socket')
    sock.close()
