from uuid import UUID


class RepositoryError(Exception):
    pass


class NoneAfterInsertError(RepositoryError):
    msg = '{} was inserted but returned None'

    def __init__(self, resource: str) -> None:
        super().__init__(self.msg.format(resource))


class NoneAfterUpdateError(RepositoryError):
    msg = 'resource {} with id {} was updated but returned None'

    def __init__(self, resource: str, resource_id: UUID) -> None:
        super().__init__(self.msg.format(resource, resource_id))
