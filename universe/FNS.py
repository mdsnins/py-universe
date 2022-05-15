from .util import convert_timestr

class FNSArtist():
    """
    Class FNSArtist
    
    Save information of an artist.
    """

    def __init__(self, account_no, artist_id, nickname, profile_picture):
        """ (FNSAttachment, String, Int, String,String) -> NoneType
        Initialize FNSArtist Object
        """
        self.feeds = {}
        self.attachments = {}
        self.account_no = account_no
        self.artist_id = artist_id
        self.nickname = nickname
        self.profile_picture = profile_picture
    
    def AddFeed(self, feed):
        """ (FNSArtist, FNSFeed) -> NoneType
        Add FNSFeed to current FNSArtist.
        Must be called from FNSFeed
        """
        self.feeds[feed.feed_id] = feed
    
    def AddAttachment(self, attachment):
        """ (FNSArtist, FNSAttachment) -> NoneType
        Add FNSAttachment to current FNSArtist.
        Must be called from FNSAttachment
        """
        self.attachments[attachment.attachment_id] =  attachment

    def __str__(self):
        return "<FNSArtist: ({}, {}) \"{}\"".format(self.artist_id, self.account_no, self.nickname)

class FNSAttachment():
    """
    Class FNSAttachment
    
    Save information of a single FNS feed attachment.
    """

    def __init__(self, attachment_id):
        """ (FNSAttachment, UUID) -> NoneType
        Initialize FNSAttachment Object
        """
        self.attachment_id = attachment_id
    
    def SetFile(self, url, type):
        """ (FNSFeed, string, string) -> NoneType
        Set the type and data of an attachment
        """
        self.file = url
        self.type = type

    def SetDate(self, create = '', publish = ''):
        """ (FNSFeed, datetime?, datetime?) -> NoneType
        Set the create and publish datetime.
        """
        if create:
            self.create_date = convert_timestr(create)
        if publish:
            self.publish_date = convert_timestr(publish)

    def SetArtist(self, artist):
        """ (FNSFeed, FNSArtist) -> NoneType
        Set FNSArtist to current FNSArtist
        """
        self.artist = artist
        artist.AddAttachment(self)

    def __str__(self):
        return "<FNSAttachment: ({}, {}) \"{}\">".format(self.attachment_id, self.type, self.artist.nickname)

class FNSFeed():
    """
    Class FNSFeed 

    Save information of a single FNS feed.
    This doesn't include comment information.
    """

    def __init__(self, feed_id):
        """ (FNSFeed, UUID) -> NoneType
        Initialize FNSFeed Object
        """
        self.feed_id = feed_id
        self.attachments = dict()
        self.tags = []

    def AddAttachment(self, attachment):
        """ (FNSFeed, FNSAttachment) -> NoneType
        Add FNSAttachment to current FNSFeed
        """
        self.attachments[attachment.attachment_id] = attachment

    def SetBody(self, body):
        self.body = body

    def SetDate(self, create = '', modify = '', publish = ''):
        """ (FNSFeed, datetime?, datetime?, datetime?) -> NoneType
        Set the create, modify, and publish datetime.
        """
        if create:
            self.create_date = convert_timestr(create)
        if modify:
            self.modify_date = convert_timestr(modify)
        if publish:
            self.publish_date = convert_timestr(publish)
    
    def SetArtist(self, artist):
        """ (FNSFeed, FNSArtist) -> NoneType
        Set FNSArtist to current FNSFeed
        """
        self.artist = artist
        artist.AddFeed(self)
    
    def AddTag(self, tag):
        """ (FNSFeed, String) -> NoneType
        Add a tag to current FNSFeed
        """
        self.tags.append(tag)

    def __str__(self):
        return "<FNSFeed: ({}) \"{}\">".format(self.feed_id, self.artist.nickname)

    def like():
        #TODO: implement
        pass

