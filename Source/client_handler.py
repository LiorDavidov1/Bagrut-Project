import socket
import json
import ssl


class ClientHandler:
   def __init__(self, host='localhost', port=5000):
       self.host = host
       self.port = port


   def send_request(self, data):
       context = ssl.create_default_context()
       context.load_verify_locations(cafile='cert.pem')
       context.verify_mode = ssl.CERT_REQUIRED
       try:
           with socket.create_connection((self.host, self.port)) as sock:
               with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                   ssock.sendall(json.dumps(data).encode())
                   response = ssock.recv(4096)
                   return json.loads(response.decode())
       except Exception as e:
           return {"error": str(e)}