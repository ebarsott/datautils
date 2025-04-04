#!/usr/bin/env python

import multiprocessing

from . import serf


class Lord(object):
    def __init__(self):
        self._state = None
        self.process = None
        self._cbindex = 0
        self.callbacks = {} 

    def attach(self, attr, func):
        ######################################################################
        # Elizabeth: original code throwing TypeError: list indices must be integers or slices, not str
        ######################################################################
        #if attr not in self.callbacks: 
            #self.callbacks[attr] = {} 
        #cbid = self._cbindex
        #self._cbindex += 1
        #self.callbacks[attr][cbid] = func
        #return cbid
        ######################################################################
        ######################################################################
        # Elizabeth: try instead:
        for callback in self.callbacks: # this works
            if self.callbacks[callback] != attr: # this works
                self.callbacks[callback] = {} # this works
        cbid = self._cbindex # this works
        self._cbindex += 1 # this works
        for attribute in self.callbacks:
            if self.callbacks[attribute] == attr:
                self.callbacks[attribute][cbid] = func 
        return cbid
        ######################################################################

    # Elizabeth: original code; returning int for callback id after changing definintion for attach above.
    #def detatch(self, cbid):
    #    for a in self.callbacks:
    #        if cbid in self.callbacks[a]:
    #            del self.callbacks[a][cbid]
    #            return
    #    raise ValueError("Callback id[%s] not found" % (cbid, ))
    # Elizabeth: try instead:
    def detatch(self, cbid):
        for a in self.callbacks:
            if self.callbacks[a] == cbid:
                del self.callbacks[a][cbid]
                return
        raise ValueError("Callback id[%s] not found" % (cbid, ))

    def state(self, new_state=None, update=False):
        if new_state is None:
            if update:
                self.update()
            return self._state
        self._state = new_state

    def error(self, *args, **kwargs):
        raise serf.SerfError(*args, **kwargs)

    def send(self, attr, *args, **kwargs):
        assert isinstance(attr, str)
        self.pipe.send((attr, args, kwargs))

    def start(self, serf_class, args=None, kwargs=None, wait=True):
        if self.process is not None and self.process.is_alive():
            return
        self.pipe, serf_pipe = multiprocessing.Pipe()
        self.process = multiprocessing.Process(
            target=serf.run_serf, args=(
                serf_class, serf_pipe, args, kwargs))
        self.process.daemon = True
        self.process.start()
        if wait:
            while self.state(update=True) is None:
                self.update()

    def stop(self, wait=True):
        if self.process is None:
            return
        if not self.process.is_alive():
            self.process = None
            return
        self.send('exit')
        if not wait:
            return
        while self.process.is_alive():
            self.update()
        self.process.join()
        self.process = None

    def __del__(self):
        self.stop(wait=True)
        
    def update(self, timeout=0.001):
        if self.pipe.poll(timeout):
            msg = self.pipe.recv()
            attr, args, kwargs = serf.parse_message(self, msg)
            getattr(self, attr)(*args, **kwargs)

            if attr in self.callbacks:
                cb_group = self.callbacks[attr]
                if isinstance(cb_group, dict):
                    for cb in cb_group.values():
                        cb(*args, **kwargs)
                elif isinstance(cb_group, list):
                    for cb in cb_group:
                        cb(*args, **kwargs)
                elif callable(cb_group):
                    cb_group(*args, **kwargs)


    # Elizabeh: this is throwing an error
    #def update(self, timeout=0.001):
    #    if self.pipe.poll(timeout):
    #        msg = self.pipe.recv()
    #        attr, args, kwargs = serf.parse_message(self, msg)
    #        getattr(self, attr)(*args, **kwargs)
    #        if attr in self.callbacks:
    #            [
    #                self.callbacks[attr][cbid](*args, **kwargs)
    #                for cbid in self.callbacks[attr]] # Elizabeth: original
                    #for cbid in range(len(self.callbacks[attr]))] # Elizabeth: test
