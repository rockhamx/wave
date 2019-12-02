from flask_admin.contrib.sqla import ModelView


class BaseView(ModelView):
    can_view_details = True
    can_export = True


class UserView(BaseView):
    # column_list = ['username', 'name', 'email', 'location', 'description', 'confirmed', 'locale', 'timezone']
    column_exclude_list = ['password_hash', 'email_hash', 'theme', 'is_administrator']
    column_filters = ['confirmed']
    column_searchable_list = ['username', 'name']
    form_excluded_columns = ['password_hash', ]


class PostView(BaseView):
    # column_list = ['author', 'title', 'subtitle', 'description', 'hearts', 'language', 'is_public', 'publication',
    #                'pub_timestamp', 'edit_timestamp', ]
    column_exclude_list = ['clicked', 'body', 'html', 'preview']
    column_filters = ['is_public']
    column_searchable_list = ['title', 'subtitle', 'description']
    # column_details_list = ['html']


class DraftView(BaseView):
    column_searchable_list = ['title', 'subtitle', 'description']
    column_exclude_list = ['content']
    column_filters = ['is_public', 'type']


class CommentView(BaseView):
    column_searchable_list = ['content', ]


class PublicationView(ModelView):
    column_searchable_list = ['name', 'description']


class TagView(ModelView):
    column_searchable_list = ['name', 'description']


class MessageView(ModelView):
    column_searchable_list = ['content']
