import datetime
import domain.model as model
import pytest
from typing import List
from adapters import repository
from service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product: model.Product):
        self._products.add(product)

    def _get(self, sku) -> model.Product:
        return next((p for p in self._products if p.sku == sku), None)

    def list(self) -> List[model.Product]:
        return super().list()


class FakeUnitOfWork(services.unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.commited = False

    def rollback(self):
        pass

    def _commit(self):
        self.commited = True


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATAED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATAED-LAMP", 10, uow)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


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
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, uow)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, uow)
    services.allocate("oref", "RETRO-CLOCK", 10, uow)

    batch = next(
        b
        for b in uow.products.get("RETRO-CLOCK").batches
        if b.reference == "in-stock-batch"
    )
    assert batch.available_quantity == 90
    batch = next(
        b
        for b in uow.products.get("RETRO-CLOCK").batches
        if b.reference == "shipment-batch"
    )
    assert batch.available_quantity == 100


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    batch = [
        b for b in uow.products.get("CRUNCHY-ARMCHAIR").batches if b.reference == "b1"
    ]
    assert batch is not None
    assert uow.commited


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATION-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATION-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)
