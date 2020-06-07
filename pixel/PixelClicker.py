from threading import Thread, Event


class PixelClicker(Thread):
    def __init__(self, stop_event: Event) -> None:
        super().__init__()
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event or not self.stop_event.is_set():
            pass

