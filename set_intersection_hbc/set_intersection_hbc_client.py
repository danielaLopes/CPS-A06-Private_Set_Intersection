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
import uuid

# import library in a different directory
import sys
sys.path.append('../')
from multiset_operations import get_polinomial, union, intersection, generate_r, Polynomial
from threshold_paillier import ThresholdPaillier, EncryptedNumber, ThresholdPaillierPublicKey, ThresholdPaillierPrivateKey, combineShares


# Basic Client for socket operations
class Client:

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

    # --------------------- socket-related methods ---------------------
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

    # --------------------- messaging methods ---------------------
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

    def receive_key(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []

        data = self.conn.recv(4096)     
        buffer.append(data.decode('utf-8'))

        self.refreshSocket()
        return buffer

    def receive_encrypted_polinomial(self, n_players):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        message_delimitor = ']}'.encode('utf-8')
        while n_received < n_players:
            # necessary because encrypted polynomials can get quite big
            data = self.conn.recv(4096)  
            if data[-2:] == message_delimitor:
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            else:
                while data[-2:] != message_delimitor:
                    data += self.conn.recv(4096)  
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            n_received += 1
            self.refreshSocket()

        return buffer

# regular version where only client 1 can decrypt
class Set_Intersection_HBC_Client(Client):
    
    # --------------------- paillier serialization methods ---------------------
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

    def serialize_group_encrypted_polinomial(self, toSend):  
        encrypted_polynomial_json = {}
        encrypted_polynomial_json['values'] = [
            (x.c, x.nSPlusOne, x.n) for x in toSend
        ]
        return json.dumps(encrypted_polynomial_json)

    def deserialize_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            paillier.EncryptedNumber(self.public_key, int(x[0]), int(x[1]))
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_group_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            EncryptedNumber(int(x[0]), x[1], x[2])
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_encrypted_polinomial(polynomial)))
        return polynomial_list

    def deserialize_group_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_group_encrypted_polinomial(polynomial)))
        return polynomial_list

    # --------------------- encryption and decryption methods ---------------------
    # only client 1 has private key and decrypts
    def generate_key_pair(self):
        if self.i == 1:
            self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=2048)
            self.broadcast(self.serialize_public_key(self.public_key))
        else:
            self.public_key = self.deserialize_public_key(self.receive_key()[0])

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

    # --------------------- encrypted operation methods ---------------------
    # sum two encrypted polynomials:
    def sum_encrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.sum(polynomial2)

    # multiply an unencrypted polynomial and an encrypted polynomial:
    def multiply_encrypted_unencrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.multiplication(polynomial2)

    # --------------------- protocol methods ---------------------
    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format [0,1,1,2,3]
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.multiset = ast.literal_eval(client_input)
        self.polynomial = get_polinomial(self.multiset)
        self.encrypted_polynomial = self.encrypt_polynomial(self.polynomial)

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            # client 1 is the first to send polynomials   
            self.broadcast(self.serialize_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            print("Waiting to receive encrypted fi from player 1")
            self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            print("Waiting to receive encrypted fi from player 1")
            self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            print("after receiving from player 1")
            self.broadcast(self.serialize_encrypted_polinomial(self.encrypted_polynomial.coefficients))        

    # 1.c)
    def choose_r_polynomials(self):
        self.r_polynomials = []
        for i in (0, self.c): 
            self.r_polynomials.append(generate_r(self.polynomial.degree()))
    
    # 1.d)
    def compute_phi_polynomial(self):
        self.phi_polynomial = self.multiply_encrypted_unencrypted_polynomials(self.encrypted_polynomial, self.r_polynomials[0])
        for i in range(0, len(self.other_polynomials)):
            phi_part = self.multiply_encrypted_unencrypted_polynomials(self.other_polynomials[i], self.r_polynomials[i+1])
            self.phi_polynomial = self.sum_encrypted_polynomials(self.phi_polynomial, phi_part)
    
    # 2. and 3.
    def send_phi_polynomial(self):
        # phi polynomial is already encrypted
        self.lambda_polynomial = self.phi_polynomial
        
        # 2.
        if self.i == 1:         
            # client 1 is the first to send polynomials
            serialized_polynomial = self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients)
            self.broadcast(serialized_polynomial)
            # waits until other client sends him the components of the final lambda polynomial, encrypted
            self.other_lambda_polynomial = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomial = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            self.sum_lambda_phi_polynomials()
            self.send_lambda_polynomial()

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        self.lambda_polynomial = self.sum_encrypted_polynomials(self.other_lambda_polynomial, self.lambda_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        self.send_to_client_1(self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients))

    # 4.
    def send_final_polynomial(self):
        # performed by client 1 only
        self.broadcast(self.serialize_encrypted_polinomial(self.other_lambda_polynomial))

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_intersection_multiset(self):
        if self.i == 1:
            self.final_intersection_polynomial = self.decrypt_polynomial(self.other_lambda_polynomial)
            intersection_els = self.final_intersection_polynomial.get_elements(Counter(self.multiset))
            print("final intersection multiset: " + str(intersection_els))

    def private_set_intersection(self):
        self.generate_key_pair()

        # ----------------- Phase 1 ------------------
        # initiate by player 3, then player 2, then player 1
        self.create_polynomial()
        input("Press enter to exchange encrypted polynomial with other players (order by 2 ,1): ")
        self.send_multiset_polynomial()

        input("Press enter to choose r polynomials and compute phi polynomial (order by 2 ,1): ")
        self.choose_r_polynomials()
        self.compute_phi_polynomial()

        # --------------- Phases 2 + 3 ---------------
        input("Press enter to exchange encrypted lambda with other players (order by 2 ,1): ")
        self.send_phi_polynomial()

        # ----------------- Phase 4 ------------------
        self.get_intersection_multiset()


