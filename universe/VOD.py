from .util import convert_timestr, warning

class VOD():
    """
    Class VOD
    
    Save information of a VOD.
    """
    FETCHED = False # Must be True if and only if everything is loaded.

    def __init__(self, vod_no):
        self.vod_no = vod_no
        self.FETCHED = False
    
    def SetTitle(self, title):
        """ (VOD, String) -> NoneType
        Set the title of current VOD
        """
        self.title = title

    def SetThumbnail(self, landscape = '', portrait = '', square = ''):
        """ (VOD, String?, String?, String?) -> NoneType
        Set thumbnails images of current VOD
        """
        self.thumb_landscape = landscape
        self.thumb_portrait = portrait
        self.thumb_square = square
    
    def SetCDNInfo(self, filename, assertion, playready, widevine, fairplay):
        self.filename = filename
        self.CDN_assertion = assertion
        self.CDN_playready = playready
        self.CDN_widevine = widevine
        self.CDN_fairplay = fairplay

    def SetDRMInfo(self, playready, widevine, fairplay, fairplay_cert):
        self.DRM_playready = playready
        self.DRM_widevine = widevine
        self.DRM_fairplay = fairplay
        self.DRM_fairplay_cert = fairplay_cert

    def SetSubtitle(self, ko = '', en = '', ja = '', cn = '', tw = ''):
        self.subtitle_ko = ko
        self.subtitle_en = en
        self.subtitle_ja = ja
        self.subtitle_cn = cn
        self.subtitle_tw    = tw

    def SetDuration(self, duration):
        """ (VOD, Integer) -> NoneType
        Set a durtaion time of current VOD
        """
        self.duration = duration
    
    def SetSeries(self, vod_series):
        """ (VOD, VODSeries) -> NoneType
        Set a series of current VOD as given VODSeries
        """
        self.series = vod_series
        vod_series.AddVod(self)

    def __str__(self):
        return "<VOD: ({}) \"{}\">".format(self.vod_no, self.title)

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
        self.vods[vod.vod_no] = vod

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

    def __str__(self):
        return "<VODSeries: ({}) \"{}\">".format(self.vod_series_no, self.title)

