import socket
from cryptography.fernet import Fernet


class WebServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname("")
        self.port = 12345

    def server_start(self):
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as error_msg:
            print('Bind failed. Error Code : ' + str(error_msg[0]) + ' Message ' + error_msg[1])
            exit(1)

        self.socket.listen(10)

    def __to_file(self, msg, key):
        """
        Writes both the Encoded message and the Key to a file

        :param msg: The Encoded Message
        :param key: The Fernet Key
        :return: None
        """
        msg_h = open('msg.txt', 'w')
        msg_h.write(msg.decode())
        msg_h.close()

        key_h = open('key.txt', 'w')
        key_h.write(key.decode())
        key_h.close()

    def GET_response(self):
        # file_object = open("index.html", "rb")
        # webpage = file_object.read()
        # print webpage
        print("Waiting HTTP header:")
        c, addr = self.socket.accept()
        print('Got connection from', addr)
        data = c.recv(1000)  # should receive request from client. (GET ....)
        webpage = self.__parsing_header(data)
        # c.send(b'HTTP/1.1 200 OK\n')
        # c.send(b'Content-Type: text/html\n')
        # c.send(b'\n\n')  # header and body should be separated by additional newline
        c.send(webpage)
        c.close()
        return "Request answered correctly"

    def _generate_headers(self, response_code):
        header = b''
        if response_code == 200:
            header = b"HTTP/1.1 200 OK\nContent-Type: text/html\n"

        elif response_code == 404:
            header = b"HTTP/1.1 404 Not Found\n\n"
            return header

        elif response_code == 302:
            header = b"HTTP/1.1 302 Found\nContent-Type: text/html\n"
        return header

    def __parsing_header(self, data):
        decoded_data = data .decode()
        print(decoded_data)
        request_method = decoded_data.split(' ')[0]
        requested_file = decoded_data.split(' ')[1]
        if requested_file == '/':
            requested_file = 'index.html'

        try:
            requested_file = requested_file.replace("/", "", 1)
            fh = open(requested_file, 'rb')
            response_data = fh.read()
            response_size = str(len(response_data))
            response_size = bytes(response_size, 'utf8')
            fh.close()

        except IOError as e:
            print("Error opening/reading the file")
            response_header = self._generate_headers(404)
            return response_header

        if request_method == "GET":
            response_header = self._generate_headers(200)
            response_header += (b"Content-Length: " + response_size + b"\n\n")
            response = response_header
            response += response_data
            return response

        elif request_method == "HEAD":
            response_header = self._generate_headers(200)
            response_header += (b"Content-Length: " + response_size + b"\n\n")
            response = response_header
            return response

        elif request_method == "POST":
            if "chave=" in decoded_data:
                decrypt_key = decoded_data.split("chave=", 1)[1]
                decrypt_key = decrypt_key.split("\n", 1)[0]
                plain_message = decrypt_key.split("\n", 1)[1]
                f = Fernet(decrypt_key)
                decoded_msg = f.decrypt(plain_message)
                msg_h = open('msg.txt', 'w')
                msg_h.write(decoded_data)
                msg_h.close()
                response_header = self._generate_headers(200)
                response_size = len(decoded_msg)
                response_size = bytes([response_size])
                response_header += (b"Content-Length: " + response_size + b"\n\n")
                response = response_header + decoded_msg
                return response

            elif "texto=" in decoded_data:
                plain_message = decoded_data.split('texto=', 1)[1]
                key = Fernet.generate_key()
                f = Fernet(key)
                encoded_message = bytes(plain_message, 'utf8')
                encoded_message = f.encrypt(encoded_message)
                self.__to_file(encoded_message, key)
                response_header = self._generate_headers(200)
                response_size = len(encoded_message) + len(key)
                response_size = bytes([response_size])
                response_header += (b"Content-Length: " + response_size + b"\n\n")
                response = response_header + encoded_message + b" " + key
                return response
        else:
            print("Unknown HTTP Request.")