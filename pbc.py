# pipe based communicator
import os

# from https://stackoverflow.com/a/30375198
def int_to_bytes(x):
    return x.to_bytes(4, 'big')
def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')

class pbc: # pipe based communicator
    def __init__(self,fds=None):
        if fds is None: # as parent
            self.is_parent = True
            pipe1r, pipe1w = os.pipe()
            pipe2r, pipe2w = os.pipe()

            self.r,self.w = pipe1r, pipe2w
            self.childfds = pipe2r, pipe1w

            self.all_fds = [pipe1r,pipe1w,pipe2r,pipe2w]

            # make inheritable in child process.
            # https://docs.python.org/3/library/os.html#fd-inheritance
            [os.set_inheritable(k,True) for k in self.all_fds]
        else:
            # as child
            # child_pbc = pbc(parent.childfds)
            self.is_parent = False

            self.r,self.w = fds
            self.all_fds = [self.r,self.w]

        print('[pbc({})] self.w = {}, self.r = {}'.format(
            'parent' if self.is_parent else 'child',
            self.w,self.r
            ))

    def read(self):
        fd = self.r
        length = os.read(fd,4) # 2^32 max
        if len(length)!=4:
            raise EOFError('EOF on read(), expect 4, got {}'.format(len(length)))
        length = int_from_bytes(length)

        content = bytearray()
        remain = length
        while 1:
            temp = os.read(fd,remain)
            content += temp
            remain -= len(temp)

            if remain>0:
                continue
            elif remain<0:
                raise Exception('overread')
            else:
                return content
                # raise EOFError('EOF on read(), expect {}, got {}'.format(length,len(content)))
        # return content

    def write(self,bytes):
        fd = self.w
        length = len(bytes)
        length_bytes = int_to_bytes(length)
        if os.write(fd,length_bytes) != 4:
            raise EOFError('EOF on write()')
        if os.write(fd,bytes) != length:
            raise EOFError('EOF on write()')
        return True

    def __del__(self):
        [os.close(fd) for fd in self.all_fds]

# if __name__ == '__main__':
#     pbc1 = pbc()
#     pbc2 = pbc(pbc1.childfds)
#
#     pbc1.write('hello'.encode('utf-8'))
#     print(pbc2.read().decode('utf-8'))
#
#     pbc2.write('world'.encode('utf-8'))
#     print(pbc1.read().decode('utf-8'))
