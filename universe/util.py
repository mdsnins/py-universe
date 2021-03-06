import base64
import json
from datetime import datetime

from . import config

def parse_bearer_token(bearer):
    parts = bearer.split('.')
    if len(parts) != 3:
        raise Exception("Not a valid JWT")
    if parts[0] != "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9":
        raise Exception("Invalid header")
    try:
        payload = json.loads(ub64d(parts[1]))
        return payload["exp"], int(payload["account_no"]), payload["np_game_account_id"], payload["type"]
    except:
        raise Exception("Error while parsing payload")
    assert(False) # unreachable

def convert_timestr(timestr):
    if timestr[-3] != ":":
        timestr = timestr[:-2] + ":" + timestr[-2:]
    return datetime.fromisoformat(timestr) \
                   .astimezone().strftime("%Y/%m/%d (%a) %H:%M:%S")

def b64e(plaintext, charset='latin-1'):
    return base64.b64encode(plaintext.encode(charset)).decode()

def b64d(base64text, charset='latin-1'):
    return base64.b64decode(base64text + '=' * (4 - len(base64text) % 4)).decode(charset)

# url-safe base64
def ub64e(plaintext, charset='latin-1'):
    return base64.urlsafe_b64encode(plaintext.encode(charset)).decode()

# https://stackoverflow.com/a/9956217
def ub64d(base64text, charset='latin-1'):
    return base64.urlsafe_b64decode(base64text + '=' * (4 - len(base64text) % 4)).decode(charset)

# https://stackoverflow.com/a/26853961
def merge(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z

# Logging related
def warning(msg):
    if not config.SHOW_WARNING: # Check warning log level
        return
    print("<py-universe.warn> {}".format(msg))

def fail(msg):
    print("<py-universe.fail> {}".format(msg))
