#!/usr/bin/python3
import http.server
from http.server import BaseHTTPRequestHandler
import urllib.parse
import socketserver
import json
from collections import Counter
import ast

from multiset_operations import polynomial_union, polynomial_intersection

_multiset1 = ""
_multiset2 = ""


class RequestHandler(BaseHTTPRequestHandler):  

    # computes UNION and INTERSECTION requests
    def do_GET(self):
        global _multiset1 
        global _multiset2
        print("Received GET request for " + self.path) 
        operation = urllib.parse.urlparse(self.path).path

        if _multiset1 != "" and _multiset2 != "": 

            list_multiset1 = ast.literal_eval(_multiset1)
            list_multiset2 = ast.literal_eval(_multiset2)

            if operation == "/union":         
                result = polynomial_union(list_multiset1, list_multiset2)
                union_multiset = result.get_elements(Counter(list_multiset1 + list_multiset2))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(union_multiset).encode())
            elif operation == "/intersection":  
                result = polynomial_intersection(list_multiset1, list_multiset2)
                intersection_multiset = result.get_elements(Counter(list_multiset1))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(intersection_multiset).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Requires a multiset from each client!')
            print("Operation cannot be performed! Requires a multiset from each client!")


    # computes SUBMIT
    def do_POST(self):
        global _multiset1 
        global _multiset2

        print("Received POST request for a SUBMIT")
        content_len = int(self.headers.get('Content-Length'))
        json_body = self.rfile.read(content_len)
        json_body_decoded = json_body.decode("utf-8")
        json_multiset = json.loads(json_body_decoded)
        
        if _multiset1 != "" and _multiset2 != "":
            # resets multisets for next round
            _multiset1 = ""
            _multiset2 = ""
        if _multiset1 != "":
            _multiset2 = json_multiset["multiset"]
        else:
            _multiset1 = json_multiset["multiset"]

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Submit successful!')
        print("SUBMIT successful")


def main():
    PORT = 8000

    httpd = socketserver.TCPServer(('localhost', PORT), RequestHandler)

    print("Trusted Third Party serving at port " + str(PORT))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()


if __name__ == "__main__":
    main()