# regular version where only all clients need to perform group decryption,
# so that no client can obtain more information other than the intersection
# polynomial, like the decryption of fi
class Set_Intersection_HBC_Client_Shared_Key(Client):
    
    # --------------------- paillier serialization methods ---------------------
    def serialize_key_server_request(self):
        toSend_json = {} 
        toSend_json['uuid'] = self.uuid
        toSend_json['i'] = self.i
        toSend_json['n'] = self.n
        return json.dumps(toSend_json)

    def deserialize_shared_keys(self, received):  
        key_dict = json.loads(received)
        
        public_key = key_dict['public_key']
        self.public_key = ThresholdPaillierPublicKey(
                n=int(public_key['n']), nSPlusOne=public_key['nSPlusOne'],
                r=public_key['r'], ns=public_key['ns'], w=public_key['w'],
                delta=public_key['delta'], combineSharesConstant=public_key['combineSharesConstant'])
        
        private_key = key_dict['private_key']
        self.private_key = ThresholdPaillierPrivateKey(
                n=private_key['n'], 
                l=private_key['l'], 
                combineSharesConstant=private_key['combineSharesConstant'],
                w=private_key['w'], 
                v=private_key['v'], 
                viarray=private_key['viarray'], 
                si=private_key['si'],
                server_id=private_key['server_id'],
                r=private_key['r'],
                delta=private_key['delta'],
                nSPlusOne=private_key['nSPlusOne'])

    def serialize_group_encrypted_polinomial(self, toSend):  
        encrypted_polynomial_json = {}
        encrypted_polynomial_json['values'] = [
            (x.c, x.nSPlusOne, x.n) for x in toSend
        ]
        return json.dumps(encrypted_polynomial_json)

    def serialize_share(self, toSend):  
        share_json = {}
        share_json['values'] = [x for x in toSend]
        return json.dumps(share_json)

    def deserialize_group_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            EncryptedNumber(int(x[0]), x[1], x[2])
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_share(self, received):  
        received_dict = json.loads(received)
        values = [x for x in received_dict['values']]
        return Polynomial(values)

    def deserialize_group_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_group_encrypted_polinomial(polynomial)))
        return polynomial_list

    # --------------------- encryption and decryption methods ---------------------
    # pk, sk: paillier key pair
    # all players share sk and perform group decryption
    def generate_shared_key_pair(self):
        if self.i == 1:
            # to tell other players what key group to request
            self.uuid = str(uuid.uuid1())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('127.0.0.1', 9001))
                sock.send(self.serialize_key_server_request().encode('utf-8'))
                data = sock.recv(10248)
                self.deserialize_shared_keys(data.decode('utf-8'))

            self.broadcast(self.uuid)
        else:
            self.uuid = self.receive_key()[0]
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock2:
                sock2.connect(('127.0.0.1', 9002))
                sock2.send(self.serialize_key_server_request().encode('utf-8'))
                data = sock2.recv(10248)
                self.deserialize_shared_keys(data.decode('utf-8'))        

    def encrypt_polynomial(self, polynomial):
        ciphertext = []
        for value in polynomial.coefficients:
            ciphertext.append(self.public_key.encrypt(value))
        return Polynomial(ciphertext)

    def decrypt_part_of_polynomial(self, polynomial, key_part):
        plaintext = []
        for value in polynomial.coefficients:
            plaintext.append(key_part.partialDecrypt(value))
        return Polynomial(plaintext)

    # --------------------- encrypted operation methods ---------------------
    # sum two encrypted polynomials:
    def sum_encrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.encrypted_sum(polynomial2, self.public_key)

    # multiply an unencrypted polynomial and an encrypted polynomial:
    def multiply_encrypted_unencrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.encrypted_multiplication(polynomial2, self.public_key)

    # --------------------- protocol methods ---------------------
    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format [0,1,1,2,3]
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.multiset = ast.literal_eval(client_input)
        self.polynomial = get_polinomial(self.multiset)
        self.encrypted_polynomial = self.encrypt_polynomial(self.polynomial)

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            # client 1 is the first to send polynomials   
            self.broadcast(self.serialize_group_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            print("Waiting to receive encrypted fi from player 1")
            self.other_polynomials = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            print("Waiting to receive encrypted fi from player 1")
            self.other_polynomials = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            print("after receiving from player 1")
            self.broadcast(self.serialize_group_encrypted_polinomial(self.encrypted_polynomial.coefficients))        

    # 1.c)
    def choose_r_polynomials(self):
        self.r_polynomials = []
        for i in (0, self.c): 
            self.r_polynomials.append(generate_r(self.polynomial.degree()))
    
    # 1.d)
    def compute_phi_polynomial(self):
        self.phi_polynomial = self.multiply_encrypted_unencrypted_polynomials(self.encrypted_polynomial, self.r_polynomials[0])
        for i in range(0, len(self.other_polynomials)):
            phi_part = self.multiply_encrypted_unencrypted_polynomials(self.other_polynomials[i], self.r_polynomials[i+1])
            self.phi_polynomial = self.sum_encrypted_polynomials(self.phi_polynomial, phi_part)
    
    # 2. and 3.
    def send_phi_polynomial(self):
        # phi polynomial is already encrypted
        self.lambda_polynomial = self.phi_polynomial
        
        # 2.
        if self.i == 1:         
            # client 1 is the first to send polynomials
            serialized_polynomial = self.serialize_group_encrypted_polinomial(self.lambda_polynomial.coefficients)
            self.broadcast(serialized_polynomial)
            # waits until other client sends him the components of the final lambda polynomial, encrypted
            self.other_lambda_polynomial = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomial = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            self.sum_lambda_phi_polynomials()
            self.send_lambda_polynomial()

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        self.lambda_polynomial = self.sum_encrypted_polynomials(self.other_lambda_polynomial, self.lambda_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        self.send_to_client_1(self.serialize_group_encrypted_polinomial(self.lambda_polynomial.coefficients))

    # 4.
    def send_final_polynomial(self):
        # performed by client 1 only
        self.broadcast(self.serialize_group_encrypted_polinomial(self.other_lambda_polynomial))

    def combine_shares(self, shares):
        final_coefficients = []

        for i in range(0, len(self.other_lambda_polynomial.coefficients)):
            final_coefficients.append(combineShares([shares[0].coefficients[i], shares[1].coefficients[i]], 
                    self.public_key.w, self.public_key.delta, self.public_key.combineSharesConstant, 
                    self.public_key.nSPlusOne, self.public_key.n, self.public_key.ns, [1,2]))

        self.final_intersection_polynomial = Polynomial(final_coefficients)
        print("final intersection polynomial: " + str(self.final_intersection_polynomial))
        #intersection_els = self.final_intersection_polynomial.get_elements_by_roots(Counter(self.multiset))
        intersection_els = self.final_intersection_polynomial.get_elements(Counter(self.multiset))
        print("final intersection multiset: " + str(intersection_els))

    def get_intersection_group_decryption_multiset(self):
        shares = []

        if self.i == 1:
            self.final_polynomial = self.other_lambda_polynomial
            self.broadcast(self.serialize_group_encrypted_polinomial(self.final_polynomial.coefficients))
            shares.append(self.decrypt_part_of_polynomial(self.final_polynomial, self.private_key))
            self.broadcast(self.serialize_share(shares[0].coefficients))
            shares.append(self.deserialize_share(self.receive_encrypted_polinomial(1)[0]))

        elif self.i == 2:
            self.final_polynomial = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            shares.append(self.deserialize_share(self.receive_encrypted_polinomial(1)[0]))
            shares.append(self.decrypt_part_of_polynomial(self.final_polynomial, self.private_key))
            self.broadcast(self.serialize_share(shares[1].coefficients))
        self.combine_shares(shares)

    def private_set_intersection(self):
        self.generate_shared_key_pair()

        # ----------------- Phase 1 ------------------
        # initiate by player 3, then player 2, then player 1
        self.create_polynomial()
        input("Press enter to exchange encrypted polynomial with other players (order by 2 ,1): ")
        self.send_multiset_polynomial()

        input("Press enter to choose r polynomials and compute phi polynomial (order by 2 ,1): ")
        self.choose_r_polynomials()
        self.compute_phi_polynomial()

        # --------------- Phases 2 + 3 ---------------
        input("Press enter to exchange encrypted lambda with other players (order by 2 ,1): ")
        self.send_phi_polynomial()

        # ----------------- Phase 4 ------------------
        input("Press enter to perform group decryption (order by 2 ,1): ")
        self.get_intersection_group_decryption_multiset()

def main():
    
    description = 'Welcome to the Set Intersection Client!\n\
    Experiment this protocol with 2 clients and no Trusted Third Party.\n'

    usage = '\n\
    python set_intersection_client.py <command> [<args>]\n\
    python set_intersection_client.py single_key "<i>" "<n>" "<c>"\n\
    python set_intersection_client.py shared_key "<i>" "<n>" "<c>"'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['single_key','shared_key'])
    parser.add_argument('i', type=int)
    parser.add_argument('n', type=int)
    parser.add_argument('c', type=int)

    args = parser.parse_args()

    if args.command.__eq__('single_key'):
        client = Set_Intersection_HBC_Client(args.i, args.n, args.c)
    elif args.command.__eq__('shared_key'):
        client = Set_Intersection_HBC_Client_Shared_Key(args.i, args.n, args.c)
    else:
        parser.error('wrong command')

    client.private_set_intersection()

if __name__ == "__main__":
    main()