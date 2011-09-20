"""
SAML 2.0 AuthnRequest to Response Handler and various processors.
"""
from django.utils.importlib import import_module

class ProcessorRegistry(object):
    """
    Manages processors configured in settings.SAML2IDP_PROCESSOR_CLASSES.
    """
    def __init__(self):
        self._processors = []

    def load_processors(self):
        """
        Populate processors lists from settings.SAML2IDP_PROCESSOR_CLASSES.
        Code informed heavily by django.core.handlers.base.BaseHandler.
        Must be called after the environment is fixed (see __call__).
        """
        from saml2idp_settings import SAML2IDP_PROCESSOR_CLASSES
        from django.core import exceptions
        self._processors = []

        processors = []
        for processors_path in SAML2IDP_PROCESSOR_CLASSES:
            try:
                dot = processors_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured('%s isn\'t a processors module' % processors_path)
            sp_module, sp_classname = processors_path[:dot], processors_path[dot+1:]
            try:
                mod = import_module(sp_module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured('Error importing processors %s: "%s"' % (sp_module, e))
            try:
                sp_class = getattr(mod, sp_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured('processors module "%s" does not define a "%s" class' % (sp_module, sp_classname))

            sp_instance = sp_class()
            processors.append(sp_instance)

        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._processors = processors

    def find_processor(self, request):
        """
        Return the first processor that is willing to handle this request.
        """
        if not self._processors:
            self.load_processors()
        for proc in self._processors:
            if proc.can_handle(request):
                return proc
        raise Exception('No SAML 2.0 processor is configured to handle this request.')

class GenericProcessor(object):
    """
    Generic SAML 2.0 AuthnRequest to Response Handler Processor.
    Sub-classes should provide Service Point-specific functionality.
    """
    def can_handle(self, request):
        return False

generic = GenericProcessor
