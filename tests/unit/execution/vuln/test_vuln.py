import pytest
from execution.vuln.subzy_wrapper import SubzyPlugin
from execution.vuln.ffuf_wrapper import FfufPlugin
from execution.vuln.nuclei_wrapper import NucleiPlugin
from execution.vuln.dalfox_wrapper import DalfoxPlugin

def test_subzy_command():
    plugin = SubzyPlugin()
    cmd = plugin.build_command(["sub.example.com"], {})
    assert "subzy" in cmd

def test_ffuf_command():
    plugin = FfufPlugin()
    cmd = plugin.build_command("http://example.com", {"wordlist": "wordlist.txt"})
    assert "ffuf" in cmd

def test_nuclei_command():
    plugin = NucleiPlugin()
    cmd = plugin.build_command(["http://example.com"], {})
    assert "nuclei" in cmd

def test_dalfox_command():
    plugin = DalfoxPlugin()
    cmd = plugin.build_command(["http://example.com"], {})
    assert "dalfox" in cmd
