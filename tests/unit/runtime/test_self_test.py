import pytest
from runtime.self_test import SelfTest

def test_self_test_run():
    st = SelfTest()
    assert st.run() is True
