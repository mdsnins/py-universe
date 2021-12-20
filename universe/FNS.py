from .util import convert_timestr

class FNSArtist():
    """
    Class FNSArtist
    
    Save information of an artist.
    """

    def __init__(self, account_no, artist_id, nickname, profile_picture):
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
        self.tags.append(tag)

    def __str__(self):
        return "<FNSFeed: [{}] {}>".format(self.artist.nickname, self.feed_id)
    def like():
        #TODO: implement
        pass

class FNSModule():
    __SESS = None
    artists = {}
    attachments = {}
    feeds = {}
    tags = {}

    def __addArtist(self, account_no, artist):
        self.artists[account_no] = artist
    
    def __addFeed(self, feed_id, feed):
        if not feed_id in self.feeds:
            self.feeds[feed_id] = feed
    
    def __addAttachment(self, attachment_id, attachment):
        if not attachment_id in self.attachments:
            self.attachments[attachment_id] = attachment

    def __init__(self, sess):
        self.__SESS = sess
        self.artists = {}
        self.feeds = {}

    def __processFeed(self, f):
        # if already processed, pass
        if f["id"] in self.feeds:
            return False

        # parse the artist first
        if not f["account_no"] in self.artists:
            # add
            self.__addArtist(f["account_no"],
                FNSArtist(f["account_no"], f["artist_id"], f["nickname"], f["profile_picture"])
            )
        elif self.artists[f["account_no"]].artist_id == -1:
            # update
            self.artists[f["account_no"]].artist_id = f["artist_id"]
            self.artists[f["account_no"]].nickname = f["nickname"]
            self.artists[f["account_no"]].profile_picture = f["profile_picture"]
        
        feed = FNSFeed(f["id"])
        feed.SetBody(f["body"])
        feed.SetDate(f.get("create_date", ""), f.get("modify_date", ""), f.get("publish_date", ""))
        
        for a in f["attach_urls"]:
            if not a["account_no"] in self.artists:
                # add dummy artist
                self.__addArtist(a["account_no"],
                    FNSArtist(a["account_no"], -1, "", "")
                )
            attach = FNSAttachment(a["id"])
            attach.SetDate(f.get("create_date", ""), f.get("publish_date", ""))
            attach.SetFile(a["file"], a["type"])
            attach.SetArtist(self.artists[a["account_no"]])
            self.__addAttachment(attach.attachment_id, attach)
            feed.AddAttachment(attach)

        for tag in f.get("tags", []):
            feed.AddTag(tag)
            if not tag in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(feed)

        feed.SetArtist(self.artists[f["account_no"]])
        self.__addFeed(feed.feed_id, feed)
        return True
    
    def LoadFeed(self, planet_id, artist_id = 1, next = 0.0, search_user = 0.0, size = 10, tags = ''):
        code, fns_obj, extra = self.__SESS.Get("https://api.universe-official.io/fns/feeds", {
            "planet_id": planet_id, "artist_id": artist_id, "next": next,
            "search_user": search_user, "size": size, "tags": tags
        })

        fns_obj = fns_obj["fns"]

        count = 0
        for feed in fns_obj["feeds"]:
            if self.__processFeed(feed):
                count += 1
        
        return count, fns_obj["next"]
        

