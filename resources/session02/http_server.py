#!/usr/bin/env python

import socket
import sys

def response_ok():
    retVal = []
    retVal.append('HTTP/1.1 200 OK')
    retVal.append('Content-Type: text/plain')
    retVal.append('')
    retVal.append('this is pretty minimal response')
    return '\r\n'.join(retVal)

def response_method_not_allowed():
    retVal = []
    retVal.append('HTTP/1.1 405 Method Not Allowed')
    retVal.append('')
    return '\r\n'.join(retVal)

def parse_request(request):

    method, uri, prot = request.split('\r\n',1)[0].split()
    if method != 'GET':
        raise NotImplementedError('Only processes GET request')
    print >>sys.stderr, 'request is okay'

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>log_buffer, "making a server on {0}:{1}".format(*address)
    sock.bind(address)
    sock.listen(1)
    
    try:
        while True:
            print >>log_buffer, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>log_buffer, 'connection - {0}:{1}'.format(*addr)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data
                    print >>log_buffer, 'received "{0}"'.format(data)
                    if len(data) < 1024:
                        break
                print >>log_buffer, 'sending response'
                try:
                    parse_request(request)
                    response = response_ok()
                except NotImplementedError:
                    response = response_method_not_allowed()
                conn.sendall(response)
            finally:
                conn.close()
            
    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
