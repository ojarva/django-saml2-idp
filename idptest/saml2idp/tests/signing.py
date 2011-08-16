import unittest
from saml2idp.signing import get_signature_xml

class TestSigning(unittest.TestCase):
    def test1(self):
        signature_xml = get_signature_xml("this is a test")
        print signature_xml
