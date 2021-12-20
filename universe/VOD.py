from .util import convert_timestr

class VOD():
    pass

class VODSeries():
    """
    Class VODSeries
    
    Save information of a VOD series.
    """
    def __init__(self, vod_series_no):
        self.vods = {}
        self.vod_series_no = vod_series_no
    
    def AddVod(self, vod):
        """ (VODSeries, VOD) -> NoneType
        Add a VOD to the current VODSeries.
        Must be called from VOD
        """
        self.vods[vod.vod_id] = vod

    def SetTitle(self, title):
        """ (VODSeries, String) -> NoneType
        Set the title of current VODSeries
        """
        self.title = title

    def SetThumbnail(self, landscape = '', portrait = '', square = ''):
        """ (VODSeries, String?, String?, String?) -> NoneType
        Set thumbnails images of current VODSeries
        """
        if landscape:
            self.thumb_landscape = landscape
        if portrait:
            self.thumb_portrait = portrait
        if square:
            self.thumb_square = square

class VODModule():
    """
    Class VODModule

    A class to handle VOD
    """
    __SESS = None
    vod = {}
    vod_series = {}

    def __processVODSeries(self, vs):
        if vs["vod_series_no"] in self.vod_series:
            return False

        series = VODSeries(vs["vod_series_no"])
        series.SetTitle(vs["title"]["ko"])
        series.SetThumbnail(landscape = vs["thumbnail"].get("landscape", {}).get("s3path", ""),
                            portrait = vs["thumbnail"].get("portrait", {}).get("s3path", ""),
                            square = vs["thumbnail"].get("square", {}).get("s3path", ""))
        
        self.vod_series[series.vod_series_no] = series
        return True

    def __init__(self, sess):
        """ (VODModule, UserSession) -> NoneType
        Initialize VODModule with given UserSession
        """
        self.__SESS = sess
        self.vod = {}
        self.vod_series = {}

    def LoadSeries(self, planet_id):
        """ (VODModule, Int) -> NoneType
        Load VOD Series of the given planet_id
        """
        if self.__SERIES_URL is None:
            raise Exception("VODModule cannot be used standalone")
        
        code, fns_obj, extra = self.__SESS.Get(self.__SERIES_URL, {
            "planet_id": planet_id
        })

        if code != 0:
            raise Exception("Error while fetching vod series")
        
        media_obj = fns_obj["media"]

        count = 0
        for vod_series in media_obj["vod_series"]:
            if self.__processVODSeries(vod_series):
                count += 1
        return count

