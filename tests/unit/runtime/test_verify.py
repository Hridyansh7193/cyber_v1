from runtime.verify import Verifier

def test_verifier_run():
    verifier = Verifier()
    report = verifier.verify()
    assert report is not None
    assert report.environment.python_version is not None
