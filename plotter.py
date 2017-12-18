# interactive plotter that runs in a separate process.

class interprocess_plotter:
    def __init__(self,num_lines=1):
        # super().__init__(remote_plotter_callback)
        from run_python import python_instance
        self.pi = python_instance('plotter2.py',is_filename=True)

        self.pi.send(('init',num_lines))

        # self.send(('init',num_lines))

    def pushys(self,ys):
        # self.send(('pushys', ys))
        self.pi.send(('pushys', ys))

    # def __del__(self):
    #     del self.pi

if __name__=='__main__':
    ip = interprocess_plotter2(2)
    import math,time
    for i in range(100):
        ip.pushys([math.sin(i/10), math.sin(i/10+2)])
        time.sleep(0.05)

    time.sleep(2)
    del ip # ugh..