class VODModule():
    """
    Class VODModule

    A class to handle VOD
    """
    __SESS = None
    vod = {}        # Dictonary<planet_id, Dictionary<vod_no, VOD>>
    vod_series = {} # Dictonary<planet_id, Dictionary<vod_series_no, VODSeries>>

    def __processVODSeries(self, planet_id, video_series_obj):
        if video_series_obj["vod_series_no"] in self.vod_series[planet_id]:
            return False

        series = VODSeries(video_series_obj["vod_series_no"])
        series.SetTitle(video_series_obj["title"]["ko"])
        series.SetThumbnail(landscape = video_series_obj["thumbnail"].get("landscape", {}).get("s3path", ""),
                            portrait = video_series_obj["thumbnail"].get("portrait", {}).get("s3path", ""),
                            square = video_series_obj["thumbnail"].get("square", {}).get("s3path", ""))
        
        self.vod_series[planet_id][series.vod_series_no] = series
        return True
        
    def __processVOD(self, planet_id, vod_series, vod_no):
        vod = self.FetchVOD(planet_id, vod_no)
        vod.SetSeries(self.vod_series[planet_id][vod_series])

        self.vod[planet_id][vod_no] = vod
        return True
    
    def __processUnfetchedVOD(self, planet_id, vod_series, vod_no, vod_media):
        vod = VOD(vod_no)
        vod.SetTitle(vod_media["title"]["ko"])
        vod.SetDuration(vod_media["duration_time"])
        vod.SetThumbnail(landscape = vod_media["thumbnail"]["landscape"]["s3path"],
                            portrait = vod_media["thumbnail"]["portrait"]["s3path"],
                            square = vod_media["thumbnail"]["square"]["s3path"])

        vod.SetSeries(self.vod_series[planet_id][vod_series])

        self.vod[planet_id][vod_no] = vod
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
        Load VOD Series of the given planet_id.
        Return the number of loaded VOD series.
        """
        self.vod[planet_id] = dict()
        self.vod_series[planet_id] = dict()

        code, fns_obj, _ = self.__SESS.Get("https://api.universe-official.io/media/vodseries", {
            "planet_id": planet_id
        })

        if code != 0:
            raise Exception("Error while fetching vod series")
        
        media_obj = fns_obj["media"]

        count = 0
        for vod_series in media_obj["vod_series"]:
            if self.__processVODSeries(planet_id, vod_series):
                count += 1
        return count

    def LoadAllVOD(self, fetchVOD = True):
        """ (VODModule) -> NoneType
        Load a list of VOD with all currently loaded VOD series.
        Return the total number of VOD added.
        """
        count = 0
        for p in self.vod_series:
            count += self.LoadVODFromPlanet(p, fetchVOD = fetchVOD)

        return count

    def LoadVODFromPlanet(self, planet_id, fetchVOD = True):
        """ (VODModule, Integer) -> NoneType
        Load a list of VOD with specific planet id.
        Return the total number of VOD added.
        """

        # Check integrity before 
        if not planet_id in self.vod_series:
            raise Exception("The planet {} is not loaded".format(planet_id))

        count = 0
        for vs in self.vod_series[planet_id]:
            count += self.LoadVODFromSeries(planet_id, vs, fetchVOD = fetchVOD)
        
        return count
    
    def LoadVODFromSeries(self, planet_id, vod_series, fetchVOD = True):
        code, vb_obj, _ = self.__SESS.Get("https://api.universe-official.io/media/vodbridge", {
            "planet_id": planet_id,
            "vod_series_no": vod_series
        })

        if code != 0:
            raise Exception("Error while fetching vod series")
        
        count = 0
        vb_obj = vb_obj["media"]["vod_bridge"]
        for vod_no, vod_media in vb_obj["vod_media"].items():
            count += 1
            if fetchVOD:
                self.__processVOD(planet_id, vod_series, vod_no)
            else:
                self.__processUnfetchedVOD(planet_id, vod_series, vod_no, vod_media)

        return count


    def FetchVOD(self, planet_id, vod_no):
        """ (VODModule, Integer, Integer) -> NoneType
        Load a list of VOD with specific planet id and vod no.
        Return the total number of VOD added.
        """
        code, vod_obj, _ = self.__SESS.Get("https://api.universe-official.io/media/vodview", {
            "planet_id": planet_id,
            "media_no": vod_no
        })

        if code != 0:
            raise Exception("Error while fetching vod")
        v = vod_obj["media"]["vod_view"]
        s3 = v["vod_s3path"]
        vod = VOD(vod_no)
        vod.SetTitle(v["title"]["ko"])
        vod.SetDuration(s3["duration_time"])
        vod.SetThumbnail(landscape = v["thumbnail"]["landscape"]["s3path"],
                         portrait = v["thumbnail"]["portrait"]["s3path"],
                         square = v["thumbnail"]["square"]["s3path"])
        vod.SetDRMInfo(s3["playready_license_server_url"],
                       s3["widevine_license_server_url"],
                       s3["fairplay_license_server_url"],
                       s3["fairplay_cert_url"])
        vod.SetCDNInfo(s3["origin_filename"], s3["assertion"],
                       s3["cloudfront_dash_playready_url"],
                       s3["cloudfront_dash_widevine_url"],
                       s3["cloudfront_hls_fairplay_url"])
        vod.SetSubtitle(ko = v["vod_subtitle"]["ko"]["s3path"],
                        en = v["vod_subtitle"]["en"]["s3path"],
                        ja = v["vod_subtitle"]["ja"]["s3path"],
                        cn = v["vod_subtitle"]["zh-cn"]["s3path"],
                        tw = v["vod_subtitle"]["zh-tw"]["s3path"])

        return vod