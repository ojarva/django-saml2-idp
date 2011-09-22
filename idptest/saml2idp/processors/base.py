from exceptions import UserNotAuthorized
import logging

class Saml2IdpProcessor(object):
    """
    Generic SAML 2.0 AuthnRequest to Response Processor.
    Sub-classes should provide Service Point-specific functionality.

    This class can be used directly by including this in settings.py:
        SAML2IDP_PROCESSOR_CLASSES = [
            'saml2idp.processors.generic'.
        ]
    """
    # Design note: I've tried to make this easy to sub-class and override
    # just the bits you need to override. I've made use of object properties,
    # so that your sub-classes have access to all information: use wisely.
    # Formatting note: These methods are alphabetized.

    def __init__(self):
        self._logger = logging.get_logger(self.__class__.__name__)

    def _determine_audience(self):
        """
        Determine the _audience.
        """
        self._audience = self.request_params.get('DESTINATION', None)
        if not self._audience:
            self.audience = self._request_params.get('PROVIDER_NAME', None)

    def _extract_saml_request(self):
        """
        Retrieves the _saml_request AuthnRequest from the _django_request.
        """
        self._saml_request = self._django_request.session['SAMLRequest']
        self._relay_state = self._django_request.session['RelayState']

    def _decode_request(self):
        """
        Decodes _request_xml from _saml_request.
        """
        self._request_xml = base64.b64decode(self._saml_request)
        self._logger.debug('Decoded XML: ' + self._request_xml)

    def _parse_request(self):
        """
        Parses various parameters from _request_xml into _request_params.
        """
        pass

    def _reset(self):
        """
        Initialize (and reset) object properties, so we don't risk carrying
        over anything from the last authentication.
        """
        self._django_request = None
        self._saml_request = None
        self._relay_state = None
        self._request = None
        self._request_xml = None
        self._request_params = None
        self._system_params = {
            'ISSUER': saml2idp_settings.SAML2IDP_ISSUER,
        }

    def _validate_request(self):
        """
        Validates the _saml_request. Sub-classes should override this and
        throw an Exception if the validation does not succeed.
        """
        pass

    def _validate_user(self):
        """
        Validates the User. Sub-classes should override this and
        throw an Exception if the validation does not succeed.
        """
        pass

    def can_handle(self, request):
        self._reset()
        self._django_request = dict(**request) #deepcopy and save for generate_request
        return False

    def generate_response(self):
        """
        Processes request and returns template variables suitable for a response.
        """
        self._extract_saml_request()

        # Read the request.
        self._decode_request()
        self._parse_request()

        # Validations:
        self._validate_request()
        self._validate_user()

        # Build the Assertion.
        self._determine_audience()

        email = get_email(request)

        assertion_id = get_random_id()
        session_index = request.session.session_key
        assertion_params = {
            'ASSERTION_ID': assertion_id,
            'ASSERTION_SIGNATURE': '', # it's unsigned
            'AUDIENCE': audience, # YAGNI? See note in xml_templates.py.
            'AUTH_INSTANT': get_time_string(),
            'ISSUE_INSTANT': get_time_string(),
            'NOT_BEFORE': get_time_string(-1 * HOURS), #TODO: Make these settings.
            'NOT_ON_OR_AFTER': get_time_string(15 * MINUTES),
            'SESSION_INDEX': session_index,
            'SESSION_NOT_ON_OR_AFTER': get_time_string(8 * HOURS),
            'SP_NAME_QUALIFIER': audience,
            'SUBJECT_EMAIL': email
        }
        assertion_params.update(system_params)
        assertion_params.update(request_params)

        # Build the SAML Response.
        assertion_xml = xml_render.get_assertion_salesforce_xml(assertion_params, signed=True)
        response_id = get_random_id()
        response_params = {
            'ASSERTION': assertion_xml,
            'ISSUE_INSTANT': get_time_string(),
            'RESPONSE_ID': response_id,
            'RESPONSE_SIGNATURE': '', # initially unsigned
        }
        response_params.update(system_params)
        response_params.update(request_params)

        # Present the Response. (Because Django has already enforced login.)
        acs_url = request_params['ACS_URL']

        response_xml = xml_render.get_response_xml(response_params, signed=True)
        encoded_xml = codex.nice64(response_xml)
        autosubmit = saml2idp_settings.SAML2IDP_AUTOSUBMIT
        tv = {
            'acs_url': acs_url,
            'saml_response': encoded_xml,
            'relay_state': relay_state,
            'autosubmit': autosubmit,
        }
