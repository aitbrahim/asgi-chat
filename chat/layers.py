from __future__ import unicode_literals

from . import DEFAULT_CHANNEL_LAYER

from .exceptions import InvalidChannelLayerError
import settings
import importlib

class ChannelLayerManager(object):
    """
    Takes settings of dictionary and initialise them
    """
    def __init__(self):
        self.backends = {}

    @property
    def configs(self):
        # Lazy load settings so we can be imported
        return settings.CHANNEL_LAYERS_CONFIG

    def make_backend(self, name):
        """
        Instantiate channel layer.
        """
        config = self.configs[name].get("CONFIG", {})
        return self._make_backend(name, config)

    def _make_backend(self, name, config):
        # Load the backend class
        try:
            _mod = self.configs[name]["BACKEND"].split(".")
            backend_module = importlib.import_module(".".join(_mod[:-1]))
            backend_class = getattr(backend_module, _mod[-1])
        except KeyError:
            raise InvalidChannelLayerError("No BACKEND specified for %s" % name)
        except ImportError:
            raise InvalidChannelLayerError(
                "Cannot import BACKEND %r specified for %s"
                % (self.configs[name]["BACKEND"], name)
            )

        # """
        # Static import for now
        # """
        # from channels_redis.core import RedisChannelLayer
        # Initialise and pass config
        return backend_class(**config)

    def __getitem__(self, key):
        if key not in self.backends:
            self.backends[key] = self.make_backend(key)
        return self.backends[key]

    def __contains__(self, key):
        return key in self.configs

    def set(self, key, layer):
        """
        Sets an alias to point to a new ChannelLayerWrapper instance, and
        returns the old one that it replaced. Useful for swapping out the
        backend during tests.
        """
        old = self.backends.get(key, None)
        self.backends[key] = layer
        return old


def get_channel_layer(alias=DEFAULT_CHANNEL_LAYER):
    try:
        return channel_layers[alias]
    except KeyError:
        return None


# Default global instance of the channel layer manager
channel_layers = ChannelLayerManager()
