import requests
import json

from authlib.jose import JsonWebEncryption, jwt 
from time import time
from .util import merge, parse_bearer_token

class Http():
    """
    Class Http

    Manipulate the API calls as real application.
    Must be initiated with Bearer string and symmetry key for JWE.
    """

    ACCOUNT_NO = 0
    NP_GAME_ACCOUNT_ID = ""
    BEARER = ""
    EXP = -1

    JWE = None
    KEK = ""

    __PROXY = None
    __VERIFY = True

    def __generateJWE(self, jwe_payload):
        """ PRIVATE (Http, Object) -> String
        Create a JWE string with given jwe_payload and user authorities.
        """
        real_payload = merge({
            "account_no": self.ACCOUNT_NO,
            "np_game_account_id": self.NP_GAME_ACCOUNT_ID
        }, jwe_payload)

        # inner JWT (will be JWE payload)
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        jwt_str = jwt.encode(header, real_payload, bytes(bytearray(self.KEK))).decode()

        # generate real JWE
        header = {
            "alg": "A256KW",
            "enc": "A256CBC-HS512",
            "zip": "DEF",
            "typ": "JWT"
        }
        payload = jwt_str.encode("utf-8-sig") # BOM is required
        return self.JWE.serialize_compact(header, payload, self.KEK).decode()

    def __handleResponse(self, resp):
        """ PRIVATE (Http, requests.Response) -> (Int, Object | String, NoneType | Object | String)
        Process the given HTTP Response object properly, then try to decrypt and parse.
        If there isn't any problem, (0, Object, None) will be returned.
        Otherwise, (Int, String, Object) will be returned.
        """
        if resp.status_code != 200:
            return 1098, "HTTP request failed", resp
        try:
            decrypted = self.JWE.deserialize_compact(resp.text, self.KEK)
            try:
                return 0, json.loads(decrypted["payload"].decode())["data"], None
            except:
                return 1002, "Abnormal API response", decrypted["payload"]
        except:
            return 1001, "Decryption failed", resp.text
        
        

    def __init__(self, bearer, key):
        """ (Http, String, List<Int>) -> NoneType
        Create new Http instance with specific bearer token and JWE KEK.
        """
        # check the validity of bearer token
        exp, no, id = parse_bearer_token(bearer)
        if exp <= time():
            raise Exception("Token has been expired")

        self.BEARER = bearer
        self.EXP = exp
        self.ACCOUNT_NO = no
        self.NP_GAME_ACCOUNT_ID = id
        self.JWE = JsonWebEncryption()
        self.KEK = key

    def UpdateToken(self, new_bearer, preserve_user = True):
        """ (Http, String, Boolean) -> NoneType
        Update current HTTP instance with new Bearer token.
        This can be used for refreshing token.
        Unless preserve_user is given as False, it checkes the user integrity
        """
        if self.BEARER == new_bearer:
            return

        # check the validity of bearer token
        exp, no, id = parse_bearer_token(new_bearer)
        if exp <= time():
            raise Exception("The new token has been expired")
        if preserve_user:
            if self.ACCOUNT_NO != no:
                raise Exception("account_no doesn't match")
            if self.NP_GAME_ACCOUNT_ID != id:
                raise Exception("np_game_account_id doesn't match")
        else:
            self.ACCOUNT_NO = no
            self.NP_GAME_ACCOUNT_ID = id

        self.BEARER = new_bearer
        self.EXP = exp

    def Get(self, target, query = {}):
        """ (Http, String, Dictionary<String, String>) -> (Int, Object)
        Attemp to call API GET request to target, and parse it.
        Returns code 0 and parsed result if succeed.
        Otherwise, returns a positive number with message.
        """
        
        if self.EXP < time():
            return 1099, "Token has been expired", None

        payload = self.__generateJWE(query)
        resp = requests.get(target, headers = {
            "Payload": payload,
            "Accept": "text/plain",
            "Authorization": "Bearer {}".format(self.BEARER),
            "User-Agent": None
            },
            proxies = self.__PROXY,
            verify = self.__VERIFY
        )

        return self.__handleResponse(resp)

    def Post(self, target, query = {}, data = {}):
        """ (Http, String, Dictionary<String, String>, Dictionary<String, String>) -> (Int, Object)
        Attemp to call API POST request to target, and parse it.
        Returns code 0 and parsed result if succeed.
        Otherwise, returns a positive number with message.
        """
        if self.EXP < time():
            return 1099, "Token has been expired", None

        payload = self.__generateJWE(query)
        body = self.__generateJWE(data)
        resp = requests.post(target, headers = {
            "Payload": payload,
            "Accept": "text/plain",
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(self.BEARER),
            "User-Agent": None
            },
            data = body,
            proxies = self.__PROXY,
            verify = self.__VERIFY
        )

        return self.__handleResponse(resp)

    def setProxy(self, https_proxy = ""):
        """ (Http, String) -> NoneType
        Set HTTPS proxy as given url.
        In addition, disable TLS ceritifcate verification.
        """
        self.__PROXY = {"https": https_proxy}
        self.__VERIFY = False

    def unsetProxy(self):
        """ (Http) -> NoneType
        Unset HTTPS proxy.
        In addition, enable TLS certificate verification.
        """
        self.__PROXY = None
        self.__VERIFY = True

