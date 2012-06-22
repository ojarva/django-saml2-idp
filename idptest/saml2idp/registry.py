"""
Registers and loads Processor classes from settings.
"""
# Python imports
import logging
# Django imports
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
# Local imports
import exceptions
import saml2idp_metadata

# Setup logging
logger = logging.getLogger(__name__)

def get_processor(dottedpath):
    """
    Get an instance of the processor with dottedpath.

    For example:
    >>> x = get_processor('saml2idp.demo.Processor')
    """
    try:
        dot = dottedpath.rindex('.')
    except ValueError:
        raise ImproperlyConfigured('%s isn\'t a processors module' % dottedpath)
    sp_module, sp_classname = dottedpath[:dot], dottedpath[dot+1:]
    try:
        mod = import_module(sp_module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing processors %s: "%s"' % (sp_module, e))
    try:
        sp_class = getattr(mod, sp_classname)
    except AttributeError:
        raise ImproperlyConfigured('processors module "%s" does not define a "%s" class' % (sp_module, sp_classname))

    instance = sp_class()
    return instance

def find_processor(request):
    """
    Returns the Processor instance that is willing to handle this request.
    """
    for name, sp_config in saml2idp_metadata.SAML2IDP_REMOTES.items():
        proc = get_processor(sp_config['processor'])
        try:
            if proc.can_handle(request):
                return proc
        except exceptions.CannotHandleAssertion, e:
            # Log these, but keep looking.
            logger.debug('%s %s' % (proc, e))
    raise exceptions.CannotHandleAssertion('None of the processors in SAML2IDP_REMOTES could handle this request.')

#class ProcessorRegistry(object):
#    """
#    Manages processors configured in settings.SAML2IDP_PROCESSOR_CLASSES.
#    """
#    def __init__(self):
#        self._processors = []
#        self._logger = logging.getLogger(self.__class__.__name__)
#
#    def load_processors(self):
#        """
#        Populate processors lists from settings.SAML2IDP_PROCESSOR_CLASSES.
#        Code informed heavily by django.core.handlers.base.BaseHandler.
#        Must be called after the environment is fixed (see __call__).
#        """
#        from saml2idp.saml2idp_settings import SAML2IDP_PROCESSOR_CLASSES
#        from django.core import exceptions
#        self._processors = []
#
#        processors = []
#        for processors_path in SAML2IDP_PROCESSOR_CLASSES:
#            sp_instance = get_processor(processors_path)
#            processors.append(sp_instance)
#
#        # We only assign to this when initialization is complete as it is used
#        # as a flag for initialization being complete.
#        self._processors = processors
#
#    def find_processor(self, request):
#        """
#        Return the first processor that is willing to handle this request.
#        """
#        if not self._processors:
#            self.load_processors()
#        for proc in self._processors:
#            try:
#                if proc.can_handle(request):
#                    return proc
#            except exceptions.CannotHandleAssertion, e:
#                # Log these, but keep looking.
#                self._logger.debug('%s %s' % (proc, e))
#        raise exceptions.CannotHandleAssertion('None of the SAML2IDP_PROCESSOR_CLASSES could handle this request.')
