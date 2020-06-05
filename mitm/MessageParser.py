from threading import Thread, Event
from queue import Queue
import logging
from scapy.packet import Raw

from labot.sniffer.network import Msg, sniff, on_receive

logger = logging.getLogger("MessageParser")

sniffed_types = {
    "ExchangeTypesExchangerDescriptionForUserMessage",
    "ExchangeTypesItemsExchangerDescriptionForUserMessage",
}

class IncompleteData(Exception):
    pass

class MessageParser(Thread):
    def __init__(self, message_queue: Queue, stop_event: Event = None) -> None:
        super().__init__()
        self.queue = message_queue
        self.stop_event = stop_event

    def extract_data(self, message: dict) -> [dict]:
        item_prices = []
        item_lines = message.get("itemTypeDescriptions")
        # item_lines represents the lines in the HDV
        for line in item_lines:
            objectGID = line.get("objectGID")
            objectType = line.get("objectType")
            prices = line.get("prices")

            if objectGID is None or objectType is None or prices is None:
                raise IncompleteData("")
            
            item = {
                "category": objectType,
                "item_gid": objectGID
            }

            for index, price in enumerate(prices):
                if not price:
                    continue
                item_prices.append({**item, "price": price, "quantity": 10**index})

        return item_prices


    def run(self):
        logger.info("Message parser started...")

        def on_msg(message: Msg) -> None:
            message = message.json()
            logger.debug(f"Sniffed message: {message}")
            message_type = message.get("__type__")
            if not message_type in sniffed_types:
                return
            if message_type == "ExchangeTypesItemsExchangerDescriptionForUserMessage":
                data = self.extract_data(message)
                logger.debug(f"Sending {data} to the queue")
                for entry in data:
                    self.queue.put(entry)


        sniff(
            filter="tcp port 5555",
            lfilter=lambda p: p.haslayer(Raw),
            stop_event=self.stop_event,
            prn=lambda p: on_receive(p, on_msg),
        )

        logger.info("Message parser killed.")
