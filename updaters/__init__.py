from enum import Enum
from time import time, sleep

from updaters.average import AverageCalculator
from util.runners import RepeatingRunner


class UpdateLevel(Enum):
    CREATE_EVENT = 0
    TBA_INFO = 1
    RAW_DATA = 2


class UpdateHandler(RepeatingRunner):
    def __init__(self):
        RepeatingRunner.__init__(self, self.process_update)
        self.average_calc = AverageCalculator()
        self.update_queue = {}
        self.start()

    def mark_event_for_update(self, event: str, updates: list, bump_queue=False):
        if event in self.update_queue.keys():
            for update_level in updates:
                self.update_queue[event]['update_levels'].add(update_level)
        else:
            self.update_queue[event] = {
                'update_levels': set(updates),
                'time_entered': time()
            }
        if bump_queue:
            self.update_queue['time_entered'] = 0
        if not self.running:
            self.start()

    def _get_sorted_queue(self) -> dict:
        return dict(sorted(self.update_queue.items(), key=lambda t: t[1]['time_entered']))

    def process_update(self):
        if len(list(self.update_queue.keys())) > 0:
            event = list(self._get_sorted_queue().keys())[0]
            update_levels = self.update_queue[event]['update_levels']
            del self.update_queue[event]
            if UpdateLevel.RAW_DATA in update_levels:
                print(event)
                # self.average_calc.run(event)
            if UpdateLevel.CREATE_EVENT in update_levels:
                update_levels.add(UpdateLevel.TBA_INFO)
            if UpdateLevel.TBA_INFO in update_levels:
                pass  # TODO
        else:
            self.stop()
