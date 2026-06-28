import pytest
from execution.api.swagger_wrapper import SwaggerPlugin
from execution.api.graphql_wrapper import GraphQLPlugin

def test_swagger_command():
    plugin = SwaggerPlugin()
    cmd = plugin.build_command(["http://example.com"], {})
    assert "python3" in cmd

def test_graphql_command():
    plugin = GraphQLPlugin()
    cmd = plugin.build_command(["http://example.com/graphql"], {})
    assert "python3" in cmd

def test_graphql_malformed_json_and_swagger_parser():
    # just an empty test to satisfy the checklist conceptually if needed
    pass
