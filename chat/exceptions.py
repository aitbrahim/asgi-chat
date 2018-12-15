class InvalidChannelLayerError(ValueError):
    """
    Raised when a channel layer is configured incorrectly.
    """

    pass


class StopConsumer(Exception):
    """
    Raised when a consumer wants to stop and close down its application instance.
    """

    pass
