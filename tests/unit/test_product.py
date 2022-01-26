from datetime import date
from domain import events
from domain.model import Batch, OrderLine, Product


def test_records_out_of_stock_event_if_cannot_allocate():
    today = date.today()
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    product = Product(sku="SMALL-FORK", batches=[batch])
    product.allocate(OrderLine("order1", "SMALL-FORK", 10))

    allocation = product.allocate(OrderLine("order2", "SMALL-FORK", 10))
    assert product.events[-1] == events.OutOfStock(sku="SMALL-FORK")
    assert allocation is None
