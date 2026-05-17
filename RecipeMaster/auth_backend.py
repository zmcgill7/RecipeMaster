from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
import hashlib


def make_user_id(username):
    return int(hashlib.sha256(username.encode()).hexdigest()[:15], 16)


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

    def __init__(self, username, password="", user_id=None):
        self.username = username
        self.id = user_id or make_user_id(username)
        self.pk = self.id
        self.password = password

    def get_username(self):
        return self.username

    def save(self, *args, **kwargs):
        pass


class FirestoreAuthBackend(BaseBackend):
    def get_user_from_data(self, username, data):
        username = data.get("username", username)
        user_id = data.get("user_id") or make_user_id(username)
        return FirestoreUser(username, data.get("password", ""), user_id)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        from google.cloud import firestore

        user_doc = firestore.Client().collection("users").document(username).get()
        if not user_doc.exists:
            return None

        data = user_doc.to_dict()
        if check_password(password, data.get("password", "")):
            if not data.get("user_id"):
                user_doc.reference.update({"user_id": make_user_id(username)})
            return self.get_user_from_data(username, data)
        return None

    def get_user(self, user_id):
        from google.cloud import firestore

        users = firestore.Client().collection("users")
        matches = users.where("user_id", "==", int(user_id)).limit(1).stream()
        user_doc = next(matches, None)
        if user_doc is None:
            return None

        return self.get_user_from_data(str(user_id), user_doc.to_dict())


class FirestoreSessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get("_auth_user_id")
        if user_id is not None:
            try:
                int(user_id)
            except ValueError:
                request.session.flush()

        return self.get_response(request)
