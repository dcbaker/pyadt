# SPDX-License-Identifier: MIT
# Copyright © 2023 Dylan Baker

"""An implementation of a Result type."""

from __future__ import annotations
from functools import wraps
from typing import *
from dataclasses import dataclass

if TYPE_CHECKING:
    from .maybe import Maybe

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')
F = TypeVar('F')

__all__ = [
    'Error',
    'ErrorWrapper',
    'Result',
    'Success',
    'UnwrapError',
    'unwrap_result',
    'wrap_result',
]


class UnwrapError(Exception):
    """Error thrown when unwrapping is invalid."""


class ErrorWrapper(Exception):
    """wraps non Exception Errors"""


class Result(Generic[T, E]):

    """Base Class for Option, do not directly instantiate"""

    @staticmethod
    def is_ok() -> bool:
        """Returns True if this is a Success otherwise False."""
        raise NotImplementedError()

    @staticmethod
    def is_err() -> bool:
        """Returns True if this is an Error otherwise False."""
        raise NotImplementedError()

    def unwrap(self, msg: str | None = None) -> T:
        """Get the held value or throw an Exception.

        :param msg: The error message, otherwise a default is used
        :raises UnwrapError: If this is an Err
        :return: The held value
        """
        raise NotImplementedError()

    def unwrap_or(self, fallback: T) -> T:
        """Return the held value or fallback if this is an Error.

        :param fallback: A value to use incase of Error
        :return: The held value or the fallback
        """
        raise NotImplementedError()

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        """Return the held value or the result of the fallback.

        :param fallback: A callable to generate a result if this in Error
        :return: Either the held value or the fallback value
        """
        raise NotImplementedError()

    def unwrap_err(self, msg: str | None = None) -> E:
        """Return the Error, or throw an UnwrapError

        :param msg: The message to add to the UnwrapError, otherwise a default is used
        :raises UnwrapError: Thrown if this is a Success
        :return: The held error
        """
        raise NotImplementedError()

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        """Transform the held value or return the Error unchanged.

        :param cb: A callback taking the held success type and returning a new one
        :return: A result with the transformed Success or an unchanged Error
        """
        raise NotImplementedError()

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        """Transform the held error or return the success unchanged.

        :param cb: A callback taking the held error type and returning a new one
        :return: A result with the transformed Error or an unchanged Success
        """
        raise NotImplementedError()

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        """Transform the held value or return the default.

        :param default: A value to use of Error
        :param cb: A callback to transform the held value of a Success
        :return: The fallback value or the transformed held value
        """
        raise NotImplementedError()

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        """Transform the held value or return the calculated default

        :param default: A callable returning a value for Error
        :param cb: A callback to transform the held value of a Success
        :return: The fallback value or the transformed held value
        """
        raise NotImplementedError()

    def and_then(self, cb: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Run the callback if this is a Success, otherwise return the Err unchanged

        :param cb: A callback run on the held value of a Success
        :return: a new Result with a transformed value or the error
        """
        raise NotImplementedError()

    def or_else(self, cb: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Run the callback if this is an Error, otherwise return the Success unchanged

        :param cb: A callback run on the held value of a Error
        :return: a new Result with a transformed value or the Success
        """
        raise NotImplementedError()

    def err(self) -> Maybe[E]:
        """Transform an Result[T, E] into a Maybe[E]

        A Success will be mapped to Nothing[E], while and Error becomes Something[E]

        :return: A Maybe with the error
        """
        raise NotImplementedError()

    def ok(self) -> Maybe[T]:
        """Transform an Result[T, E] into a Maybe[T]

        A Success will be mapped to Something[T], while and Error becomes Nothing[T]

        :return: A Maybe with the held value
        """
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class Error(Result[T, E]):

    _held: E

    def __bool__(self) -> bool:
        return False

    @staticmethod
    def is_ok() -> bool:
        return False

    @staticmethod
    def is_err() -> bool:
        return True

    def unwrap(self, msg: str | None = None) -> T:
        e: Exception
        if isinstance(self._held, Exception):
            e = self._held
        else:
            e = ErrorWrapper(self._held)
        raise UnwrapError(msg or 'Attempted to unwrap an Error') from e

    def unwrap_or(self, fallback: T) -> T:
        return fallback

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return fallback()

    def unwrap_err(self, msg: str | None = None) -> E:
        return self._held

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        return Error(self._held)

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        return Error(cb(self._held))

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        return default()

    def and_then(self, cb: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Error(self._held)

    def or_else(self, cb: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cb(self._held)

    def err(self) -> Maybe[E]:
        from .maybe import Something
        return Something(self._held)

    def ok(self) -> Maybe[T]:
        from .maybe import Nothing
        return Nothing()


@dataclass(slots=True, frozen=True)
class Success(Result[T, E]):

    _held: T
    def __bool__(self) -> bool:
        return True

    @staticmethod
    def is_ok() -> bool:
        return True

    @staticmethod
    def is_err() -> bool:
        return False

    def unwrap(self, msg: str | None = None) -> T:
        return self._held

    def unwrap_or(self, fallback: T) -> T:
        return self._held

    def unwrap_or_else(self, fallback: Callable[[], T]) -> T:
        return self._held

    def unwrap_err(self, msg: str | None = None) -> E:
        if msg is None:
            msg = 'Attempted to unwrap the error from a Success'
        raise UnwrapError(msg)

    def map(self, cb: Callable[[T], U]) -> Result[U, E]:
        return Success(cb(self._held))

    def map_err(self, cb: Callable[[E], F]) -> Result[T, F]:
        return Success(self._held)

    def map_or(self, default: U, cb: Callable[[T], U]) -> U:
        return cb(self._held)

    def map_or_else(self, default: Callable[[], U], cb: Callable[[T], U]) -> U:
        return cb(self._held)

    def and_then(self, cb: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cb(self._held)

    def or_else(self, cb: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return Success(self._held)

    def err(self) -> Maybe[E]:
        from .maybe import Nothing
        return Nothing()

    def ok(self) -> Maybe[T]:
        from .maybe import Something
        return Something(self._held)


def wrap_result(catch: type[Exception] | tuple[type[Exception], ...] = Exception) -> Callable[[Callable[P, R]], Callable[P, Result[R, Exception]]]:
    """Decorator for wrapping throwing functions to return a Result instead

    This is meant for simple cases only, if you wish to have more complex error
    handling than simply catching all exceptions and putting them in the Result
    you will need to handle that yourself.

    :param f: A callable to wrap
    :param catch: A Exeption or tuple of Exceptions to catch, defaults to Exception
    :return: A result of T or the caught Exception(s) as E
    """

    def wrapper(f: Callable[P, R]) -> Callable[P, Result[R, Exception]]:
        @wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> Result[R, Exception]:
            try:
                return Success(f(*args, **kwargs))
            except catch as e:
                return Error(e)

        return inner

    return wrapper


def unwrap_result(f: Callable[P, Result[R, E]]) -> Callable[P, R]:
    """Decorator for unwrapping Result returning functions, return the result or
    throwing the Exception.

    This is meant for simple cases only, if you wish to have more complex error
    handling than simply catching all exceptions and putting them in the Result
    you will need to handle that yourself.

    :param f: A callable to unwrap
    :raises ErrorWrapper: if E is not an Exception type
    :raises E: any values of E that Exceptions
    :return: the valu eof a Success
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        r = f(*args, **kwargs)
        if r.is_ok():
            return r.unwrap()
        e = r.unwrap_err()
        if isinstance(e, Exception):
            raise e
        raise ErrorWrapper(e)

    return inner
