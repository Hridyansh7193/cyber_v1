import pytest
from unittest.mock import patch
from execution.api.swagger_wrapper import SwaggerWrapper
from execution.api.graphql_wrapper import GraphqlWrapper

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_swagger_wrapper_success(mock_run):
    mock_run.return_value = (0, "swagger out", "", 1.0)
    res = SwaggerWrapper.execute(["http://example.com"])
    assert res.success

def test_swagger_wrapper_empty():
    res = SwaggerWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_graphql_wrapper_success(mock_run):
    mock_run.return_value = (0, "graphql out", "", 1.0)
    res = GraphqlWrapper.execute(["http://example.com/graphql"])
    assert res.success

def test_graphql_wrapper_empty():
    res = GraphqlWrapper.execute([])
    assert res.success
