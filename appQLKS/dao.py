from appQLKS.models import User
from appQLKS import app, db


def get_user_by_id(id):
    return User.query.get(id)