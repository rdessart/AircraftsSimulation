from threading import Thread, Lock

from .aircraft import Aircraft


class Aircrafts(Thread):
    def __init__(self):
        Thread.__init__(self, name="Aircrafts Perfo Thread")
        self.aircrafts = []
        self.mutex = Lock()
        self.exit = False

    def __len__(self) -> int:
        return len(self.aircrafts)

    def get_stack_id(self) -> list:
        return [acf.id for acf in self.aircrafts]

    def append(self, object: Aircraft):
        ids = self.get_stack_id()
        if len(ids) == 0:
            object.id = 1
        else:
            max_id = max(ids)
            for i in range(max_id):
                if i not in ids:
                    object.id = max_id
                    break
            if object.id == 0:
                object.id = max_id + 1
        self.aircrafts.append(object)

    def quit(self) -> None:
        locked = self.mutex.acquire(True)
        if not locked:
            return None
        self.exit = True
        self.mutex.release()

    def get_acft_by_id(self, id) -> Aircraft:
        ids = self.get_stack_id()
        if id not in ids:
            return None
        return self.aircrafts[ids.index(id)]

    def run_once(self) -> int:
        locked = self.mutex.acquire(True, 1.0)
        if not locked:
            return 0
        if self.exit:
            self.mutex.release()
            return -1
        for aircraft in self.aircrafts:
            aircraft.run()
        self.mutex.release()
        return 1

    def run(self) -> None:
        while self.run_once() > 0:
            continue

    def __str__(self) -> str:
        locked = self.mutex.acquire(True, 1.0)
        if locked:
            output = ""
            for aircraft in self.aircrafts:
                output += str(aircraft.performance)
            self.mutex.release()
            return output
