"""
Parse data from SAML 2.0 XML.
"""
from BeautifulSoup import BeautifulStoneSoup

def parse_request(request_xml):
    """
    Returns various parameters from request_xml in a dict.
    """
    soup = BeautifulStoneSoup(request_xml)
    request = soup.findAll()[0]
    tmp = {}
    params['ACS_URL'] = request['assertionconsumerserviceurl']
    params['REQUEST_ID'] = request['id']
    return params
