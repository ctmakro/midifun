# socket based communicator
import os

# from https://stackoverflow.com/a/30375198
def int_to_bytes(x):
    return x.to_bytes(4, 'big')
def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')

import socket

class sbc: # socket based communicator
    def __init__(self,port=None):
        if port is None:
            self.is_parent=True
        else:
            self.is_parent=False

        sock = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
        self.sock = sock
        sock.bind(('localhost',0))
        bindaddr,bindport = sock.getsockname()

        if self.is_parent:
            self.port = bindport
            sock.listen()
            self.conn_ready = False
            print('[pbc(parent)] listening on port',self.port)
        else:
            sock.connect(('localhost',port))
            self.conn = sock
            self.port = port
            print('[pbc(child)] connecting to port',self.port,'from port',bindport)

    def readyup(self):
        if self.is_parent:
            # only servers need to wait for incoming connection.
            if self.conn_ready:
                pass
            else:
                conn,address = self.sock.accept()
                self.conn = conn
                self.conn_ready = True

    def read(self):
        self.readyup()

        c = self.conn
        length = c.recv(4)
        if len(length)!=4:
            raise EOFError('EOF on read(), expect 4, got {}'.format(len(length)))
        length = int_from_bytes(length)

        content = b''
        remain = length
        while 1:
            temp = c.recv(remain)
            content += temp
            remain -= len(temp)

            if remain>0:
                continue
            elif remain<0:
                raise Exception('overread')
            else:
                return content

    def write(self,bytes):
        self.readyup()

        c = self.conn
        length = len(bytes)
        length_bytes = int_to_bytes(length)
        if c.send(length_bytes) != 4:
            raise EOFError('EOF on write()')
        if c.send(bytes) != length:
            raise EOFError('EOF on write()')
        return True

    def __del__(self):
        self.conn.close()

# if __name__ == '__main__':
#     sbc1 = sbc()
#     sbc2 = sbc(sbc1.port)
#
#     sbc1.write('hello'.encode('utf-8'))
#     print(sbc2.read().decode('utf-8'))
#
#     sbc2.write('world'.encode('utf-8'))
#     print(sbc1.read().decode('utf-8'))