class FNSModule():
    __SESS = None
    artists = {}      # Dictionary<planet_id, Dictionary<account_no, FNSArtist>>
    attachments = {}  # Dictionary<planet_id, Dictionary<attachment_id, FNSAttachment>>
    feeds = {}        # Dictionary<planet_id, Dictionary<feed_id, FNSFeed>>
    tags = {}         # Dictionary<planet_id, Dictionary<tag, List<FNSFeed>>>

    def __addArtist(self, planet_id, account_no, artist):
        """ PRIVATE (FNSModule, string, FNSArtist) -> NoneType
        Add a FNSArtist to current FNSModule
        """
        self.artists[planet_id][account_no] = artist
    
    def __addFeed(self, planet_id, feed_id, feed):
        """ PRIVATE (FNSModule, string, FNSFeed) -> NoneType
        Add a FNSFeed to current FNSModule
        """
        if not feed_id in self.feeds:
            self.feeds[planet_id][feed_id] = feed
    
    def __addAttachment(self, planet_id, attachment_id, attachment):
        """ PRIVATE (FNSModule, string, FNSAttachment) -> NoneType
        Add a FNSAttachment to current FNSModule
        """
        if not attachment_id in self.attachments:
            self.attachments[planet_id][attachment_id] = attachment

    def __processFeed(self, planet_id, f):
        """ PRIVATE (FNSModule, Object) -> FNSFeed
        Process parsed FNS Feed JSON object
        """
        
        escape = False
        # if already processed, pass
        if f["id"] in self.feeds[planet_id]:
            # Should update the attachment
            for a in f["attach_urls"]:
                self.attachments[planet_id][a["id"]].SetFile(a["file"], a["type"])
            escape = True
            
        # parse the artist first
        if not f["account_no"] in self.artists[planet_id]:
            # add
            self.__addArtist(planet_id, f["account_no"],
                FNSArtist(f["account_no"], f["artist_id"], f["nickname"], f["profile_picture"])
            )
        elif self.artists[planet_id][f["account_no"]].artist_id == -1:
            # update
            self.artists[planet_id][f["account_no"]].artist_id = f["artist_id"]
            self.artists[planet_id][f["account_no"]].nickname = f["nickname"]
            self.artists[planet_id][f["account_no"]].profile_picture = f["profile_picture"]
        else:
            if self.artists[planet_id][f["account_no"]].profile_picture != f["profile_picture"]:
                self.artists[planet_id][f["account_no"]].profile_picture = f["profile_picture"]

            if self.artists[planet_id][f["account_no"]].nickname != f["nickname"]:
                self.artists[planet_id][f["account_no"]].nickname = f["nickname"]

        if escape:
            return self.feeds[planet_id][f["id"]]

        feed = FNSFeed(f["id"])
        feed.SetBody(f["body"])
        feed.SetDate(f.get("create_date", ""), f.get("modify_date", ""), f.get("publish_date", ""))
        
        for a in f["attach_urls"]:
            if not a["account_no"] in self.artists[planet_id]:
                # add dummy artist
                self.__addArtist(planet_id, a["account_no"],
                    FNSArtist(a["account_no"], -1, "", "")
                )
            attach = FNSAttachment(a["id"])
            attach.SetDate(f.get("create_date", ""), f.get("publish_date", ""))
            attach.SetFile(a["file"], a["type"])
            attach.SetArtist(self.artists[planet_id][a["account_no"]])
            self.__addAttachment(planet_id, attach.attachment_id, attach)
            feed.AddAttachment(attach)

        for tag in f.get("tags", []):
            feed.AddTag(tag)
            if not tag in self.tags:
                self.tags[planet_id][tag] = []
            self.tags[planet_id][tag].append(feed)

        feed.SetArtist(self.artists[planet_id][f["account_no"]])
        self.__addFeed(planet_id, feed.feed_id, feed)
        return feed
    
    def __init__(self, sess):
        """ (FNSModule, UserSession) -> NoneType
        Initialize FNSModule with given UserSession
        """
        self.__SESS = sess
        self.artists = {}
        self.feeds = {}
        self.attachments = {}
        self.tags = {}

    def LoadFeed(self, planet_id, artist_id = 1, next = 0.0, search_user = '', size = 10, tags = ''):
        """ (FNSModule, Int, Int, Float, String, Int, String) -> (List<FNSFeed>, Float)
        Load FNS feeds from given planet id and information.
        Also, process feeds internally.
        Returns a tuple of the list of feeds proceed and the next search parameter.
        """
        if not planet_id in self.artists:
            self.artists[planet_id] = dict()
            self.feeds[planet_id] = dict()
            self.attachments[planet_id] = dict()
            self.tags[planet_id] = dict()

        code, fns_obj, _ = self.__SESS.Get("https://api.universe-official.io/fns/feeds", {
            "planet_id": planet_id, "artist_id": artist_id, "next": next,
            "search_user": search_user, "size": size, "tags": tags
        })

        if code != 0:
            raise Exception("Error while fetching FNS feed")

        fns_obj = fns_obj["fns"]

        added = []
        for feed in fns_obj["feeds"]:
            f =  self.__processFeed(planet_id, feed)
            if f is not None:
                added.append(f)
        
        return added, fns_obj["next"]
