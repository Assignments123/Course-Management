from flask import request
import jwt
from jwt.exceptions import InvalidTokenError
import datetime
from functools import wraps
import os
import json

def validate_jwt(token, secret_key):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        # Perform additional checks if necessary
        return True, decoded_token
    except InvalidTokenError:
        return False, None
    
def tokenvalidationmiddleware(func):
    # middleware function for validating the token
    # this middleware/decorator is applied to index function only
    @wraps(func)
    def wrapper(*args , **kwargs):

        secretkey = os.getenv('SECRETKEY')
        token = request.headers.get('Authorization')

        print("token inside middleware" , token)

        if not token:
            return "token is missing"
        
        # try:
        valid, decoded_token = validate_jwt(token, secretkey)
        if valid:
            # Perform additional checks if necessary
            return func(*args, **kwargs)
        return json.dumps({'message': 'Unauthorized'}), 401
            # payload = jwt.decode(token ,secretkey) #while decoding the token its givind DecodeError
        
        # except jwt.DecodeError:
        #     response = {"message":"Unable to Decode Token"}
        #     return response
        # except jwt.ExpiredSignatureError:
        #     response = {"message":"Token is Expireed!!"}
        #     return response
        # except jwt.InvalidTokenError:
        #     response = {"message":"Token is Invalid!!"}
        #     return response
        
        # return  func(*args , **kwargs)

    return wrapper


def generatetoken():
    
    # function for generating a JWT token for authentication

    secretkey = os.getenv('SECRETKEY')
    
    payload = {
        'user' : 'manoj',
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    }

    token = jwt.encode(payload,secretkey)

    return token
