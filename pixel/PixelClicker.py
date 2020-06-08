from threading import Thread, Event
from queue import Queue
from time import sleep
import pyautogui
import logging

from pixel.actions import ClickOnUnclickedCategories, GoToCategoriesTop, GoToBottomItemsAndClick, ClickNextCategory

pyautogui.FAILSAFE = True
logger = logging.getLogger("PIXEL")

class PixelClicker(Thread):
    """
    get an action queue that may be fed by other threads. Currently, I think it is just going to feed itself
    TODO: I think I may have to review the way to manage actions (check fi something is true with image recognition...)
    """

    def __init__(self, action_queue: Queue, stop_event: Event=None) -> None:
        super().__init__()
        self.stop_event = stop_event
        self.actions = action_queue
        if self.actions.empty():
            self.actions.put(ClickNextCategory())


    def run(self):
        logger.info("Pixel started...")
        try:
            while not self.stop_event or not self.stop_event.is_set():
                # Try to make the actions as small as possible so you are able to quit gently at anytime
                if self.actions.empty():
                    sleep(1)
                    continue
                action = self.actions.get()
                action.execute()
                next_action = action.next_action()
                if next_action is not None:
                    self.actions.put(next_action)
        except pyautogui.FailSafeException:
            logger.info("Failsafe for Pixel, shutting down...")
        except Exception as e:
            logger.fatal(e)
        finally:
            if self.stop_event is not None:
                self.stop_event.set()
            logger.info("Pixel killed.")




if __name__ == "__main__":
    action_queue = Queue()
    action_queue.put(ClickOnUnclickedCategories())
    pixel = PixelClicker(action_queue)
    sleep(3)
    pixel.start()


