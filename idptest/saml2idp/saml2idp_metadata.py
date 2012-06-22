"""
Django Settings that more closely resemble SAML Metadata.

Detailed discussion is in doc/SETTINGS_AND_METADATA.txt.
"""
__all__ = [ 'SAML2IDP_CONFIG', 'SAML2IDP_REMOTES' ]
from django.conf import settings

###################
# Setup defaults. #
###################
SAML2IDP_CONFIG = {
    # Default metadata to configure this local IdP.
    'autosubmit': True,
    'certificate_file': 'keys/certificate.pem', # If using relative paths, be careful!
    'private_key_file': 'keys/private-key.pem', # If using relative paths, be careful!
    'issuer': 'http://127.0.0.1:8000',
    'signing': True,
}

# To test against the companion project, use these settings:
demoSpConfig = {
    'acs_url': 'http://127.0.0.1:9000/sp/acs/',
    'processor': 'saml2idp.demo.Processor',
    'links': {
        'deeplink': 'http://127.0.0.1:9000/sp/%s/',
    }
}

SAML2IDP_REMOTES = {
    # Group of SP CONFIGs.
    # friendlyname: SP config
    # 'sample': sampleSpConfig,
    'demo': demoSpConfig,
    # 'salesforce': salesforceSpConfig,
}

############################################
# Pull in overrides from project settings. #
############################################
try:
    overrides = settings.SAML2IDP_CONFIG
    SAML2IDP_CONFIG.update(overrides)
except:
    pass

try:
    remotes = settings.SAML2IDP_REMOTES
    SAML2IDP_REMOTES.update(remotes)
except:
    pass
