from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password


class FirestoreUserPk:
    def value_to_string(self, user):
        return str(user.pk)


class FirestoreUserMeta:
    pk = FirestoreUserPk()


class FirestoreUser:
    _meta = FirestoreUserMeta()
    is_active = True
    is_authenticated = True
    is_anonymous = False

    def __init__(self, username, password=""):
        self.username = username
        self.id = username
        self.pk = username
        self.password = password

    def get_username(self):
        return self.username

    def save(self, *args, **kwargs):
        pass


class FirestoreAuthBackend(BaseBackend):
    def get_user_from_data(self, username, data):
        return FirestoreUser(username, data.get("password", ""))

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        from google.cloud import firestore

        user_doc = firestore.Client().collection("users").document(username).get()
        if not user_doc.exists:
            return None

        data = user_doc.to_dict()
        if check_password(password, data.get("password", "")):
            return self.get_user_from_data(username, data)
        return None

    def get_user(self, user_id):
        from google.cloud import firestore

        user_doc = firestore.Client().collection("users").document(str(user_id)).get()
        if not user_doc.exists:
            return None

        return self.get_user_from_data(str(user_id), user_doc.to_dict())
