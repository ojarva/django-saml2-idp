"""
Signing code goes here.
"""
# python:
import hashlib
import string
# other libraries:
import M2Crypto
# this app:
import saml2idp_settings
# until we yank the old stuff entirely:
from signing_old import *

# NOTE #1: OK, encoding XML into python is not optimal.
#   However, this is the easiest way to get canonical XML...
#   ...at least, without requiring other XML-munging libraries.
#   I'm not including the indentation in the XML itself, because that messes
#   with its canonicalization. This is meant to produce one long one-liner.
#   I am indenting each line in python, for my own happiness. :)
# NOTE #2: I'm using string.Template, rather than Django Templates, to avoid
#   the overhead of loading Django's template code. (KISS, baby.)
SIGNED_INFO = (
    '<ds:SignedInfo>'
        '<ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod>'
        '<ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod>'
        '<ds:Reference URI="#${REFERENCE_URI}">'
            '<ds:Transforms>'
                '<ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform>'
                '<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform>'
            '</ds:Transforms>'
            '<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>'
            '<ds:DigestValue>${SUBJECT_DIGEST}</ds:DigestValue>'
        '</ds:Reference>'
    '</ds:SignedInfo>'
)
SIGNATURE = (
    '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">'
        '${SIGNED_INFO}'
    '<ds:SignatureValue>${RSA_SIGNATURE}</ds:SignatureValue>'
    '<ds:KeyInfo>'
        '<ds:X509Data>'
            '<ds:X509Certificate>${CERTIFICATE}</ds:X509Certificate>'
        '</ds:X509Data>'
    '</ds:KeyInfo>'
'</ds:Signature>'
)

def _nice(src):
    """ Returns src formatted nicely for our XML. """
    return src.encode('base64').replace('\n', '')

def get_signature_xml(subject, reference_uri):
    """
    Returns XML Signature for subject.
    """
    private_key_file = saml2idp_settings.SAML2IDP_PRIVATE_KEY_FILE
    certificate_file = saml2idp_settings.SAML2IDP_CERTIFICATE_FILE

    # Hash the subject.
    subject_hash = hashlib.sha1()
    subject_hash.update(subject)
    subject_digest = _nice(subject_hash.digest())

    # Create signed_info.
    signed_info = string.Template(SIGNED_INFO).substitute({
        'REFERENCE_URI': reference_uri,
        'SUBJECT_DIGEST': subject_digest,
        })

    # "Digest" the signed_info.
    info_hash = hashlib.sha1()
    info_hash.update(signed_info)
    info_digest = _nice(info_hash.digest())

    # RSA-sign the signed_info digest.
    private_key = M2Crypto.EVP.load_key(private_key_file)
    private_key.sign_init()
    private_key.sign_update(info_digest)
    rsa_signature = _nice(private_key.sign_final())

    # Load the certificate.
    certificate = M2Crypto.X509.load_cert(certificate_file)
    cert_data = ''.join(certificate.as_pem().split('\n')[1:-2])

    # Put the signed_info and rsa_signature into the XML signature.
    signature_xml = string.Template(SIGNATURE).substitute({
        'RSA_SIGNATURE': rsa_signature,
        'SIGNED_INFO': signed_info,
        'CERTIFICATE': cert_data,
        })

    return signature_xml
