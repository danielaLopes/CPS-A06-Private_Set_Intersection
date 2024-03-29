#!/usr/bin/python3
import socket
import json
import argparse
from argparse import RawTextHelpFormatter
import os
import ast 
from collections import Counter
import phe
from phe import paillier

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection, generate_r, Polynomial


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
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sockets.append(sock)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', self.port))
                self.socket = sock

    def refreshSockets(self):
        for sock in self.sockets:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def refreshSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port))
        self.socket = sock

    def connectSockets(self):
        for (sock,port) in zip(self.sockets,self.other_ports):
            sock.connect(('127.0.0.1', port))

    def acceptConnections(self):
        self.socket.listen(5)
        self.conn, addr = self.socket.accept()

    def broadcast(self, toSend):      
        for sock in self.sockets:
            try:
                sock.send(toSend.encode("utf-8"))
            except:
                self.connectSockets()
                sock.send(toSend.encode("utf-8"))

    def send_to_client_1(self, toSend):
        try:
            self.sockets[0].send(toSend.encode("utf-8"))
        except:
            self.connectSockets()
            self.sockets[0].send(toSend.encode("utf-8"))

    def receive(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        while n_received < self.n-1:
            data = self.conn.recv(4096)     
            buffer.append(Polynomial(ast.literal_eval(data.decode('utf-8'))))
            n_received += 1

        self.refreshSocket()
        return buffer

    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format "[0,1,1,2,3]"
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.multiset = ast.literal_eval(client_input)
        self.polynomial = get_polinomial(self.multiset)

    """
    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            self.connectSockets()
            # client 1 is the first to send polynomials
            self.broadcast(str(self.polynomial.coefficients))
            self.acceptConnections()
            self.other_polynomials = self.receive()   
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.acceptConnections()
            self.other_polynomials = self.receive()
            self.connectSockets()
            self.broadcast(str(self.polynomial.coefficients))"""

    # 1.c)
    def choose_r_polynomials(self):
        self.r_polynomials = []
        self.r_polynomials.append(generate_r(self.polynomial.degree()))
    
    # 1.d)
    def compute_phi_polynomial(self):
        # TODO: this is wrong
        # calculate this client phi part: phi_i = f_i * r_i,0
        self.phi_polynomial = self.polynomial.multiplication(self.r_polynomials[0])
        if len(self.r_polynomials) > 1:
            for (r, f) in (self.r_polynomials[1: ], self.other_polynomials):
                self.phi_polynomial = f.multiplication(r)

    # 2. and 3.
    def send_phi_polynomial(self):
        # 2.
        if self.i == 1:
            # client 1 is the first to send polynomials
            self.broadcast(str(self.phi_polynomial.coefficients))
            # waits until other client sends him the final lambda polynomial
            self.other_lambda_polynomials = self.receive()
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomials = self.receive()
            self.sum_lambda_phi_polynomials()
            # TODO: change this in case of more clients
            #self.broadcast(str(self.lambda_polynomial.coefficients))
            self.send_lambda_polynomial()

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        self.lambda_polynomial = self.other_lambda_polynomials[0].sum(self.phi_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        self.refreshSockets()
        # performed by client 2 only
        self.send_to_client_1(str(self.lambda_polynomial.coefficients))

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_client_intersection_elements(self):
        if self.i == 1:
            intersection_els = self.other_lambda_polynomials[0].get_elements(Counter(self.multiset))
            print("final intersection multiset: " + str(intersection_els))

    def private_set_intersection(self):
        # ----------------- Phase 1 ------------------
        self.create_polynomial()
        #client.send_multiset_polynomial()

        input("Press enter to compute phi polynomial: ")
        self.choose_r_polynomials()
        self.compute_phi_polynomial()

        # --------------- Phases 2 + 3 ---------------
        input("Press enter to exchange phi and lambda polynomials: ")
        self.send_phi_polynomial()

        # ----------------- Phase 4 ------------------
        self.get_client_intersection_elements()


# Encrypted version
class Encrypted_Set_Intersection_Client(Set_Intersection_Client):

    def __init__(self, i, n, c):
        super(Encrypted_Set_Intersection_Client, self).__init__(i, n, c)

    def receive_key(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        while n_received < self.n-1:
            data = self.conn.recv(4096)     
            buffer.append(data.decode('utf-8'))
            n_received += 1

        self.refreshSocket()
        return buffer

    def receive_encrypted_polinomial(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        message_delimitor = ']]}'.encode('utf-8')
        while n_received < self.n-1:
            # necessary because encrypted polynomials can get quite big
            data = self.conn.recv(4096)  
            if data[-3:] == message_delimitor:
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            else:
                while data[-3:] != message_delimitor:
                    data += self.conn.recv(4096)  
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            n_received += 1

        self.refreshSocket()
        return buffer

    def serialize_public_key(self, toSend):  
        toSend_json = {} 
        toSend_json['public_key'] = {'n': self.public_key.n}
        return json.dumps(toSend_json)

    def deserialize_public_key(self, received):  
        key_dict = json.loads(received)
        public_key = key_dict['public_key']
        return paillier.PaillierPublicKey(n=int(public_key['n']))

    def serialize_encrypted_polinomial(self, toSend):  
        encrypted_polynomial_json = {}
        encrypted_polynomial_json['values'] = [
            (str(x.ciphertext()), x.exponent) for x in toSend
        ]
        return json.dumps(encrypted_polynomial_json)

    def deserialize_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            paillier.EncryptedNumber(self.public_key, int(x[0]), int(x[1]))
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_encrypted_polinomial(polynomial)))
        return polynomial_list

    def encrypt_polynomial(self, polynomial):
        ciphertext = []
        for value in polynomial.coefficients:
            ciphertext.append(self.public_key.encrypt(value))
        return Polynomial(ciphertext)

    def decrypt_polynomial(self, polynomial):
        plaintext = []
        for value in polynomial.coefficients:
            plaintext.append(self.private_key.decrypt(value))
        return Polynomial(plaintext)

    def sum_encrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.sum(polynomial2)

    def generate_key_pair(self):
        # only client 1 has private key
        if self.i == 1:
            self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=2048)
            self.broadcast(self.serialize_public_key(self.public_key))
        else:
            self.public_key = self.deserialize_public_key(self.receive_key()[0])

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_client_intersection_elements(self):
        if self.i == 1:
            intersection_els = self.other_lambda_polynomials[0].get_elements(Counter(self.multiset))
        else:
            intersection_els = self.lambda_polynomial.get_elements(Counter(self.multiset))
        print("final intersection multiset: " + str(intersection_els))

    # 2. and 3.
    def send_phi_polynomial(self):
        # encrypt phi polynomial to send to other players
        self.lambda_polynomial = self.encrypt_polynomial(self.phi_polynomial)
        
        # 2.
        if self.i == 1:         
            # client 1 is the first to send polynomials
            serialized_polynomial = self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients)
            self.broadcast(serialized_polynomial)
            # waits until other client sends him the components of the final lambda polynomial, encrypted
            print("waiting for other lambda polynomials...")
            self.other_lambda_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial())
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial())
            self.sum_lambda_phi_polynomials()
            self.send_lambda_polynomial()

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        # TODO: change for more clients
        self.lambda_polynomial = self.other_lambda_polynomials[0].sum(self.lambda_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        self.send_to_client_1(self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients))

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_client_intersection_elements(self):
        if self.i == 1:
            self.decrypted_final_polynomial = self.decrypt_polynomial(self.other_lambda_polynomials[0])
            intersection_els = self.decrypted_final_polynomial.get_elements(Counter(self.multiset))
            print("final intersection multiset: " + str(intersection_els))

    def private_set_intersection(self):
        self.generate_key_pair()

        # ----------------- Phase 1 ------------------
        self.create_polynomial()
        #client.send_multiset_polynomial()

        input("Press enter to compute phi polynomial: ")
        self.choose_r_polynomials()
        self.compute_phi_polynomial()

        # --------------- Phases 2 + 3 ---------------
        input("Press enter to exchange phi and lambda polynomials: ")
        self.send_phi_polynomial()

        # ----------------- Phase 4 ------------------
        self.get_client_intersection_elements()


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

    client.private_set_intersection()


if __name__ == "__main__":
    main()