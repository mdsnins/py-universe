from universe import UserSession
from universe import config
from tests.test_util import *

def is_good(sess):
    code, data, msg = sess.Get("https://api.universe-official.io/planet/home", {"planet_id": 34})
    return code == 0

def test_user_initialize_with_access_token(at):
    try:
        sess = UserSession(access_token=at, refresh_token="")
    except Exception as e:
        fail("user_initialize_with_access_token", -1, str(e), "")
    
    if is_good(sess):
        success("user_initialize_with_access_token")
        return
    fail("user_initialize_with_access_token", -1, "Failed to communicate", "")

def test_user_initialize_with_refresh_token(rt):
    try:
        sess = UserSession(access_token="", refresh_token=rt)
    except Exception as e:
        fail("test_user_initialize_with_refresh_token", -1, str(e), "")
    
    if is_good(sess):
        success("test_user_initialize_with_refresh_token")
        return
    fail("test_user_initialize_with_refresh_token", -1, "Failed to communicate", "")

def do_test():
    config.SHOW_WARNING = True
    test_user_initialize_with_access_token(config.TEST_ACCESS_TOKEN)
    test_user_initialize_with_refresh_token(config.TEST_REFRESH_TOKEN)

do_test()

