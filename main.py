from queue import Queue
import threading
from time import sleep
import logging


from mitm.MessageParser import MessageParser
from database.utils import ItemSaver

logging.basicConfig(level=logging.DEBUG)
main = logging.getLogger("main")

if __name__ == "__main__":
    message_queue = Queue()
    stop_event = threading.Event()
    item_saver = ItemSaver(queue=message_queue, stop_event=stop_event)
    mitm = MessageParser(message_queue=message_queue, stop_event=stop_event)
    item_saver.start()
    mitm.start()
    try:
        while not stop_event.is_set():
            sleep(1)
    except KeyboardInterrupt:
        main.info("Keyboard interrupt, gracefully stopping")
        stop_event.set()
        item_saver.join()
        mitm.join()
    main.info("Bot stopped.")
