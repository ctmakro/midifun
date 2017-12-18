from sp import sp,run_subprocess,stdoutprint

# pipe based communicator
# from pbc import pbc
# socket based communicator
from sbc import sbc

# add following as prefix of code to initialize sbc at child-side
with open('sbc.py','r') as f:
    sbccode = f.read()

class python_instance:
    def __init__(self,code,is_filename=False,sigint=True,print_callback = stdoutprint):
        # create pipe based communicator prior to starting child process (important). otherwise the child cannot inherit the fd-s of the pipes
        # self.pbc = pbc()

        self.sbc = sbc()

        if is_filename==True:
            with open(code,'r') as f:
                code = f.read()

        t,pop = run_subprocess(
            ['python','-u'],
            end_callback = None,
            # print_callback = stdoutprint,
            print_callback = print_callback,
            # pass_fds = self.pbc.childfds, # not supported on windows...
        )
        self.finished=False
        self.t,self.pop = t,pop

        # file descriptors for child-side communication
        # cfds = self.pbc.childfds

        port = self.sbc.port

        precode = sbccode + '\n' + \
        "sbc = sbc({})".format(port)

        if sigint==False:
            precode+='''
import signal
def handle():
    pass
signal.signal(signal.SIGINT, handle)
'''
        precode+='''
def read(*a):return sbc.read(*a)
def write(*a):return sbc.write(*a)
def send(obj):
    import pickle
    bytes = pickle.dumps(obj)
    write(bytes)
def recv():
    import pickle
    bytes = read()
    return pickle.loads(bytes)
        '''

        postcode = '''
del sbc
        '''
        code = precode + code # + postcode

        # print(code)
        pop.stdin.write(code.encode('utf-8'))
        pop.stdin.close()

        # def onexit():
        #     nonlocal self
        #     del self
        #
        # import atexit
        # atexit.register(onexit)

    def wait_for_finish(self):
        print('waiting for', self.pop.pid, 'to finish')
        [k.join() for k in self.t]
        print(self.pop.pid,'finished')
        self.finished=True

    def kill(self):
        if self.finished:
            pass
        else:
            pid = self.pop.pid
            print('trying to kill',pid)
            self.pop.kill()
            self.wait_for_finish()
            print(pid,'killed')

    def __del__(self):
        self.kill()
        # del self.pbc
        del self.sbc

    def read(self):
        return self.sbc.read()
    def write(self,bytes):
        return self.sbc.write(bytes)

    def send(self,obj):
        import pickle
        bytes = pickle.dumps(obj)
        self.write(bytes)

    def recv(self):
        import pickle
        bytes = self.read()
        return pickle.loads(bytes)

def extract_source(f):
    import inspect
    lines = inspect.getsourcelines(f)
    print("".join(lines[0]))

if __name__ == '__main__':
    code = '''
import time
while True:
    d = recv()
    if d == 'stop':
        send('ok, stopped')
        break
    else:
        print(d)
    time.sleep(0.5)
# recv()
    '''

    pi = python_instance(code)

    pi.send('hello')
    pi.send('world')
    pi.send('yeah!')
    pi.send('stop')
    print(pi.recv())

    import time
    time.sleep(1)
    # del pi # pi might not end as expected.
    pi.wait_for_finish()
