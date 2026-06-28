import pytest
import os
from execution.recon.subfinder_wrapper import SubfinderWrapper
from execution.recon.httpx_wrapper import HttpxPlugin
from execution.recon.assetfinder_wrapper import AssetfinderWrapper
from execution.recon.katana_wrapper import KatanaPlugin
from execution.recon.gau_wrapper import GauWrapper

def read_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "../../../fixtures", name)
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def test_subfinder_parser():
    plugin = SubfinderWrapper()
    out = read_fixture("subfinder.txt")
    res = plugin.parse(out, "")
    assert "sub1.example.com" in res
    assert "sub2.example.com" in res
    assert "sub3.example.com" in res

def test_subfinder_command():
    plugin = SubfinderWrapper()
    cmd = plugin.build_command("example.com", {})
    assert "subfinder" in cmd
    assert "-d" in cmd

def test_httpx_command():
    plugin = HttpxPlugin()
    cmd = plugin.build_command(["sub.example.com"], {})
    assert "httpx" in cmd
    assert "-l" in cmd

def test_assetfinder_command():
    plugin = AssetfinderWrapper()
    cmd = plugin.build_command("example.com", {})
    assert "assetfinder" in cmd

def test_katana_command():
    plugin = KatanaPlugin()
    cmd = plugin.build_command(["http://example.com"], {})
    assert "katana" in cmd

def test_gau_command():
    plugin = GauWrapper()
    cmd = plugin.build_command("example.com", {})
    assert "gau" in cmd

