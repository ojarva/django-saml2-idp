"""
Validations for various conditions; or place-holders for future enhancement.
These methods should return nothing for success and raise an exception on
invalid conditions. (I think.)
"""

def validate_request(authn_req):
    #XXX: Validate against known/approved SPs?
    pass

def validate_user(request):
    """
    Stub. If you need per-user validation beyond simple authentication, then
    create a method with this signature and pass it into login_continue()
    as the 'validate_user_function' optional parameter.
    """
    pass
