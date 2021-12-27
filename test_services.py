import model
from repository import FakeRepository
import services


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
