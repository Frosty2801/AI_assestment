"""Pytest fixtures."""
import pytest
from unittest.mock import Mock
import sys
sys.path.append("../src")


@pytest.fixture
def mock_vectorstore():
    mock = Mock()
    mock.similarity_search.return_value = []
    return mock


@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.invoke.return_value = "Mock response"
    return mock
