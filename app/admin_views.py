from flask import url_for, flash, abort, current_app
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction
from flask_login import current_user
from flask_babelex import lazy_gettext as _l
from wtforms import PasswordField
from wtforms.validators import InputRequired, Length


class WaveModelView(ModelView):
    page_size = 10
    can_set_page_size = True

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
    can_view_details = True
    # can_delete = False
    # can_export = True
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
                     'password_hash': _l('Password Hash'),
                     'email_hash': _l('Email Hash'),
                     'theme': _l('Theme'),
                     'is_administrator': _l('is administrator')
                     }
    # column_list = ('username', 'name', 'email', 'location', 'description', 'confirmed', 'locale', 'timezone', )
    column_exclude_list = ['password_hash', 'email_hash', 'theme', 'timezone', 'is_administrator', "member_since"]
    column_filters = ['confirmed', 'member_since', 'last_seen']
    column_searchable_list = ['username', 'name', 'location']
    column_editable_list = ['name', 'confirmed']
    # column_extra_row_actions = [
        # LinkRowAction('glyphicon glyphicon-user', lambda link, row, row_id: 'http://127.0.0.1/{}'.format(row)),
        # EndpointLinkRowAction('glyphicon glyphicon-test', 'my_view.index_view')
    # ]

    form_columns = ['email', 'username', 'password', 'name', 'confirmed', 'description', 'location', 'locale']
    # form_excluded_columns = ['posts', 'comments', 'drafts', 'hearted', 'bookmarks', 'member_since', 'last_seen',
    #                          'followers', 'following', 'followed_publications', 'message_sent', 'message_received',
    #                          'password_hash', 'email_hash', 'theme', 'timezone', 'is_administrator']
    form_extra_fields = {
        'password': PasswordField(_l(u'Password'), validators=[InputRequired(), Length(1, 64)])
    }
    # form_args = dict(
    #     password=dict(validators=[InputRequired()])
    # )


class PostView(WaveModelView):
    can_view_details = True
    can_export = True

    # column_labels = {'Author': '',
    #                  'Description': '',
    #                  'Hearts': '',
    #                  'Language': '',
    #                  'Is_Public': '',
    #                  'Publication': '',
    #                  'Subtitle': '',
    #                  'Pub_Timestamp': '',
    #                  'Edit_Timestamp': '',
    #                  'Title': ''}
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
    column_filters = ['read']


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
