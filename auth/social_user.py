from social.apps.django_app.default.models import UserSocialAuth

def get_token(token_type, user):
    social = user.social_auth.get(uid = user.email)
    token = social.extra_data[token_type]
    return token
