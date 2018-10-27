import server

def main():
    web_server = server.WebServer()
    web_server.server_start()
    while 1:
        data = web_server.GET_response()
        print(data)

if __name__ == '__main__':
    main()