from domain import events
from service_layer import unit_of_work
from service_layer.handler import send_out_of_stock_notification, add_batch, allocate


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results


HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
    events.BatchCreated: [add_batch],
    events.AllocationRequired: [allocate],
}
