# Python imports:
import logging
import time
import uuid
# Django/other library imports:
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
# saml2idp app imports:
import codex
import saml2idp_settings
import validation
import xml_parse
import xml_render

def get_random_id():
    random_id = uuid.uuid4().hex
    return random_id

def get_time_string(delta=0):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time() + delta))

@login_required
@csrf_view_exempt
@csrf_response_exempt
def login(request):
    """
    Receives a SAML 2.0 AuthnRequest from a Service Point and
    presents a SAML 2.0 Assertion for POSTing back to the Service Point.
    """
    # Receive the AuthnRequest.
    if request.method == 'POST':
        msg = request.POST['SAMLRequest']
        relay_state = request.POST['RelayState']
    else:
        msg = request.GET['SAMLRequest']
        relay_state = request.GET['RelayState']

    # Read the request.
    xml = codex.decode_base64_and_inflate(msg)
    logging.debug('login view received xml: ' + xml)
    request_params = xml_parse.parse_request(xml)
    validation.validate_request(request_params)

    # Build the Assertion.
    system_params = {
        'ISSUER': saml2idp_settings.SAML2IDP_ISSUER,
    }

# For the moment, leave this out. YAGNI? See xml_templates.py.
#    # Guess at the Audience.
#    audience = request_params['DESTINATION']
#    if not audience:
#        audience = request_params['PROVIDER_NAME']

    assertion_id = get_random_id()
    assertion_params = {
        'ASSERTION_ID': assertion_id,
        'ASSERTION_SIGNATURE': '', # it's unsigned
        'AUDIENCE': audience,
        'AUTH_INSTANT': get_time_string(),
        'ISSUE_INSTANT': get_time_string(),
        'NOT_BEFORE': get_time_string(),
        'NOT_ON_OR_AFTER': get_time_string(5), # minutes
        'SESSION_NOT_ON_OR_AFTER': get_time_string(8 * 60), # 8 hours
        'SP_NAME_QUALIFIER': audience,
        'SUBJECT_EMAIL': request.user.email
    }
    assertion_params.update(system_params)
    assertion_params.update(request_params)

    # Build the SAML Response.
    assertion_xml = xml_render.get_assertion_xml(assertion_params, signed=True)
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
    tv = {
        'acs_url': acs_url,
        'saml_response': encoded_xml,
        'relay_state': relay_state,
    }
    return render_to_response('saml2idp/login.html', tv)

@csrf_view_exempt
def logout(request):
    """
    Receives a SAML 2.0 LogoutRequest from a Service Point.
    """
    tv = {}
    return render_to_response('saml2idp/logout.html', tv)

def logged_out(request):
    """
    Presents a standard logged-out message, in case the Service Point doesn't
    have its own logged-out page.
    """
    tv = {}
    return render_to_response('saml2idp/logged_out.html', tv)
