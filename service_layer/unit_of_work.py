import abc
import config
from adapters import repository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service_layer import message_bus


class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractProductRepository

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                message_bus.handle(event)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(config.get_sqlite_url()))


class SqlalchemyUnitofWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        return self.session.commit()

    def rollback(self):
        self.session.rollback()
