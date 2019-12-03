from flask import url_for, flash, abort, current_app
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_babelex import lazy_gettext as _l


class WaveModelView(ModelView):
    page_size = 10
    def is_accessible(self):
        return current_user.is_administrator

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            abort(404)
            # return redirect(url_for('user.profile', username=current_user.username))
        else:
            return current_app.login_manager.unauthorized()


class WaveAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_administrator

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            abort(404)
            # return redirect(url_for('user.profile', username=current_user.username))
        else:
            return current_app.login_manager.unauthorized()


class UserView(WaveModelView):
    column_labels = {'username': _l('Username'),
                     'name': _l('Name'),
                     'email': _l('Email'),
                     'location': _l('Location'),
                     'description': _l('Description'),
                     'confirmed': _l('Confirmed'),
                     'locale': _l('Locale'),
                     'timezone': _l('Timezone'),
                     'member_since': _l('Member_since'),
                     'last_seen': _l('Last_seen'),
                     }
    # column_labels = dict(username=lazy_gettext(u'Username'))
    can_view_details = True
    can_export = True
    # column_list = ['username', 'name', 'email', 'location', 'description', 'confirmed', 'locale', 'timezone']
    column_exclude_list = ['password_hash', 'email_hash', 'theme', 'is_administrator']
    column_filters = ['confirmed']
    column_searchable_list = ['username', 'name', 'location']
    # column_searchable_list = [_l('username')]
    # column_searchable_list = [_l('Username')]
    form_excluded_columns = ['password_hash', ]


class PostView(WaveModelView):
    can_view_details = True
    can_export = True
    # column_list = ['author', 'title', 'subtitle', 'description', 'hearts', 'language', 'is_public', 'publication',
    #                'pub_timestamp', 'edit_timestamp', ]
    column_exclude_list = ['clicked', 'body', 'html', 'preview']
    column_filters = ['is_public']
    column_searchable_list = ['title', 'subtitle', 'description']
    # column_details_list = ['html']


class DraftView(WaveModelView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['title', 'subtitle', 'description']
    column_exclude_list = ['content']
    column_filters = ['is_public', 'type']


class CommentView(WaveModelView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['content', ]


class PublicationView(WaveModelView):
    column_searchable_list = ['name', 'description']


class TagView(WaveModelView):
    column_searchable_list = ['name', 'description']


class MessageView(WaveModelView):
    column_searchable_list = ['content']


# Not using it
class FollowView(WaveModelView):
    column_searchable_list = ['content']


class HeartsView(WaveModelView):
    column_searchable_list = ['content']


class BookmarkView(WaveModelView):
    column_searchable_list = ['content']


class FollowedPublicationView(WaveModelView):
    column_searchable_list = ['content']


class PostTags(WaveModelView):
    column_searchable_list = ['content']
