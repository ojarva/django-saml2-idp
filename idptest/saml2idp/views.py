# Python imports:
import time
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
    #TODO: Make this work.
    return "a" * 40;

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
    request_params = xml_parse.parse_request(xml)
    validation.validate_request(request_params)

    # Build the assertion.
    params = {
        'ISSUER': saml2idp_settings.SAML2IDP_ISSUER,
    }
    params.update(request_params)
    params = {
        'ASSERTION_ID': get_random_id(),
        'ISSUE_INSTANT': get_time_string(),
        'SP_NAME_QUALIFIER': '', #XXX
        'SUBJECT_EMAIL': '',
    }

    # Present sent the Assertion. (Because Django has already enforced login.)
    tv = {
        'acs_url': params['ACS_URL'],
        'saml_response': response_xml.encode('base64'),
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
