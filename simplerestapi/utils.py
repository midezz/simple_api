def cached_property(func):
    def item_property(self):
        if hasattr(self, f'_{func.__name__}'):
            return getattr(self, f'_{func.__name__}')
        else:
            parameter = func(self)
            setattr(self, f'_{func.__name__}', parameter)
            return parameter

    return property(item_property)
