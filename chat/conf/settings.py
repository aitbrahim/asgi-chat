from starlette.config import Config


config = Config()

CHANNEL_LAYERS_CONFIG = config('CHANNEL_LAYERS_CONFIG', cast=dict, default={
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },

})