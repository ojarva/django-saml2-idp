"""
Functions for creating XML output.
"""
import logging
import string
from xml_templates import ASSERTION, RESPONSE

# Setup logging.
logging.basicConfig(filename='saml2idp.log', format='%(asctime)s: %(message)s', level=logging.DEBUG)

def get_assertion_xml(parameters, signed=False):
    # Reset signature.
    params = {}
    params.update(parameters)
    params['ASSERTION_SIGNATURE'] = ''
    template = string.Template(ASSERTION)

    unsigned = template.substitute(params)
    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['ASSERTION_ID'])
    params['ASSERTION_SIGNATURE'] = signature_xml
    signed = template.substitute(params)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed

def get_response_xml(parameters, signed=False):
    """
    Returns XML for response, with signatures, if signed is True.
    """
    # Reset signatures.
    params = {}
    params.update(parameters)
    params['ASSERTION_SIGNATURE'] = ''
    params['RESPONSE_SIGNATURE'] = ''

    assertion_xml = get_assertion_xml(params, issuer, signed)

    template = string.Template(RESPONSE)
    unsigned = template.substitute(params)

    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['RESPONSE_ID'])
    params['RESPONSE_SIGNATURE'] = signature_xml
    signed = template.substitute(params)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed
