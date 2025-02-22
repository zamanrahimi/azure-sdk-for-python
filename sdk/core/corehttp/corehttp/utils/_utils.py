# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
from typing import (
    Any,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
    Dict,
)
from urllib.parse import urlparse


class _FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC.

    Copy/pasted from Python doc

    :param int offset: offset in minutes
    """

    def __init__(self, offset):
        self.__offset = datetime.timedelta(minutes=offset)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return str(self.__offset.total_seconds() / 3600)

    def __repr__(self):
        return "<FixedOffset {}>".format(self.tzname(None))

    def dst(self, dt):
        return datetime.timedelta(0)


def case_insensitive_dict(
    *args: Optional[Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]], **kwargs: Any
) -> MutableMapping[str, Any]:
    """Return a case-insensitive mutable mapping from an inputted mapping structure.

    :param args: The positional arguments to pass to the dict.
    :type args: Mapping[str, Any] or Iterable[Tuple[str, Any]
    :return: A case-insensitive mutable mapping object.
    :rtype: ~collections.abc.MutableMapping
    """
    return CaseInsensitiveDict(*args, **kwargs)


def _format_parameters_helper(http_request, params):
    """Helper for format_parameters.

    Format parameters into a valid query string.
    It's assumed all parameters have already been quoted as
    valid URL strings.

    :param http_request: The http request whose parameters
     we are trying to format
    :type http_request: any
    :param dict params: A dictionary of parameters.
    """
    query = urlparse(http_request.url).query
    if query:
        http_request.url = http_request.url.partition("?")[0]
        existing_params = {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        params.update(existing_params)
    query_params = []
    for k, v in params.items():
        if isinstance(v, list):
            for w in v:
                if w is None:
                    raise ValueError("Query parameter {} cannot be None".format(k))
                query_params.append("{}={}".format(k, w))
        else:
            if v is None:
                raise ValueError("Query parameter {} cannot be None".format(k))
            query_params.append("{}={}".format(k, v))
    query = "?" + "&".join(query_params)
    http_request.url = http_request.url + query


class CaseInsensitiveDict(MutableMapping[str, Any]):
    """
    NOTE: This implementation is heavily inspired from the case insensitive dictionary from the requests library.
    Thank you !!
    Case insensitive dictionary implementation.
    The keys are expected to be strings and will be stored in lower case.
    case_insensitive_dict = CaseInsensitiveDict()
    case_insensitive_dict['Key'] = 'some_value'
    case_insensitive_dict['key'] == 'some_value' #True

    :param data: Initial data to store in the dictionary.
    :type data: Mapping[str, Any] or Iterable[Tuple[str, Any]]
    """

    def __init__(
        self, data: Optional[Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]] = None, **kwargs: Any
    ) -> None:
        self._store: Dict[str, Any] = {}
        if data is None:
            data = {}

        self.update(data, **kwargs)

    def copy(self) -> "CaseInsensitiveDict":
        return CaseInsensitiveDict(self._store.values())

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the `key` to `value`.

        The original key will be stored with the value

        :param str key: The key to set.
        :param value: The value to set the key to.
        :type value: any
        """
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key: str) -> Any:
        return self._store[key.lower()][1]

    def __delitem__(self, key: str) -> None:
        del self._store[key.lower()]

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def lowerkey_items(self) -> Iterator[Tuple[str, Any]]:
        return ((lower_case_key, pair[1]) for lower_case_key, pair in self._store.items())

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return False

        return dict(self.lowerkey_items()) == dict(other.lowerkey_items())

    def __repr__(self) -> str:
        return str(dict(self.items()))
