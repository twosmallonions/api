# Copyright 2025 Marius Meschter
# SPDX-License-Identifier: AGPL-3.0-only

import uuid

import pytest


@pytest.fixture
def owner():
    return str(uuid.uuid4())
