from __future__ import annotations
# coding: utf-8
# Author: paolo.serra@autodesk.com
# Copyright (c) 2024 Autodesk, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

__author__ = 'Paolo Emilio Serra - paolo.serra@autodesk.com'
__copyright__ = '2024'
__version__ = '1.0.0'


import datetime
import decouple
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Sequence, Tuple, Callable
import json
import pathlib
import tempfile
import base64
import logging
import requests
import urllib

import aps

CONSUMER_KEY = decouple.config('CONSUMER_KEY')
CONSUMER_SECRET = decouple.config('CONSUMER_SECRET')
REDIRECT_URI = decouple.config('REDIRECT_URI')


# https://aps.autodesk.com/en/docs/oauth/v2/developers_guide/scopes/
SCOPES = (
    'user-profile:read',
    'user:read',
    'user:write',
    'viewables:read',
    'data:read',
    'data:write',
    'data:create',
    'data:search',
    'bucket:create',
    'bucket:read',
    'bucket:update',
    'bucket:delete',
    'code:all',
    'account:read',
    'account:write',
    'openid',
    'data:read:'  # Dynamic URN Scope
)


def validate_input(a: Any, *target: Any, none_allowed: bool = False) -> bool:
    """
    Validates the input against a target object_type and supports none
    @param a: The input
    @param target: the valid types
    @param none_allowed: if True the input could be None
    @return: True if the Input is valid otherwise raises and exception
    """
    tgs = []
    for t in target:
        if not isinstance(t, type):
            tgs.append(type(t))
        else:
            tgs.append(t)
    if not none_allowed and a is None:
        m = f'Input "{type(a).__name__}" cannot be None'
        logging.exception(m)
        raise ValueError(m)
    if not any([isinstance(a, t) for t in tgs]):
        m = f'Input is not a valid type ({", ".join([t.__name__ for t in tgs])}): "{a.__class__.__name__}"'
        logging.exception(m)
        raise TypeError(m)
    return True


def validate_sequence(a: Sequence, same_type: bool = True, target: type = str, none_allowed: bool = False, empty_allowed: bool = False, fn: Callable[..., bool] = None) -> Optional[bool]:
    """
    Returns True if the input is a sequence that satisfies the other conditions
    @param a: The object to validate
    @param same_type: If True checks that all the items in the object are of the same type
    @param target: The target type to check against
    @param none_allowed: If True None values are allowed
    @param empty_allowed: If True an empty sequence is allowed
    @param fn: The optional function that needs to evaluate True for each item in the sequence
    @return:
    """
    if hasattr(a, '__iter__'):
        if not empty_allowed:
            if len(a) == 0:
                return False
            if same_type:
                if fn is None:
                    fn = lambda k: True
                return all(validate_input(i, target, none_allowed) and fn(i) for i in a)
            else:
                return all(validate_input(i, set((type(i) for i in a)), none_allowed) and fn(i) for i in a)
        else:
            return True
    return False


def is_valid_enumeration_string(a: str, valid_values: Sequence[str]) -> Optional[bool]:
    if validate_sequence(valid_values):
        if validate_sequence(a) and a in valid_values:
            return True
    return False


def validate_query_list_enumerator_string(a: Sequence[str], parameters: Dict[str, Any], key: str, valid_values: Sequence[str]) -> Dict[str, Any]:
    if all(is_valid_enumeration_string(i, valid_values) for i in a):
        parameters[key] = a
    return parameters


