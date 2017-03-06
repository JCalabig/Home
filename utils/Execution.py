from DefaultLogger import Log
import threading, time


class RepeatedExecution(threading.Thread):
    def __init__(self, action, start=False, tag=""):
        threading.Thread.__init__(self)
        self.tag = tag
        self._action = action
        self._quit = False
        if start is True:
            self.start()

    def quit(self):
        Log.info("%s: quitting", self.tag)
        try:
            self._quit = True
            if self is not threading.current_thread():
                Log.info("%s: ... waiting to quit", self.tag)
                self.join()
        finally:
            Log.info("%s: quitting exited", self.tag)

    def run(self):
        Log.info("%s: thread started", self.tag)
        try:
            while not self._quit:
                if self._action is not None:
                    self._action()
        finally:
            Log.info("%s: thread exited", self.tag)


class CountedExecution(RepeatedExecution):
    def __init__(self, repeated_action, interval, count, start=False, tag="CountedExecution"):
        self._interval = interval
        self._repeated_action = repeated_action
        self.count = count
        RepeatedExecution.__init__(self, self._internal_action, start, tag)

    def _internal_action(self):
        if self.count <= 0:
            return
        Log.info("%s: doing action, count=%d", self.tag, self.count)
        self._repeated_action()
        self.count -=1
        time.sleep(self._interval)


class IntervalExecution(RepeatedExecution):
    def __init__(self, interval_action, interval_seconds, start=False, tag="IntervalExecution"):
        self._interval_action = interval_action
        self._interval_seconds = interval_seconds
        self._last_execution = 0
        RepeatedExecution.__init__(self, self._internal_action, start, tag)

    def reset(self):
        self._last_execution = 0

    def _internal_action(self):
        if (time.time() - self._last_execution) < self._interval_seconds:
            return
        Log.info("%s: doing action", self.tag)
        self._interval_action()
        self._last_execution = time.time()
        time.sleep(1)

if __name__ == "__main__":
    def do():
        print("hey")

    try:
        t = IntervalExecution(do, 3, True)
        time.sleep(30)
    except:
        Log.info("Exception", exc_info=1)
    finally:
        t.quit()
