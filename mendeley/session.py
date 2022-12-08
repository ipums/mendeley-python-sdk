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
from requests.exceptions import JSONDecodeError

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
            # If the first request of a session has an expired token, Mendeley sends back a 401 with the JSON message
            # {"message": "Could not access resource because: Token has expired"}
            # We want to handle that the same as when the oauth session throws a TokenExpiredError
            if rsp.status_code == 401:
                try:
                    if 'Token has expired' in rsp.json()["message"]:
                        raise TokenExpiredError(status_code=401, request=rsp)
                except JSONDecodeError:
                    pass
        except TokenExpiredError as e:
            logger.debug(f"Handling a token expiration from {e}")
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

class TokenRefresher(object):
    def __init__(self, refresh_token, update_token_callback, **kwargs):
        self.refresh_token = refresh_token
        self.update_token_callback = update_token_callback
        self.refresh_token_params = kwargs
    
    def refresh(self, session):
        new_token = session.refresh_token('https://api.mendeley.com/oauth/token', self.refresh_token, auth=(session.client_id, session.client_secret), **self.refresh_token_params)
        if self.update_token_callback:
            self.update_token_callback(new_token)

