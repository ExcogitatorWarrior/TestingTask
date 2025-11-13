import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 86400  # 1 day


def create_jwt(user_id, role_name):
    payload = {
        "user_id": user_id,
        "role": role_name,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        "iat": datetime.utcnow(),           # issued at
        "jti": str(uuid.uuid4())           # unique token ID
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None