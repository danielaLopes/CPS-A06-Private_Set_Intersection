#!/usr/bin/python3
import http.server
from http.server import BaseHTTPRequestHandler
import urllib.parse
import socketserver
import json
from collections import Counter

from multiset_operations import union
from multiset_operations import intersection


_multiset1 = ""
_multiset2 = ""


class RequestHandler(BaseHTTPRequestHandler):  

    # computes UNION and INSTERSECTION requests
    def do_GET(self):
        global _multiset1 
        global _multiset2
        print("Received GET request for " + self.path) 
        operation = urllib.parse.urlparse(self.path).path
        query = urllib.parse.urlparse(self.path).query
        print("operation " + operation)
        print("query " + query) 

        if _multiset1 != "" and _multiset2 != "": 

            print("_multiset1: " + _multiset1)
            print("_multiset2: " + _multiset2)
            
            value = query.split("=")[1]
            print("value " + value) 

            map_multiset1 = map(int, _multiset1.strip('[]').split(','))
            map_multiset2 = map(int, _multiset2.strip('[]').split(','))

            if operation == "/union":         
                result = union(map_multiset1, map_multiset2, int(value))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(result).encode())
            elif operation == "/intersection":  
                result = intersection(map_multiset1, map_multiset2, int(value))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(result).encode())
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
            print("reset")
            _multiset1 = ""
            _multiset2 = ""
        if _multiset1 != "":
            _multiset2 = json_multiset["multiset"]
        else:
            _multiset1 = json_multiset["multiset"]

        print("_multiset1:" + _multiset1)
        print("_multiset2:" + _multiset2)

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