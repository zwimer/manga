class Singleton(type):
    _objs = {}  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._objs:
            cls._objs[cls] = super().__call__(*args, **kwargs)
        return cls._objs[cls]
