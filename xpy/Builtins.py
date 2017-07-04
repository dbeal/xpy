
import inspect

def typename(o):
    return type(o).__name__

def typedict(o):
    return type(o).__dict__

def EA(*args, **kwargs):
    return (args, kwargs)
    
def FL(msg):
    """Format {template} tokens with the caller's locals."""
    result = msg
    frame = inspect.currentframe()
    if frame is not None:
        back = frame.f_back
        d = dict(back.f_globals, **back.f_locals)
        result = msg.format(**d)
    return result

