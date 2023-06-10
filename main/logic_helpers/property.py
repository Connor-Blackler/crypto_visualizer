class _Event(object):
    def __init__(self):
        self.callbacks = []

    def notify(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)

    def register(self, callback):
        self.callbacks.append(callback)
        return callback

    @classmethod
    def watched_property(cls, event_name, key):
        actual_key = '_%s' % key

        def getter(obj):
            return getattr(obj, actual_key)

        def setter(obj, value):
            event = getattr(obj, event_name)
            setattr(obj, actual_key, value)
            event.notify(value)

        return property(fget=getter, fset=setter)


class DataWithCallback(object):
    value = _Event.watched_property('changed', 'value')

    def __init__(self, data):
        self.changed = _Event()
        self.value = data


if __name__ == '__main__':
    my_data = DataWithCallback(42)
    my_data2 = DataWithCallback("bob")

    @my_data.changed.register
    @my_data2.changed.register
    def print_it(value):
        print(f'var changed to {value}')

    my_data.value = 10
    my_data2.value = "timmy"

    print(my_data.value)
    print(my_data2.value)
