class ConfigEndpointError(Exception):
    def __init__(self, message, errors):
        message_errors = message + '\n' + '\n'.join(errors)
        super().__init__(message_errors)
        self.errors = errors
