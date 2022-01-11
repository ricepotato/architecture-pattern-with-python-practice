import datetime
import domain.model as model
import pytest
from adapters.repository import AbstractRepository
import service_layer.services as services


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeRepository(set):
    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def list(self):
        return list(self)


def test_returns_allocation():
    # line = model.OrderLine("o1", "COMPLICATAED-LAMP", 10)
    repo = FakeRepository.for_batch("b1", "COMPLICATAED-LAMP", 100, eta=None)
    result = services.allocate("o1", "COMPLICATAED-LAMP", 10, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    # line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    # batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository.for_batch("b1", "AREALSKU", 100, eta=None)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_prefers_current_stock_batches_to_shipments():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    model.allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    repo = FakeRepository([in_stock_batch, shipment_batch])
    session = FakeSession()

    # line = model.OrderLine("oref", "RETRO-CLOCK", 10)
    services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
