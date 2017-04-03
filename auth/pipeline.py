# -*- coding: utf-8 -*-
def get_user_avatar(backend, details, response,uid, user, *args, **kwargs):
    url = None

    if backend.name == 'google-oauth2' :

        user.first_name = details["first_name"]
        user.last_name = details["last_name"]
        user.username = details["username"]
        user.email = details["email"]

        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')

        user.save()
