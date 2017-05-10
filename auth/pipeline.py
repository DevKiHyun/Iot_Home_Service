# -*- coding: utf-8 -*-

from worker import mydb

def user_setting(backend, details, response ,uid, user, *args, **kwargs):
    url = None

    if backend.name == 'google-oauth2' :
        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')

        mydb.create_app_email(details["email"])
        mydb.create_app_email_folder()
