import socket
import math


def consume_headers(sck: socket.socket):
    headers = dict()

    while True:
        header = sck.readline()
        header = str(header, "utf-8").strip()

        # data section is separated by newline
        if not header or header == '':
            break

        # otherwise, collect header values
        

        # status
        if header.startswith("HTTP/1.1"):
            _, statusCode, statusMessage = header.split(" ", 2)
            headers["status"] = int(statusCode.strip())
            headers["statusMessage"] = statusMessage.strip()
            continue 

        # capture generic headers
        try:
            name, value = header.split(":", 1)
            headers[name.lower()] = value.strip()
        except ValueError:
            print("don't know how to handle header", header)
            
    print("=== HEADERS ===")
    for header in headers:
        print(f"{header}: {headers[header]}")
    
    print("")
    return headers


def create_socket(url: str, method: str = "GET") -> socket.socket:
    # connect to socket and set GET request
    protocol, _, host, path = url.split('/', 3)
    protocol = protocol.strip(":").strip()

    try:
        host, port = host.split(":", 1)
    except ValueError:
        if protocol == "https":
            port = 443
        else:
            port = 80
            
    print("=== REQUEST ===\n", f'{method} /{path} HTTP/1.0\r\nHost: {host}\n', sep='')

    s = socket.socket()
    s.connect(socket.getaddrinfo(host, port)[0][-1])
    s.send(bytes(f'{method} /{path} HTTP/1.0\r\nHost: {host}\r\n\r\n', 'utf8'))

    return s


def stream_to_file(filename, url):
    s = create_socket(url)
    
    # parse headers
    headers = consume_headers(s)
    if headers["status"] < 200 or headers['status'] >= 400:
        raise Exception(f"Error fetching url: {headers['statusMessage']} [{headers['status']}]")
    
    try:
        size = int(headers["content-length"])
    except KeyError:
        raise Exception(f"Error fetching url: no content-length header")

    # open file
    with open(filename, "w+b") as f:
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
            print("Chunk %i (%i), %i/%i - %i%%" %
                  (i, chunk_size, received, size, round(float(received)/size, 3) * 100), end="\t\t\r")
            i += 1
        
        print("\n")
        
    s.close()


def request(url, method: str = "GET") -> str:
    s = create_socket(url, method)
    headers = consume_headers(s)
    body = s.read()
    s.close()

    return str(body, "utf8")