@dataclass
class Token:
    """An object that stores the necessary information to handle the access token."""
    CreationTime: str = field(default=str(datetime.datetime.now()))
    Access: str = None
    Type: str = 'Bearer'
    Expires: int = 1700
    Legs: int = 3
    Scope: List[str] = field(default_factory=list)
    Code: str = None
    Refresh: str = None

    Path: pathlib.Path = pathlib.Path(tempfile.gettempdir()) / 'autodesk.consulting.token.aps'

    def __post_init__(self):
        if self.Scope is None or len(self.Scope) == 0:
            self.Scope = ['data:read']

    @property
    def Value(self) -> str:
        return f'{self.Type} {self.Access}'

    def json(self) -> Dict[str, Any]:
        return {
            'CreationTime': str(self.CreationTime),
            'Access': self.Access,
            'Type': self.Type,
            'Expires': self.Expires,
            'Legs': self.Legs,
            'Scope': self.Scope,
            'Code': self.Code,
            'Refresh': self.Refresh
        }

    def __repr__(self) -> str:
        return json.dumps(self.json(), indent=4).replace("'", '"').replace('True', 'true').replace('False',
                                                                                                   'false').replace(
            'None', 'null')

    def serialize(self) -> None:
        Token.Path.write_text(repr(self))

    @classmethod
    def read(cls) -> Token:
        if Token.Path.exists() and Token.Path.is_file():
            try:
                t = Token.Path.read_text()
                if len(t) > 0:
                    tk = Token(**json.loads(t))
                    if tk.Scope is None:
                        tk.Scope = ['data:read']
                    return tk
                else:
                    Token.Path.unlink()
            except Exception as ex:
                Token.Path.unlink()
                logging.exception(ex)
                raise ex
        return Token()

    @classmethod
    def from_string(cls, text: str) -> Token:
        logging.info(f'received: {text}')
        if text is not None and len(text) > 0:
            tk = Token(**json.loads(text))
            if tk.Scope is None:
                tk.Scope = ['data:read']
            return tk
        return Token()


token = Token.read()


