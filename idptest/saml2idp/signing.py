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

SIGNATURE = (
    '${SIGNED_INFO}\n'
    '${RSA_SIGNATURE}\n'
    '${CERTIFICATE}\n'
    )
SIGNED_INFO = 'SUBJECT_DIGEST = ${SUBJECT_DIGEST}'

def get_signature_xml(subject):
    """
    Returns XML Signature for subject.
    """
    private_key_file = saml2idp_settings.SAML2IDP_PRIVATE_KEY_FILE
    certificate_file = saml2idp_settings.SAML2IDP_CERTIFICATE_FILE

    # Hash the subject.
    subject_hash = hashlib.sha1()
    subject_hash.update(subject)
    subject_digest = subject_hash.digest().encode('base64')

    # Create signed_info.
    signed_info = string.Template(SIGNED_INFO).substitute({
        'SUBJECT_DIGEST': subject_digest,
        })

    # "Digest" the signed_info.
    info_hash = hashlib.sha1()
    info_hash.update(signed_info)
    info_digest = info_hash.digest().encode('base64')

    # RSA-sign the signed_info digest.
    private_key = M2Crypto.RSA.load_key(private_key_file)
    private_key.sign_init()
    private_key.sign_update(signed_info_digest)
    rsa_signature = private_key.sign_final()

    # Load the certificate.
    certificate = M2Crypto.X509.load_cert(certificate_file)

    # Put the signed_info and rsa_signature into the XML signature.
    signature_xml = string.Template(SIGNATURE).substitute({
        'RSA_SIGNATURE': rsa_signature,
        'SIGNED_INFO': signed_info,
        'CERTIFICATE': certificate,
        })

    return signature_xml
