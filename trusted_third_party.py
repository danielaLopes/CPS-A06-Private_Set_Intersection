#!/usr/bin/python3
import SimpleHTTPServer
import SocketServer
from collections import Counter

def get_polinomial(multiset, x):
    counter_multiset = Counter(multiset)
    for key, value in counter_multiset:
        print("key: " + key)
        print("value: " + value)

class UnionHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


def main():
    PORT = 8000

    httpd = SocketServer.TCPServer(('localhost', PORT), UnionHandler)

    print("Trusted Third Party serving at port" + PORT)
    httpd.serve_forever()

if __name__ == "__main__":
    main()