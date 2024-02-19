from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from miappe_validator import Miappe_validator as mv

hostName = "0.0.0.0"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This web server only serves post requests</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def get_body(self):
        content_len = int(self.headers.get('Content-Length'))
        return self.rfile.read(content_len)

    def do_POST(self):
        body = json.loads(self.get_body())
        self.logs = []
        try:
            self.logs = mv(body['file']).run_miappe_validator()
        except Exception as e:
            self.logs.append(str(e))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>OntoBrapi Validator</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>", "utf-8"))
        for logLine in self.logs:
            self.wfile.write(bytes(logLine, "utf-8"))
            self.wfile.write(bytes("<br>", "utf-8"))
        self.wfile.write(bytes("</p></body></html>", "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
