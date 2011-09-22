import base

class processor(base.processor):
    """
    SalesForce.com-specific SAML 2.0 AuthnRequest to Response Handler Processor.
    """
    def can_handle(self, request):
        return True

    def _determine_audience(self):
        self._audience = 'https://saml.salesforce.com'
