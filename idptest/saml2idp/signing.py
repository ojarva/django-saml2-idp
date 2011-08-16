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
from xml_templates import SIGNED_INFO, SIGNATURE
# until we yank the old stuff entirely:
from signing_old import *


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
