"""
SAML 2.0 AuthnRequest to Response Handler and various processors.

NOTE: Could this be done with middleware? Sure. But it's really only used by
      the views in this app, and the interface of a Saml2IdpProcessor doesn't
      match that of a Middleware class.
"""
from registry import ProcessorRegistry
from base import Saml2IdpProcessor as generic

# Import other specific processors here:
from salesforce import SalesForceProcessor as salesforce