def get_2_legged_token(scope: Sequence[str] = None) -> Token:
    """
    Obtains an Apigee 2-legged authentication Token with no user context needed or for app only
    @param scope: The list of scopes for the token
    @return: the Token Value
    """
    global token

    if scope is None:
        scope = ('data:read', )

    token.Scope = scope
    token.Legs = 2
    token.Code = None

    scope = ' '.join(scope)

    data = {'grant_type': 'client_credentials', 'scope': scope}

    endpoint = f'https://developer.api.autodesk.com/authentication/v2/token'
    basic = base64.b64encode(bytes(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8'))).decode('utf-8')
    headers = {'Authorization': f'Basic {basic}',
               'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(endpoint, headers=headers, data=data)

    j = resp.json()

    token.CreationTime = str(datetime.datetime.now())
    token.Access = j.get('access_token', None)
    token.Expires = j.get('expires_in', 1799)

    if token.Type is None:
        token.Type = j['token_type']

    token.serialize()
    return token


def get_code_address(scope: Sequence[str] = None) -> str:
    endpoint = 'https://developer.api.autodesk.com/authentication/v2/authorize'
    redir = urllib.parse.quote(REDIRECT_URI)

    if scope is None:
        scope = ['data:read']

    scope_url = '+'.join([urllib.parse.quote(s) for s in scope])

    return f'{endpoint}?response_type=code&client_id={CONSUMER_KEY}&redirect_uri={redir}&scope={scope_url}'


def get_3_legged_token(scope: Sequence[str], code: str) -> Token | str:
    """
    Requests an Apigee 3-legged authentication
    the code must be obtained from the host application
    @return: The Token
    """

    scope = validate_scope(*scope)

    endpoint = 'https://developer.api.autodesk.com/authentication/v2/token'
    basic = base64.b64encode(bytes(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8'))).decode('utf-8')
    headers = {'Authorization': f'Basic {basic}',
               'Content-Type': 'application/x-www-form-urlencoded'}
    req = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}

    res = requests.post(endpoint, headers=headers, data=req)

    if res.status_code == 200:
        j = res.json()
        token.CreationTime = str(datetime.datetime.now())
        token.Access = j['access_token']
        token.Refresh = j['refresh_token']
        token.Type = j['token_type']
        token.Expires = j['expires_in']
        token.Legs = 3
        token.Scope = scope
        token.Code = code
    else:
        logging.error(f'{res.status_code}: {res.content}')

    token.serialize()
    return token


def is_token_valid() -> bool:
    """
    Checks if the current token is still valid, otherwise it requests a refresh if user context is needed or checks if the token is still active
    :return:
    """
    # https://autodesk.slack.com/archives/CDKCPTMRP/p1685469024787249
    # the datetime.now() returns the local computer time and not the server time
    global token

    if datetime.datetime.fromisoformat(token.CreationTime) + datetime.timedelta(seconds=3300) > datetime.datetime.now():
        if token.Access is not None:
            return True
    else:
        if token.Refresh is not None:
            r = refresh_token()
            if r is not None:
                logging.info('Token refreshed')
                return True
            return False

    endpoint = 'https://developer.api.autodesk.com/authentication/v2/introspect'
    basic = base64.b64encode(bytes(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8'))).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {basic}',
    }
    data = {'token': token.Access}

    resp = requests.post(endpoint, headers=headers, data=data)

    code = resp.status_code
    if code == 401:
        return False
    elif code == 200:
        resp = resp.json()
        status = resp.get('active', False)
        if status:
            return True
    return False


def refresh_token() -> Token | None:
    """
    Refreshes the token if a user context was required
    :return:
    """
    global token
    basic = base64.b64encode(bytes(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode('utf-8'))).decode('utf-8')
    endpoint = 'https://developer.api.autodesk.com/authentication/v2/token'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {basic}'
    }

    if is_token_3_legged():
        data = {'grant_type': 'refresh_token',
                'refresh_token': token.Refresh}
    else:
        data = {'grant_type': 'client_credentials',
                'scope': '+'.join([urllib.parse.quote(s) for s in token.Scope])}

    res = requests.post(endpoint, headers=headers, data=data)
    if res.status_code == 200:
        j = res.json()
        token.CreationTime = str(datetime.datetime.now())
        token.Access = j['access_token']
        token.Refresh = j['refresh_token']
        token.Type = j['token_type']
        token.Expires = j['expires_in']
        token.serialize()
    else:
        return None
    return token


def is_token_3_legged() -> bool:
    return token.Legs == 3


def get_user_info() -> Any:
    """
    Returns the Autodesk Account user Info
    :return:
    """
    global token

    endpoint = 'https://api.userprofile.autodesk.com/userinfo'
    headers = {
        'Authorization': token.Value,
    }

    resp = requests.get(endpoint, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return {resp.status_code: resp.text}


def validate_scope(*scope) -> Tuple[str]:
    """
    Validates the scope against the list of the allowed scopes and returns a new collection of scopes
    @param scope:
    @return:
    """
    global token
    temp_scope = {}
    validate_query_list_enumerator_string(scope, temp_scope, 'values', SCOPES)

    for s in scope:
        if s is None:
            continue
        if len(s) == 0:
            continue
        if s.startswith(SCOPES[-1]):
            temp_scope.setdefault('values', []).append(s)

    new_scope = set(temp_scope.get('values', ()))

    if token.Scope is not None:
        new_scope.update(token.Scope)
    new_scope.update(scope)
    new_scope = tuple(s for s in new_scope if s in SCOPES)

    if len(new_scope) == 0:
        new_scope = ('data:read',)

    return new_scope


def validate_token(*scope: str | Tuple[str], three_legged: bool = False) -> Token:
    """
    Validates the existing token against the scopes and the user context if needed
    :param scope:
    :param three_legged:
    :return:
    """
    global token
    new_scope = validate_scope(*scope)

    if three_legged:
        if is_token_3_legged():
            if all(s in token.Scope for s in new_scope):
                if is_token_valid():
                    return token
        token = get_3_legged_token(new_scope)
    else:
        if all(s in token.Scope for s in new_scope):
            if is_token_valid():
                if not is_token_3_legged():
                    return token
        token = get_2_legged_token(new_scope)
    return token

