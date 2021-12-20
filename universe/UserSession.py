from time import time
from .config import JWE_KEY
from .util import parse_bearer_token, warning, fail
from .Http import Http

class UserSession():
    """
    Class UserSession

    Stores the refresh token and Http class.
    All API calls must be initiated from this class.
    """

    __HTTP = None
    __ACCESS_TOKEN = ""
    __REFRESH_TOKEN = ""

    def __refreshToken(self):
        """ PRIVATE (UserSession) -> Boolean
        Refresh the access token using stored refresh token.
        If refresh token is invalid, it will raise the exception.
        If succeed 
        """
        if self.__REFRESH_TOKEN == "":
            return False

        try:
            r_exp, _, _, r_type = parse_bearer_token(self.__REFRESH_TOKEN)
            if r_type != "refresh":
                warning("Given token is not a refresh token")
                return False
        except:
            warning("Failed to parse refresh token")
            return False
        if r_exp and r_exp <= time():
            warning("Refresh token has been expired")
            return False

        if self.__HTTP is None:
            self.__HTTP = Http(self.__REFRESH_TOKEN, JWE_KEY)
        else:
            self.__HTTP.UpdateToken(self.__REFRESH_TOKEN)

        code, data, _ = self.__HTTP.Post("https://auth.universe-official.io/refresh/")
        if code != 0:
                return False
        
        self.__ACCESS_TOKEN = data["auth"]["access_token"]
        self.__HTTP.UpdateToken(self.__ACCESS_TOKEN)

        return True

    def __init__(self, access_token = "", refresh_token = ""):
        a_exp, a_no, a_id, a_type = None, None, None, None
        r_exp, r_no, r_id, r_type = None, None, None, None

        try:
            a_exp, a_no, a_id, a_type = parse_bearer_token(access_token)
            self.__ACCESS_TOKEN = access_token
        except:
            pass
        try:
            r_exp, r_no, r_id, r_type = parse_bearer_token(refresh_token)
            self.__REFRESH_TOKEN = refresh_token
        except:
            pass

        if (a_exp is None) and (r_exp is None):
            raise Exception("Both of access token and refresh token is invalid")
        
        if not a_exp or a_exp <= time():
            # when access token is expired
            warning("Access token has been expired")
            if r_exp is None or r_exp <= time():
                warning("Refresh token is also invalid, failed")
                raise Exception("Fail to initialize with given tokens")
            refresh = self.__refreshToken()
            if not refresh:
                raise Exception("Failed to issue a new access token")
            warning("Refreshed! New access token -> {}".format(self.__ACCESS_TOKEN))
            return
        elif a_exp:
            # when access token is not expired yet,
            if r_exp is not None:
                # and refresh token is given,
                if r_type != "refresh":
                    warning("Given token is not a refresh token.\nRefresh token will be ignored")
                    self.__REFRESH_TOKEN = ""
                if r_no != a_no:
                    warning("The account_no is not matching: (at vs rt) : ({} vs {})\nRefresh token will be ignored".format(a_no, r_no))
                    self.__REFRESH_TOKEN = ""
                if r_id != a_id:
                    warning("The np_game_account_id is not matching: (at vs rt) : ({} vs {})\nRefresh token will be ignored".format(a_id, r_id))
                    self.__REFRESH_TOKEN = ""
        self.__HTTP = Http(self.__ACCESS_TOKEN, JWE_KEY)

    def Get(self, target, query = {}):
        """ (UserSession, String, Object) -> (Int, Object | String, NoneType | Object | String)
        The wrapper function of Http.Get.
        Extended to refresh access token.
        """
        assert(self.__HTTP is not None)
        
        code, data, msg = self.__HTTP.Get(target, query)
        if code == 9999 and self.__refreshToken():
            warning("Refreshed! New access token -> {}".format(self.__ACCESS_TOKEN))
            return self.Get(target, query)
        return code, data, msg
    
    def Post(self, target, query = {}):
        """ (UserSession, String, Object) -> (Int, Object | String, NoneType | Object | String)
        The wrapper function of Http.Post.
        Extended to refresh access token.
        """
        assert(self.__HTTP is not None)
        
        code, data, msg = self.__HTTP.Post(target, query)
        if code == 9999 and self.__refreshToken():
            warning("Refreshed! New access token -> {}".format(self.__ACCESS_TOKEN))
            return self.Get(target, query)
        return code, data, msg
    


                       


