# This is basically just a label
# The decorator itself doesn't really do anything,
# it's just an easy way to label a particular function
# that we want to call
class ContentGenerator:
    def __init__(self, func):
        self.func = func

    def __call__(self, obj=None, *args, **kwargs):
        # If called on an instance of an object (i.e. the function is a method)
        if obj:
            return self.func(obj, *args, **kwargs)
        # If the func is just a normal function
        else:
            return self.func(*args, **kwargs)
