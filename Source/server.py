import socket
import json
import logging
import ssl
import threading
from database_handler import ServerHandler


logging.basicConfig(
   level=logging.INFO,
   format='%(levelname)s - %(message)s'
)


def handle_client(conn, addr, db_handler):
   logging.info(f"Connected by {addr}")
   with conn:
       while True:
           data = conn.recv(4096)
           if not data:
               break
           try:
               request = json.loads(data.decode())
               command = request.get("command")
               logging.info(f"Received command: {command}")


               if command == "check_login":
                   response = db_handler.check_login(request["user_id"], request["password"])
               elif command == "get_loans":
                   response = db_handler.get_loans(request["student_id"])
               elif command == "get_user_info":
                   response = db_handler.get_user_info(request["user_id"])
               elif command == "request_extension":
                   logging.info(f"Processing extension request for student ID: {request['student_id']}")
                   response = db_handler.request_extension(
                       request["student_id"],
                       request["message"]
                   )
               elif command == "register_student":
                   logging.info(f"Registering new student")
                   response = db_handler.register_student(request["student_data"])
               elif command == "get_all_students":
                   response = db_handler.get_all_students()
               elif command == "update_loans":
                   logging.info(f"Updating loans for student ID: {request['student_id']}")
                   response = db_handler.update_loans(request["student_id"], request["books_authors"], request["due_date"])
               else:
                   response = {"error": "Unknown command"}

               conn.sendall(json.dumps(response).encode())
           except Exception as e:
               conn.sendall(json.dumps({"error": str(e)}).encode())


def main():
   HOST = 'localhost'
   PORT = 5000
   context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
   context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
   db_handler = ServerHandler()


   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
       sock.bind((HOST, PORT))
       sock.listen()
       logging.info(f"Server listening on {HOST}:{PORT} (with SSL/TLS)")
       while True:
           conn, addr = sock.accept()
           ssl_conn = context.wrap_socket(conn, server_side=True)
           threading.Thread(target=handle_client, args=(ssl_conn, addr, db_handler)).start()


if __name__ == "__main__":
   main()