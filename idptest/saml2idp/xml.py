"""
Functions for creating XML output.
"""
import logging
from xml_templates import ASSERTION, RESPONSE

# Setup logging.
logging.basicConfig(filename='saml2idp.log', format='%(asctime)s: %(message)s', level=logging.DEBUG)

def _get_xml(template, context):
    raw = template.render(context)
    stripped = ws_strip(raw)
    canned = canonicalize(stripped)
    return canned

def get_assertion_xml(saml_request, assertion, issuer, signed=False):
    t = Template(
        '{% load samltags %}'
        '{% assertion_xml saml_request assertion issuer signature_xml %}'
    )
    c = Context({
        'saml_request': saml_request,
        'assertion': assertion,
        'issuer': issuer,
        'signature_xml': None,
    })
    unsigned = _get_xml(t, c)
    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(create_signature(unsigned, assertion['id']))
    c['signature_xml'] = signature_xml
    signed = _get_xml(t, c)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed

def get_response_xml(saml_request, saml_response, assertion, issuer, signed=False):
    t = Template(
        '{% load samltags %}'
        '{% response_xml saml_request saml_response assertion_xml issuer signature_xml %}'
    )

    assertion_xml = get_assertion_xml(saml_request, assertion, issuer, signed)

    c = Context({
        'saml_request': saml_request,
        'saml_response': saml_response,
        'assertion_xml': assertion_xml,
        'issuer': issuer,
        'signature_xml': None,
    })
    unsigned = _get_xml(t, c)
    logging.debug('Unsigned:')
    logging.debug(unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(create_signature(unsigned, saml_response['id']))
    c['signature_xml'] = signature_xml
    signed = _get_xml(t, c)

    logging.debug('Signed:')
    logging.debug(signed)
    return signed
