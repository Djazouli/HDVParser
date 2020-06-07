from queue import Queue
import threading
from time import sleep
import logging


from mitm.MessageParser import MessageParser
from database.utils import ItemSaver
from pixel.PixelClicker import PixelClicker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

if __name__ == "__main__":
    message_queue = Queue()
    action_queue = Queue()
    stop_event = threading.Event()
    item_saver = ItemSaver(queue=message_queue, stop_event=stop_event)
    mitm = MessageParser(message_queue=message_queue, stop_event=stop_event)
    pixel = PixelClicker(action_queue=action_queue, stop_event=stop_event)
    logger.info("Bot is going to start...")
    sleep(3.) # Time needed to go on Dofus window
    item_saver.start()
    mitm.start()
    pixel.start()
    try:
        while not stop_event.is_set():
            sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt, gracefully stopping")
        stop_event.set()
        item_saver.join()
        mitm.join()
        pixel.join()
    logger.info("Bot stopped.")
