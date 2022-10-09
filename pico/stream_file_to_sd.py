import socket
import math


def stream_to_file(filename, url, port=80):
    # connect to socket and set GET request
    _, _, host, path = url.split('/', 3)
    print(host, path, port)

    s = socket.socket()
    s.connect(socket.getaddrinfo(host, port)[0][-1])
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))

    # open file
    with open(filename, "w+b") as f:
        headers = True
        size = -1

        # parse headers
        print("=== HEADERS ===")
        i = 1
        while headers:
            header = s.readline()

            # data section is separated by newline
            if not header or header == b"\r\n":
                headers = False

            header = str(header, "utf8")

            # status
            if header.startswith("HTTP/1.1"):
                _, statusCode, statusMessage = header.split(" ", 2)
                statusCode = int(statusCode.strip())
                statusMessage = statusMessage.strip()

                print('GET %s/%s \t%i %s' %
                      (host, path, statusCode, statusMessage))

            # content size
            if header.startswith("Content-Length"):
                _, size = header.split(":", 1)
                size = int(size.strip())
                print(size, "bytes")

            # disregard everything else for now

        # data section
        i = 1
        received = 0
        print("=== DATA ===")
        while received < size:
            chunk = s.recv(min(size - received, 4096))
            chunk_size = len(chunk)
            received += chunk_size

            if not chunk:
                print("we're either done, or fucked.")

            f.write(chunk)
            print("=== Chunk %i (%i), %i/%i - %i%% ===" %
                  (i, chunk_size, received, size, round(float(received)/size, 3) * 100), end="\t\t\r")
            i += 1
