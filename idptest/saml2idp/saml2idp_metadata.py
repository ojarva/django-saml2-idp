"""
Django Settings that more closely resemble SAML Metadata.

Detailed discussion is in doc/SETTINGS_AND_METADATA.txt.
"""
__all__ = [ 'SAML2IDP_CONFIG', 'SAML2IDP_REMOTES' ]
from django.conf import settings

try:
    SAML2IDP_CONFIG = settings.SAML2IDP_CONFIG
    SAML2IDP_CONFIG.update(overrides)
except:
    # Provide settings so that the demo will work out-of-the-box.
    SAML2IDP_CONFIG = {
        # Default metadata to configure this local IdP.
        'autosubmit': True,
        'certificate_file': '%s/keys/sample/sample-certificate.pem' % settings.PROJECT_ROOT,
        'private_key_file': '%s/keys/sample/sample-private-key.pem' % settings.PROJECT_ROOT,
        'issuer': 'http://127.0.0.1:8000',
        'signing': True,
    }

try:
    SAML2IDP_REMOTES = settings.SAML2IDP_REMOTES
except:
    # Provide settings so that the demo will work out-of-the-box.
    demoSpConfig = {
        'acs_url': 'http://127.0.0.1:9000/sp/acs/',
        'processor': 'saml2idp.demo.Processor',
        'links': {
            'deeplink': 'http://127.0.0.1:9000/sp/%s/',
        }
    }
    attrSpConfig = {
        'acs_url': 'http://127.0.0.1:9000/sp/acs/',
        'processor': 'saml2idp.demo.AttributeProcessor',
        'links': {
            'attr': 'http://127.0.0.1:9000/sp/%s/',
        },
    }
    SAML2IDP_REMOTES = {
        # Group of SP CONFIGs.
        # friendlyname: SP config
        'attr_demo': attrSpConfig,
        'demo': demoSpConfig,
    }
