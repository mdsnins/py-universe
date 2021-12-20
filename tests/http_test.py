from universe import Http
from universe import config
from tests.test_util import *

def test_http_set_token(token, key):
    try:
        x = Http(token, key)
    except Exception as e:
        fail("http_set_token", -1, str(e), "", True)
    success("http_set_token")
    return x

def test_http_refresh(UniverseHttp):
    # Retrieve Access Token
    code, data, extra = UniverseHttp.Post("https://auth.universe-official.io/refresh/")

    if code != 0:
        fail("http_refresh", code, data, extra, True)
    success("http_refresh")
    return data["auth"]["access_token"]

def test_http_update_access_token(UniverseHttp, access_token):
    try:
        UniverseHttp.UpdateToken(access_token)
    except Exception as e:
        fail("http_update_access_token", -1, str(e), "", True)
    success("http_update_access_token")
    return

def test_http_retrieve_planet_home(UniverseHttp, planet_id = 34):
    code, data, extra = UniverseHttp.Get("https://api.universe-official.io/planet/home", {"planet_id": planet_id})
    if code != 0:
        fail("http_retrieve_palent_home", code, data, extra, True)
    success("http_retrieve_planet_home")

def do_test():
    instance = test_http_set_token(config.TEST_REFRESH_TOKEN, config.JWE_KEY)
    access_token = test_http_refresh(instance)
    print("[+] Access-Token Retrieved: {}".format(access_token))
    test_http_update_access_token(instance, access_token)
    test_http_retrieve_planet_home(instance)
    success("===HTTP_TEST===")

do_test()

