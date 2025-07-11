import jwt
from datetime import datetime, timedelta
from app.config import JWT_SECRET, JWT_ALGORITHM
from app.utils.logger import logger  

def create_token(data: dict, expires_in: int = 3600):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Token JWT creado para: {data.get('sub', 'sin sub')} con expiración de {expires_in} segundos.")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        logger.debug("Token JWT verificado exitosamente.")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado.")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Token JWT inválido: {str(e)}")
        return None
