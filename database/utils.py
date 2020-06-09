from queue import Queue
from threading import Thread, Event
from time import sleep
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from pathlib import Path

import database.models as models

logger = logging.getLogger("Database")
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
engine = create_engine('sqlite:///'+os.path.join(BASE_DIR, "db.sqlite"))
Session = sessionmaker(bind=engine)

CACHE_TIME = 10 * 60 # seconds

def get_session()-> Session:
    return Session()

class ItemSaver(Thread):
    """
    Cache will store a dict (gid, qty, price) -> timestamp to avoid saving same things twice
    """
    def __init__(self, queue: Queue, stop_event:Event=None) -> None:
        super().__init__()
        self.item_queue = queue
        self.stop_event = stop_event
        self.cache = {}

    def add_data(self, data: dict) -> None:
        """
        Given data from an item, add it to the db
        If needed, create the item
        :param data: data from a sniffed message
        :return:
        """
        cache_index = (data["item_gid"], data["quantity"], data["price"])
        timestamp = self.cache.get(cache_index)
        if timestamp is not None and (datetime.now() - timestamp).total_seconds() < CACHE_TIME:
            logger.debug(f"Skipping {data} at {datetime.now()} because of cache at {timestamp}")
            return
        logger.debug(f"Saving: {data}")
        session = get_session()
        try:
            item_gid = data["item_gid"]
            category_id = data["category"]
            category = session.query(models.SubCategory).filter_by(dofus_id=category_id).one_or_none()
            if category is None:
                category = models.SubCategory(
                    dofus_id=category_id,
                )
                session.add(category)
            item = session.query(models.Item).filter_by(item_gid=item_gid).one_or_none()
            if item is None:
                item = models.Item(item_gid=item_gid, sub_category=category)
                session.add(item)
            timestamp = datetime.now()
            object = models.PriceEntry(
                item=item,
                quantity=data["quantity"],
                price=data["price"],
                created_ts=timestamp,
            )
            session.add(object)
            session.commit()
            self.cache[cache_index] = timestamp
        except:
            session.close()
            raise

    def run(self) -> None:
        logger.info("ItemSaver started...")
        # Continue if queue is not empty, ot we didn't call stop event
        while (not self.stop_event or not self.stop_event.is_set()) or not self.item_queue.empty():
            if self.item_queue.empty():
                sleep(1)
                continue
            data = self.item_queue.get()
            try:
                self.add_data(data)
            except Exception as e:
                self.stop_event.set()
                logger.fatal(e)

        logger.info("ItemSaver killed.")