from threading import Thread
from time import sleep, time


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
        self.__thread.daemon = True
        self.__thread.start()

    def is_running(self) -> bool:
        return self.__thread.is_alive()

    def join(self):
        if self.__thread is not None:
            self.__thread.join()

    @staticmethod
    def sleep(delay: float, tick: float):
        sleep(delay - (time() - tick))


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
            sleep(0.01)

    def work(self):
        while self.running:
            self.iter = (self.iter + 1) % 5
            self.target()


class PeriodicRunner(Runner):
    """
    A Runner that automatically runs at a fixed period.
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
        while self.is_running():
            sleep(0.01)

    def work(self):
        while self.running:
            self.iter = (self.iter + 1) % 5
            tick = time()
            self.target()
            print("run")
            self.sleep(self.delay, tick)


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
        tick = time()
        for runner in self.runners:
            runner.start()
        while self.is_running():
            self.sleep(0.01, tick)
