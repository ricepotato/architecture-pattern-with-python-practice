import domain.model as model
import pytest
from adapters.repository import FakeRepository
import service_layer.services as services


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATAED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATAED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())
