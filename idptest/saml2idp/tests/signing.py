import string
import unittest
from saml2idp.signing import get_signature_xml
from saml2idp.xml_templates import ASSERTION, RESPONSE

ASSERTION_PARAMS = {
    'ACS_URL': 'https://www.example.net/a/example.com/acs',
    'ASSERTION_ID': '_7ccdda8bc6b328570c03b218d7521772998da45374',
    'AUDIENCE': 'example.net',
    'AUTH_INSTANT': '2011-08-11T23:38:34Z',
    'ISSUE_INSTANT': '2011-08-11T23:38:34Z',
    'ISSUER': 'http://127.0.0.1:8000',
    'NOT_BEFORE': '2011-08-11T23:38:04Z',
    'NOT_ON_OR_AFTER': '2011-08-11T23:43:34Z',
    'SESSION_NOT_ON_OR_AFTER': '2011-08-12T07:38:34Z',
    'SIGNATURE': '', # it's unsigned
    'SP_NAME_QUALIFIER': 'example.net',
    'SUBJECT_EMAIL': 'randomuser@example.com',
    'REQUEST_ID': 'mpjibjdppiodcpciaefmdahiipjpcghdcfjodkbi',
}

ASSERTION_XML = '<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_7ccdda8bc6b328570c03b218d7521772998da45374" IssueInstant="2011-08-11T23:38:34Z" Version="2.0"><saml:Issuer>http://127.0.0.1:8000</saml:Issuer><saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:email" SPNameQualifier="example.net">randomuser@example.com</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData InResponseTo="#mpjibjdppiodcpciaefmdahiipjpcghdcfjodkbi" NotOnOrAfter="2011-08-11T23:43:34Z" Recipient="https://www.example.net/a/example.com/acs"></saml:SubjectConfirmationData></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="2011-08-11T23:38:04Z" NotOnOrAfter="2011-08-11T23:43:34Z"><saml:AudienceRestriction><saml:Audience>example.net</saml:Audience></saml:AudienceRestriction></saml:Conditions><saml:AuthnStatement AuthnInstant="2011-08-11T23:38:34Z" SessionNotOnOrAfter="2011-08-12T07:38:34Z"><saml:AuthnContext><saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml:AuthnContextClassRef></saml:AuthnContext></saml:AuthnStatement></saml:Assertion>'
SIGNED_ASSERTION_XML = '<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_7ccdda8bc6b328570c03b218d7521772998da45374" IssueInstant="2011-08-11T23:38:34Z" Version="2.0"><saml:Issuer>http://127.0.0.1:8000</saml:Issuer><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI="#_7ccdda8bc6b328570c03b218d7521772998da45374"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>2nGwGSBLWPG9oeBlDjEcOfaXyxM=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>mHCyMVL+zLYMsnFf4sVeCQixbJGg8lcfjGEdvbKmOxZArbhYOQ/YDyl3sywAN6MjqkOkgqoDVBvA9Tpd+S3DDQ==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIICKzCCAdWgAwIBAgIJAM8DxRNtPj90MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMTEwODEyMjA1MTIzWhcNMTIwODExMjA1MTIzWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANcNmgm4YlSUAr2xdWei5aRU/DbWtsQ47gjkv28Ekje3ob+6q0M+D5phwYDcv9ygYmuJ5wOi1cPprsWdFWmvSusCAwEAAaOBpzCBpDAdBgNVHQ4EFgQUzyBR9+vE8bygqvD6CZ/w6aQPikMwdQYDVR0jBG4wbIAUzyBR9+vE8bygqvD6CZ/w6aQPikOhSaRHMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGSCCQDPA8UTbT4/dDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA0EAIQuPLA/mlMJAMF680kL7reX5WgyRwAtRzJK6FgNjE7kRaLZQ79UKYVYa0VAyrRdoNEyVhG4tJFEiQJzaLWsl/A==</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature><saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:email" SPNameQualifier="example.net">randomuser@example.com</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData InResponseTo="#mpjibjdppiodcpciaefmdahiipjpcghdcfjodkbi" NotOnOrAfter="2011-08-11T23:43:34Z" Recipient="https://www.example.net/a/example.com/acs"></saml:SubjectConfirmationData></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="2011-08-11T23:38:04Z" NotOnOrAfter="2011-08-11T23:43:34Z"><saml:AudienceRestriction><saml:Audience>example.net</saml:Audience></saml:AudienceRestriction></saml:Conditions><saml:AuthnStatement AuthnInstant="2011-08-11T23:38:34Z" SessionNotOnOrAfter="2011-08-12T07:38:34Z"><saml:AuthnContext><saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml:AuthnContextClassRef></saml:AuthnContext></saml:AuthnStatement></saml:Assertion>'

class XmlTest(unittest.TestCase):
    def _test(self, got, exp):
        #TODO: Maybe provide more meaningful output. YAGNI?
        msg = 'Did not get expected XML.\nExp: %s\nGot: %s' % (exp, got)
        self.assertEqual(exp, got, msg)

    def _test_template(self, template_source, parameters, exp):
        got = string.Template(template_source).substitute(parameters)
        self._test(got, exp)

class TestSigning(XmlTest):
    def test1(self):
        signature_xml = get_signature_xml("this is a test", 'abcd' * 10)
        expected_xml = '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod><ds:Reference URI="#abcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod><ds:DigestValue>+ia+Gd5r/5P3C8IwhDTkpEC7rQI=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>NsgZCvIcx4E1w1NHauICZ6XOr2LnRGVJxg/e2K1+fCwBKehcExfSizi2iTZfOU66P71R1GOtUL0uCWpixN1T5w==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIICKzCCAdWgAwIBAgIJAM8DxRNtPj90MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMTEwODEyMjA1MTIzWhcNMTIwODExMjA1MTIzWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANcNmgm4YlSUAr2xdWei5aRU/DbWtsQ47gjkv28Ekje3ob+6q0M+D5phwYDcv9ygYmuJ5wOi1cPprsWdFWmvSusCAwEAAaOBpzCBpDAdBgNVHQ4EFgQUzyBR9+vE8bygqvD6CZ/w6aQPikMwdQYDVR0jBG4wbIAUzyBR9+vE8bygqvD6CZ/w6aQPikOhSaRHMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGSCCQDPA8UTbT4/dDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA0EAIQuPLA/mlMJAMF680kL7reX5WgyRwAtRzJK6FgNjE7kRaLZQ79UKYVYa0VAyrRdoNEyVhG4tJFEiQJzaLWsl/A==</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature>'
        self._test(signature_xml, expected_xml)

class TestAssertion(XmlTest):
    def test_assertion(self):
        # This test simply verifies that the template isn't bad.
        exp = ASSERTION_XML
        self._test_template(ASSERTION, ASSERTION_PARAMS, exp)

    def test_signed_assertion(self):
        # This test verifies that the assertion got signed properly.
        params = {}
        params.update(ASSERTION_PARAMS)
        signature = get_signature_xml(ASSERTION_XML, '_7ccdda8bc6b328570c03b218d7521772998da45374')
        params['SIGNATURE'] = signature
        self._test_template(ASSERTION, params, SIGNED_ASSERTION_XML)
