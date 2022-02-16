def cached_property(func):
    def get_property(self):
        if hasattr(self, f'_{func.__name__}'):
            return getattr(self, f'_{func.__name__}')
        else:
            parameter = func(self)
            setattr(self, f'_{func.__name__}', parameter)
            return parameter

    def set_property(self, value):
        setattr(self, f'_{func.__name__}', value)

    return property(get_property, set_property)
