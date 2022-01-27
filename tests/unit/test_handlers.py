import datetime
from email import message
import domain.model as model
import pytest
from typing import List
from adapters import repository
from service_layer import handler
from service_layer import messagebus
from domain import events


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


class FakeUnitOfWork(handler.unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.commited = False

    def rollback(self):
        pass

    def _commit(self):
        self.commited = True


class TestAddBatch:
    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow=uow
        )
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.commited


class TestAllocate:
    def test_returns_allocation(self):
        uow = FakeUnitOfWork()
        messagebus.handle(
            events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow
        )
        result = messagebus.handle(
            events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow
        )
        assert result[0] == "batch1"
