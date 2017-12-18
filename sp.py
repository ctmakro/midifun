# test subprocess.

import time
import subprocess as sp
import sys,os
import threading as th

printlock = th.Lock()
def stdoutprint(*args):
    printlock.acquire()
    args = list(map(lambda x:str(x),args))
    s = ' '.join(args)
    sys.stdout.write(s)
    sys.stdout.flush()
    printlock.release()

def run_subprocess(args, end_callback=None, print_callback=stdoutprint):
    if print_callback is None:
        def print_callback(*args):
            pass

    print_callback(
        '[run_subprocess] starting process "{}"\n'.format(' '.join(args))
    )
    pop = sp.Popen(args,
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        close_fds=False, # allow communication via pipes
        preexec_fn=os.setpgrp # dont forward signals like ctrl-c (important)
    )
    def stderr_poll():
        while True:
            err = pop.stderr.readline()
            print_callback(err.decode('utf-8'))
            if pop.poll() is not None:
                break

    def stdout_poll():
        while True:
            out = pop.stdout.readline()
            print_callback(out.decode('utf-8'))
            if pop.poll() is not None:
                break

    def process_poll():
        while True:
            if pop.poll() is not None:
                print_callback(
                    '[run_subprocess] process "',
                    ' '.join(args),
                    '(pid {})'.format(pop.pid),
                    '" ended with status',
                    pop.returncode,
                    '\n'
                )
                if end_callback is not None:
                    end_callback()
                break
            else:
                time.sleep(0.2)

    import threading as th
    t = [th.Thread(target=k, daemon=True) for k in [stdout_poll,stderr_poll,process_poll]]

    [k.start() for k in t]
    return t,pop

if __name__ == '__main__':
    t, pop = run_subprocess(
        # ['ping','baidu.com'],
        ['python','-'],
        print_callback=stdoutprint,
    )
    pop.stdin.write('print("bitch")\nexit()\nprint("bitch")\n\n'.encode('utf-8'))
    # pop.stdin.flush()
    pop.stdin.close()
    [k.join() for k in t]
