import platform
import logging
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(name)s:%(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

from future.moves.urllib.parse import urljoin
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session

from mendeley.exception import MendeleyApiException
from mendeley.resources import *
from mendeley.version import __version__


class MendeleySession(OAuth2Session):
    """
    Entry point for accessing Mendeley resources.

    .. attribute:: annotations

        A :class: `Annotations <mendeley.resources.annotations.Annotations>` resource for accessing annotations in the
        logged-in user's library.

    .. attribute:: catalog

       A :class:`Catalog <mendeley.resources.catalog.Catalog>` resource for accessing the Mendeley catalog.

    .. attribute:: documents

       A :class:`Documents <mendeley.resources.documents.Documents>` resource for accessing documents in the logged-in
       user's library.

    .. attribute:: files

       A :class:`Files <mendeley.resources.files.Files>` resource for accessing files in the logged-in user's library.

    .. attribute:: groups

       A :class:`Groups <mendeley.resources.groups.Groups>` resource for accessing groups that the user is a member of.

    .. attribute:: profiles

       A :class:`Profiles <mendeley.resources.profiles.Profiles>` resource for accessing profiles of Mendeley users.

    .. attribute:: trash

       A :class:`Trash <mendeley.resources.trash.Trash>` resource for accessing trashed documents in the logged-in
       user's library.
    """

    def __init__(self, mendeley, token, client=None, refresher=None):
        if client:
            super(MendeleySession, self).__init__(client=client, token=token)
        else:
            super(MendeleySession, self).__init__(client_id=mendeley.client_id, token=token)

        self.host = mendeley.host
        self.refresher = refresher

        self.annotations = Annotations(self)
        self.catalog = Catalog(self)
        self.documents = Documents(self, None)
        self.files = Files(self)
        self.groups = Groups(self)
        self.profiles = Profiles(self)
        self.trash = Trash(self, None)

    def group_members(self, group_id):
        return GroupMembers(self, group_id)

    def group_documents(self, group_id):
        return Documents(self, group_id)

    def group_trash(self, group_id):
        return Trash(self, group_id)

    def group_files(self, group_id):
        return Files(self, group_id=group_id)

    def document_files(self, document_id):
        return Files(self, document_id=document_id)

    def catalog_files(self, catalog_id):
        return Files(self, catalog_id=catalog_id)

    def request(self, method, url, data=None, headers=None, **kwargs):
        full_url = urljoin(self.host, url)

        if not headers:
            headers = {}

        headers['user-agent'] = self.__user_agent()

        try:
            rsp = self.__do_request(data, full_url, headers, kwargs, method)
        except TokenExpiredError:
            if self.refresher:
                self.refresher.refresh(self)
                rsp = self.__do_request(data, full_url, headers, kwargs, method)
            else:
                raise

        if rsp.ok:
            return rsp
        else:
            raise MendeleyApiException(rsp)

    def __do_request(self, data, full_url, headers, kwargs, method):
        rsp = super(MendeleySession, self).request(method, full_url, data, headers, **kwargs)
        return rsp

    @staticmethod
    def __user_agent():
        return 'mendeley/%s %s/%s %s/%s' % (__version__,
                                            platform.python_implementation(),
                                            platform.python_version(),
                                            platform.system(),
                                            platform.release())

# extending the MendeleySession class to do auto-token-refresh on
# token expiration. Mendeley access tokens expire after 1 hour.
class AutoRefreshMendeleySession(MendeleySession):
    def __init__(self, mendeley, token, refresh_token):
        print("I'm in init")
        super(AutoRefreshMendeleySession, self).__init__(mendeley, token)
        # silly name to avoid namespace collision with oauth refresh_token() method
        self.the_refresh_token = refresh_token
        self.client_secret = mendeley.client_secret

    def request(self, method, url, data=None, headers=None, **kwargs):
        try:
            logger.debug("Requesting " + url)
            # just try the MendeleySession request first
            return super(AutoRefreshMendeleySession, self).request(method, url, data, headers, **kwargs)
        except (MendeleyApiException, TokenExpiredError) as e:
            logger.debug("Receiving " + type(e).__name__)
            logger.debug(repr(e))
            # Check to see if we have an expired access token. This comes in two
            # forms: either a MendeleyApiException or OAuthlib's TokenExpiredError
            # Mendeley's API uses MendeleyAPIException for everything so you have
            # to unpack it.
            # In event of an expired token it sends back a 401 with the JSON message
            # {"message": "Could not access resource because: Token has expired"}
            # and the Python SDK forms a MendeleyAPIException with this message
            # in e.message and 401 in e.status
            # OAuthlib will send a TokenExpiredError if you have a long-running
            # session that goes over an hour. MendeleyApiException occurs when
            # you try to make a first request with an already expired token (such
            # as the one that's probably in the config file.)
            if ((type(e).__name__ is 'MendeleyApiException') and (e.status == 401) and ('Token has expired' in e.message)) or (type(e).__name__ is 'TokenExpiredError'):
                logger.debug("Handling a token expiration of type " + type(e).__name__)
                new_token = self.refresh_token('https://api.mendeley.com/oauth/token', self.the_refresh_token, auth=(self.client_id, self.client_secret), redirect_uri="www.ipums.org")
                logger.debug("Received new token")
                if((new_token['refresh_token']) and (new_token['refresh_token'] != self.the_refresh_token)):
                    logger.debug("The refresh token has changed.")
                pdb.set_trace()
                logger.debug("Re-requesting " + url)
                return super(AutoRefreshMendeleySession, self).request(method, url, data, headers, **kwargs)
            elif ((type(e).__name__ is 'MendeleyApiException') and (e.status == 400)):
                logger.debug("Attempt to use refresh token failed.")
                logger.debug(repr(e))
            else:
                logger.debug("Re-raising " + type(e).__name__)
                # pass on other mendeley exceptions
                raise
