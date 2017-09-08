from mendeley.resources.base import ListResource, GetByIdResource


class DocumentsBase(GetByIdResource, ListResource):
    def __init__(self, session, group_id):
        self.session = session
        self.group_id = group_id

    def get(self, id, view=None):
        return super(DocumentsBase, self).get(id, view=view)

    def list(self, page_size=None, view=None, sort=None, order=None, modified_since=None, deleted_since=None, marker=None, folder_id=None, tag=None, page=None):
        return super(DocumentsBase, self).list(page_size,
                                               view=view,
                                               sort=sort,
                                               order=order,
                                               modified_since=modified_since,
                                               deleted_since=deleted_since,
                                               marker=marker,
                                               folder_id=folder_id,
                                               tag=tag,
                                               group_id=self.group_id,
                                               page=page)

    def iter(self, page_size=None, view=None, sort=None, order=None, modified_since=None, deleted_since=None, folder_id=None, tag=None):
        return super(DocumentsBase, self).iter(page_size,
                                               view=view,
                                               sort=sort,
                                               order=order,
                                               modified_since=modified_since,
                                               deleted_since=deleted_since,
                                               folder_id=folder_id,
                                               tag=tag,
                                               group_id=self.group_id)

    @property
    def _session(self):
        return self.session

    def _obj_type(self, **kwargs):
        return self.view_type(kwargs.get('view'))

    @staticmethod
    def view_type(view):
        raise NotImplementedError
