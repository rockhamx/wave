from flask_uploads import UploadSet, IMAGES

avatar = UploadSet('avatars', IMAGES)

# def avatar_dir(user):
#     return