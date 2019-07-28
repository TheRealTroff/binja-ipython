
import threading
import sys
import signal
from os import environ
# this is the heavy monkey-patching that actually works
# i.e. you can start the kernel fine and connect to it e.g. via
# ipython console --existing
signal.signal = lambda *args, **kw: None

from binaryninja import *

from ipykernel import connect_qtconsole
import ctypes

#from IPython.kernel.zmq.kernelapp import IPKernelApp
from ipykernel.kernelapp import IPKernelApp

# If we're started from a notebook, this will be used to pass the 
# connection file the notebook server expects us to use.
ARGV_VARIABLE='BINARYNINJA_IPYTHON_CONNECTIONFILE'


class KernelWrapper():
    def __init__(self):
        self.app = IPKernelApp.instance()
        return

    def start(self):
        self.thread = threading.Thread(target=self._run_kernel)
        self.thread.start()

    def _run_kernel(self):
        argv = None
        try:
            connection_file = environ[ARGV_VARIABLE]
            argv = ['-f', connection_file]
        except KeyError:
            pass

        self.app.init_signal = lambda *args, **kw: None
        self.app.initialize(argv)
        self.app.start()


    def inject_interrupt(self, bv):
        thread_obj = self.thread
        exception = KeyboardInterrupt
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_obj.ident), ctypes.py_object(exception))


    def spawn_qt(self, bv):
        connect_qtconsole(argv=["--no-confirm-exit",])
        return


# The IPython kernel prints its banner to sys.__stdout__
sys.__stdout__ = sys.stdout

kw = KernelWrapper()
kw.start()


PluginCommand.register("Binja IPython: Start QT Shell", "Binja IPython", kw.spawn_qt)
PluginCommand.register("Binja IPython: Interrupt", "Binja IPython", kw.inject_interrupt)



