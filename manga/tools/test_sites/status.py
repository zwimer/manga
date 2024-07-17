#
# Top Level Classes
#


class Status:
    pass


class Untested(Status):
    pass


class Tested(Status):
    pass


class Success(Tested):
    pass


class Failed(Tested):
    requires_exception: bool = False
    reason: str = ""  # Set by subclasses

    @classmethod
    def kind(cls):
        if cls.requires_exception:
            return cls.__name__
        return f"{cls.__name__}: {cls.reason}"


#
# Failure Classes
#


# Do not open URLs


class NoOpen(Failed):
    pass


class Skipped(NoOpen):
    reason = "This domain was skipped"


class Unknown(NoOpen):
    reason = "This website is for an unknown / unsupported domain."


class BadRequest(NoOpen):
    requires_exception = True
    reason = "Request failed"

    def __init__(self, why: Exception):
        self.exc: Exception = why


class MalformedURL(NoOpen):
    pass


class NotInt(MalformedURL):
    reason = "The URL's chapter is not an integer."


class HasVol(MalformedURL):
    reason = "The URL contains 'vol'; this is a bad sign"


class Pattern(MalformedURL):
    reason = "The URL contains a pattern that is dangerous"


# Open URLs


class ToOpen(Failed):
    pass


class Tiny(ToOpen):
    reason = "URL failed by default, it is too small"


class Exists(ToOpen):
    reason = "The URL is valid, but this site seems to be missing other chapters"


class Missing(ToOpen):
    reason = "Previous and future chapters exist, this one does not."


class Broken(ToOpen):
    reason = "This website does not seem to have any chapters of this manga."


class PointFive(ToOpen):
    reason = "There exists a .5 release before the current chapter"
