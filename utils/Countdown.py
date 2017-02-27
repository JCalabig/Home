from DefaultLogger import Log
import threading, datetime, time


class CountdownTimer(threading.Thread):
    def __init__(self, duration_seconds, action=None, sleep_interval=1, name=""):
        threading.Thread.__init__(self)
        self._name = name
        self._action = action
        self._quit = False
        self._duration_seconds = duration_seconds
        self._counter = duration_seconds
        self._sleep_interval = sleep_interval
        self._lock = threading.Lock()

    def reset(self):
        Log.info("%s: rest: run every %d secs (sleeping every %d secs)",
                 self._name, self._duration_seconds, self._sleep_interval)
        with self._lock:
            self._counter = self._duration_seconds

    def quit(self):
        Log.info("%s: on quit", self._name)
        if self._quit is True:
            return
        self._quit = True
        if self is not threading.current_thread():
            self.join()

    def run(self):
        Log.info("%s: run every %d secs (sleeping every %d secs)",
                 self._name, self._duration_seconds, self._sleep_interval)
        while not self._quit:
            time.sleep(self._sleep_interval)
            lower_limit = -1 * self._sleep_interval
            with self._lock:
                self._counter -= self._sleep_interval
                if self._counter < lower_limit * 2:
                    self._counter = lower_limit * 2
            Log.debug("%s: counter: %d", self._name, self._counter)
            if self._action is not None and lower_limit <= self._counter <= 0:
                Log.debug("%s: performing action!", self._name)
                self._action()
        Log.info("%s: quitting!", self._name)


if __name__ == "__main__":
    t = CountdownTimer(5, CountdownTimer.quit, sleep_interval=1)
    try:
        t.start()
        t.join()
    except:
        Log.info("Exception", exc_info=1)
    finally:
        t.quit()
