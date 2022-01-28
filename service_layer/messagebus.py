import logging
from typing import Union, List
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential
from domain import events, commands
from service_layer import unit_of_work
from service_layer.handler import (
    change_batch_quantity,
    send_out_of_stock_notification,
    add_batch,
    allocate,
)

logger = logging.getLogger("app")


Message = Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not a event or commnad")
    return results


EVENT_HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
}

COMMAND_HANDLERS = {
    commands.Allocate: allocate,
    commands.CreateBatch: add_batch,
    commands.ChangeBatchQuantity: change_batch_quantity,
}


def handle_event(
    event: events.Event, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3), wait=wait_exponential()
            ):
                with attempt:
                    logger.debug("handle event %s with handler %s", event, handler)
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_events())
        except RetryError as retry_failure:
            logger.error(
                "failed to handle event %s times, giving up!",
                retry_failure.last_attempt.attempt_number,
            )
            continue


def handle_command(
    command: events.Event, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug("handing command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("exception handing command %s", command)
        raise
