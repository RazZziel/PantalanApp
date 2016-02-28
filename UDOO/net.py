#!/usr/bin/env python
# coding=utf-8

import BaseHTTPServer

class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        sensors = self.io.read()
        #sensors = [1000, 1000, 1000]
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        #self.wfile.write(bytes("{{\"sensors\": [{}]}}".format("; ".join(str(a) for a in sensors))))
        self.wfile.write(bytes("[{}]".format(", ".join(str(a) for a in sensors))))

class NET:
    def __init__(self, io):
        WebHandler.io = io
        server_address = ('', 1808)
        try:
            print("Serving on port 1808")
            httpd = BaseHTTPServer.HTTPServer(server_address, WebHandler)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('^C received, shutting down server')
            httpd.socket.close()
