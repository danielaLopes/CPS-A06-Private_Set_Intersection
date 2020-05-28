#!/usr/bin/python3
import socket
import json
#import urllib.request
#import urllib.parse
import argparse
from argparse import RawTextHelpFormatter
import os
import ast 

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection


# Non-Encrypted version
class Set_Intersection_Client:

    def __init__(self, i, n, c):
        self.i = i
        self.n = n
        self.c = c
        self.port = 8000 + i

        self.other_ports= []
        self.sockets = []
        for client_id in range(1, self.n + 1):
            if client_id != self.i:
                self.other_ports.append(8000 + client_id)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #sock.connect(('127.0.0.1', 8000 + client_id))
                self.sockets.append(sock)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
                sock.bind(('127.0.0.1', self.port))
                self.socket = sock

    def broadcast(self, toSend):
        for (sock,port) in zip(self.sockets,self.other_ports):
            sock.connect(('127.0.0.1', port))
            sock.send(toSend.encode("utf-8"))

    def receive(self):
        self.socket.listen(5)
        print("waiting to receive data...")
        #try:
        conn, addr = self.socket.accept()
        #except KeyboardInterrupt:
            #print("exiting")
            #os._exit()  
        n_received = 0
        buffer = []

        while n_received < self.n-1:
            data = conn.recv(4096)     
            buffer.append(Polynomial(ast.literal_eval(data.decode('utf-8'))))
            n_received += 1
        return buffer

    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format "[0,1,1,2,3]"
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.polynomial = get_polinomial(map(int, client_input.strip('[]').split(',')))

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            # client 1 is the first to send polynomials
            self.broadcast(str(self.polynomial.coefficients))
            self.other_polynomials = self.receive()   
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_polynomials = self.receive()
            self.broadcast(str(self.polynomial.coefficients))

        print("self.other_polynomials: " + str(self.other_polynomials))


    # 1.c)
    def choose_r_polynomials(self):
        # TODO: i dont know how to do this
        self.r_polynomials = []
        #for i in (0, self.c):
        self.append(get_polinomial([0,0]))
        #self.append(get_polinomial([1,1]))
    
    # 1.d)
    def compute_phi_polynomial(self):
        # TODO: this is wrong
        for r in self.r_polynomials:
            self.phi_polynomial = .multiplication(r)

    # 2. and 3.
    def send_phi_polynomial(self):
        # 2.
        if self.i == 1:
            # client 1 is the first to send polynomials
            self.broadcast(str(self.phi_polynomial.coefficients))
            self.other_lambda_polynomials = self.receive()
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_phi_polynomials = self.receive()
            self.sum_lambda_phi_polynomials()
            # TODO: change this in case of more clients
            self.broadcast(str(self.phi.coefficients))

        print("self.other_phi_polynomials: " + str(self.other_phi_polynomials))

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        self.lambda_polynomial = self.other_lambda_polynomial.sum(self.phi_polynomial)
    # 3.c)
    def send_phi_polynomial(self):
            



# Encrypted version
class Encrypted_Set_Intersection_Client(Set_Intersection_Client):

    def __init__(self, i, n, c):
        super(Encrypted_Set_Intersection_Client, self).__init__(i, n, c)
        print(self.i)


def main():
    
    description = 'Welcome to the Set Intersection Client!\n\
    Experiment this protocol with 2 clients and no Trusted Third Party.\n\
    1. Choose between encrypted and non-encrypted client version and give parameters to create client.\n\
    2. Submit a multiset.\n'

    usage = '\n\
    python set_intersection_client.py <command> [<args>]\n\
    python set_intersection_client.py non_encrypted "<i>" "<n>" "<c>"\n\
    python set_intersection_client.py encrypted "<i>" "<n>" "<c>"'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['non_encrypted', 'encrypted'])
    parser.add_argument('i', type=int)
    parser.add_argument('n', type=int)
    parser.add_argument('c', type=int)

    args = parser.parse_args()

    if args.command.__eq__('non_encrypted'):
        client = Set_Intersection_Client(args.i, args.n, args.c)
    elif args.command.__eq__('encrypted'):
        client = Encrypted_Set_Intersection_Client(args.i, args.n, args.c)
    else:
        parser.error('wrong command')

    client.create_polynomial()
    input("Press enter to continue: ")
    client.send_multiset_polynomial()

    input("Press enter to continue: ")
    client.choose_r_polynomials()
    client.compute_phi_polynomial()

    input("Press enter to continue: ")
    client.send_phi_polynomial()

if __name__ == "__main__":
    main()