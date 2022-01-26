from domain import events
from adapters import email


def handle(event: events.Event):
    for handler in HANDLERS[type(events.event)]:
        handler(event)


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_email("stock@made.com", f"Out of Stock for {event.sku}")


HANDLERS = {events.OutOfStock: [send_out_of_stock_notification]}
