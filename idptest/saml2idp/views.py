# Python imports:
import time
# Django/other library imports:
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
import lasso
# saml2idp app imports:
import codex
import saml2idp_settings
import validation

def get_random_id():
    #TODO: Make this work.
    return "a" * 40;

def get_time_string(delta=0):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time() + delta))

@login_required
@csrf_view_exempt
@csrf_response_exempt
def landing(request):
    """
    Receives a SAML 2.0 AuthnRequest from a Service Point and
    presents a SAML 2.0 Assertion for POSTing back to the Service Point.
    """
    # Receive the AuthnRequest.
    if request.method == 'POST':
        msg = request.POST['SAMLRequest']
        rstate = request.POST['RelayState']
    else:
        msg = request.GET['SAMLRequest']
        rstate = request.GET['RelayState']

    xml = codex.decode_base64_and_inflate(msg)
    req = lasso.Samlp2AuthnRequest()
    req.initFromXml(xml)

    validation.validate_request(req)

    # Build the assertion.
    assertion = lasso.Saml2Assertion()
    assertion.iD = get_random_id()
    assertion.issueInstant = get_time_string()
    issuer = lasso.Saml2NameID()
    issuer.content = saml2idp_settings.SAML2IDP_ISSUER
    assertion.issuer = issuer
    assertion.version = "2.0"

    # Build the assertion subject.
    subject = lasso.Saml2Subject()
    name_id = lasso.Saml2NameID()
    name_id.sPNameQualifier = req.issuer.content
    name_id.format = 'urn:oasis:names:tc:SAML:2.0:nameid-format:email'
    name_id.content = "someone@example.net"
    subject.name_id = [name_id]

    assertion.subject = subject

    # Build the response that wraps it.
    resp = lasso.Samlp2Response()
    resp.assertion = [assertion]

    # Present sent the Assertion. (Because Django has already enforced login.)
    tv = {
        'saml_request': req,
        'saml_response': resp,
        'relay_state': rstate,
    }
    return render_to_response('saml2idp/logged_in.html', tv)

def logged_in(request):
    pass

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
