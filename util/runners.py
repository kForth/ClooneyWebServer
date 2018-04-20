from threading import Thread
import time


class Runner(object):
    """
    Runs a function in a separate thread.
    """

    def __init__(self, target: classmethod, name="Runner"):
        self.__target = target
        self.name = name
        self.__thread = None

    def get_name(self) -> str:
        return self.name

    def run(self, *args, **kwargs):
        self.__thread = Thread(target=self.__target, args=args, kwargs=kwargs)
        self.__thread.start()

    def is_running(self) -> bool:
        return self.__thread.is_alive()

    def join(self):
        if self.__thread is not None:
            self.__thread.join()

    @staticmethod
    def sleep(delay: float, tick: float):
        time.sleep(max(0, delay - (time.time() - tick)))


class RepeatingRunner(Runner):
    """
    A Runner that automatically restarts itself after it's done.
    """

    def __init__(self, target: classmethod):
        Runner.__init__(self, self.work)
        self.target = target

        self.running = False
        self.iter = -1

    def start(self):
        if not self.running:
            self.running = True
            self.iter = -1
            self.run()

    def stop(self):
        self.running = False
        self.iter = -1

    def is_running(self) -> bool:
        return self.running

    def join(self):
        while self.is_running():
            time.sleep(0.01)

    def work(self):
        while self.running:
            self.iter = (self.iter + 1) % 5
            self.target()


class PeriodicRunner(Runner):
    """
    A Runner that automatically restarts itself after the specified delay.
    """

    def __init__(self, target: classmethod, delay=30.0, auto_start=True):
        Runner.__init__(self, self.work)
        self.delay = delay
        self.target = target

        self.running = False
        self.iter = -1

        if auto_start:
            self.start()

    def set_period(self, delay: float):
        self.delay = delay

    def start(self):
        if not self.running:
            self.running = True
            self.iter = -1
            self.run()

    def stop(self):
        self.running = False
        self.iter = -1

    def is_running(self) -> bool:
        return self.running

    def join(self):
        """
        Thread liveliness is checked at min 100Hz.
        """
        while self.is_running():
            time.sleep(min(0.01, self.delay))

    def work(self):
        while self.running:
            self.iter = (self.iter + 1) % 5
            tick = time.time()
            self.target()
            self.sleep(self.delay, tick)


class TriggeredPeriodicRunner(Runner):
    """
    A Runner that runs at a fixed period, but only when triggered.
    """

    def __init__(self, target: classmethod, auto_start=True, period=1.0):
        Runner.__init__(self, self._work)
        self._period = period
        self._target = target
        self._should_run_again = False

        self._running = False

        if auto_start:
            self.start()

    def will_run_again(self):
        return self._should_run_again

    def set_period(self, delay: float):
        self._period = delay

    def get_period(self):
        return self._period

    def start(self):
        if not self._running:
            self._should_run_again = False
            self._running = True
            self.run()
            self._running = False
            if self._should_run_again:
                self.start()
        else:
            self._should_run_again = True

    def stop(self):
        self._running = False
        self._should_run_again = False

    def is_running(self) -> bool:
        return self._running

    def join(self):
        while self.is_running():
            time.sleep(0.01)

    def _work(self):
        tick = time.time()
        self._target()
        self.sleep(self._period, tick)


class RunnerQueue(Runner):
    """
    Runs a series of functions or runners in the specified order.

    Not to be confused with a ResettingQueueRunner.
    """

    def __init__(self, *runners):
        Runner.__init__(self, self.work)
        self.runners = list(runners)

    def add_runner(self, runner: Runner):
        self.runners.append(runner)

    def get_list(self) -> list:
        return list(self.runners)

    def work(self):
        for runner in self.runners:
            if type(runner) is Runner:
                runner.run()
                runner.join()
            elif type(runner) in [classmethod, staticmethod]:
                runner()


class ResettingQueueRunner(Runner):
    """
    A runner with an internal queue that resets every time the runner is executed.

    Not to be confused with a RunnerQueue
    """

    def __init__(self, target: classmethod):
        Runner.__init__(self, target)
        self.target = target
        self.queue = []

    def __reset_queue(self):
        self.queue = []

    def add_to_queue(self, event):
        self.queue.append(event)

    def work(self):
        self.target()
        self.__reset_queue()


class ConcurrentRunner(RunnerQueue):
    """
    Runs a series of functions at the same time and dies when they're all done.
    Sub-thread liveliness is checked at 100Hz.
    """

    def __init__(self, *runners):
        RunnerQueue.__init__(self, *runners)

    def is_running(self):
        for runner in self.runners:
            if runner.is_running():
                return True
        return False

    def work(self):
        tick = time.time()
        for runner in self.runners:
            runner.start()
        while self.is_running():
            self.sleep(0.01, tick)
