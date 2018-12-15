from __future__ import unicode_literals

from . import DEFAULT_CHANNEL_LAYER

# from .exceptions import InvalidChannelLayerError


CHANNEL_LAYERS_CONFIG = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}


class ChannelLayerManager(object):
    """
    Takes settings of dictionary and initialise them
    """
    def __init__(self):
        self.backends = {}

    @property
    def configs(self):
        # Lazy load settings so we can be imported
        return CHANNEL_LAYERS_CONFIG

    def make_backend(self, name):
        """
        Instantiate channel layer.
        """
        config = self.configs[name].get("CONFIG", {})
        return self._make_backend(name, config)

    def _make_backend(self, name, config):
        # # Load the backend class
        # try:
        #     import importlib
        #     backend_class = __import__(self.configs[name]["BACKEND"])
        # except KeyError:
        #     raise InvalidChannelLayerError("No BACKEND specified for %s" % name)
        # except ImportError:
        #     raise InvalidChannelLayerError(
        #         "Cannot import BACKEND %r specified for %s"
        #         % (self.configs[name]["BACKEND"], name)
        #     )

        """
        Static import for now
        """
        from channels_redis.core import RedisChannelLayer
        # Initialise and pass config
        return RedisChannelLayer(**config)

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
