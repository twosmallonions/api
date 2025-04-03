import uuid

import pytest
from testcontainers.postgres import PostgresContainer



@pytest.fixture
def owner():
    return str(uuid.uuid4())
