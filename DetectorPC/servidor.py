#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
from Detector import inicializar,procesar

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind the socket to the port
server_address = ('localhost', 10000)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

#AQUI CARGAR VARIABLES
diagnosticos = inicializar()


while True:
    # Wait for a connection
    print ('waiting for a new connection -------------------------------------------------------------------')
    connection, client_address = sock.accept()
    try:
        print ('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        informe = str()
        while True:
            data = connection.recv(4096)
            # print ('received "%s"' % data.decode('utf-8'))
            informe += data.decode('utf-8')
            if (('|' in informe) and (len(informe)>3)):
                informe = procesar(informe[:-1],diagnosticos)
                # print (informe)
            if data:
                print ('sending response to the client')
                connection.sendall(bytes(informe,'utf-8'))
            else:
                print ('no more data from', client_address)
                break

        #IMPRIMIR RESULTADO


    finally:
        # Clean up the connection
        connection.close()
