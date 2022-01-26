import abc
import domain.model as model
from typing import List


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)

    def get(self, sku) -> model.Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[model.Product]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def _add(self, product: model.Product):
        self.session.add(product)

    def _get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def list(self) -> List[model.Batch]:
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[model.Batch]:
        return list(self._batches)


class AbstractProductRepository(abc.ABC):
    def add(self, product):
        pass

    def get(self, sku) -> model.Product:
        pass
