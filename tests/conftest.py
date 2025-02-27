import uuid

import pytest


@pytest.fixture
def owner():
    return str(uuid.uuid4())
