"""
Builtin sorts and function to egg.
"""


from __future__ import annotations

from typing import Generic, TypeVar, Union

from .registry import Registry

__all__ = [
    "BaseExpr",
    "BUILTINS",
    "Unit",
    "i64",
    "i64Like",
    "string",
    "stringLike",
    "Map",
    "Rational",
]


class BaseExpr:
    """
    Expression base class, which adds suport for != to all expression types.
    """

    def __ne__(self: EXPR, __o: EXPR) -> Unit:  # type: ignore
        ...

    def __eq__(self, other: NoReturn) -> NoReturn:  # type: ignore
        """
        Equality is currently not supported. We only add this method so that
        if you try to use it MyPy will warn you.
        """
        raise NotImplementedError()


BUILTINS = Registry()


@BUILTINS.class_(egg_sort="unit")
class Unit(BaseExpr):
    def __init__(self) -> None:
        ...


# The types which can be converted into an i64
i64Like = Union[int, "i64"]


@BUILTINS.class_(egg_sort="i64")
class i64(BaseExpr):
    def __init__(self, value: int):
        ...

    @BUILTINS.method(egg_fn="+")
    def __add__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="-")
    def __sub__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="*")
    def __mul__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="/")
    def __truediv__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="%")
    def __mod__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="&")
    def __and__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="|")
    def __or__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="^")
    def __xor__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="<<")
    def __lshift__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn=">>")
    def __rshift__(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="not-64")
    def __invert__(self) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="<")
    def __lt__(self, other: i64Like) -> Unit:  # type: ignore[empty-body,has-type]
        ...

    @BUILTINS.method(egg_fn=">")
    def __gt__(self, other: i64Like) -> Unit:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="min")
    def min(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="max")
    def max(self, other: i64Like) -> i64:  # type: ignore[empty-body]
        ...


@BUILTINS.class_
class string(BaseExpr):
    def __init__(self, value: str):
        ...


stringLike = Union[str, string]

T = TypeVar("T", bound=BaseExpr)
V = TypeVar("V", bound=BaseExpr)


@BUILTINS.class_(egg_sort="Map")
class Map(BaseExpr, Generic[T, V]):
    @BUILTINS.method(egg_fn="empty")
    @classmethod
    def empty(cls) -> Map[T, V]:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="insert")
    def insert(self, key: T, value: V) -> Map[T, V]:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="get")
    def __getitem__(self, key: T) -> V:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="not-contains")
    def not_contains(self, key: T) -> Unit:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="contains")
    def contains(self, key: T) -> Unit:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="set-union")
    def __or__(self, __t: Map[T, V]) -> Map[T, V]:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="set-diff")
    def __sub__(self, __t: Map[T, V]) -> Map[T, V]:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="set-intersect")
    def __and__(self, __t: Map[T, V]) -> Map[T, V]:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="map-remove")
    def map_remove(self, key: T) -> Map[T, V]:  # type: ignore[empty-body]
        ...


@BUILTINS.class_(egg_sort="Rational")
class Rational(BaseExpr):
    @BUILTINS.method(egg_fn="rational")
    def __init__(self, num: i64Like, den: i64Like):
        ...

    @BUILTINS.method(egg_fn="+")
    def __add__(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="-")
    def __sub__(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="*")
    def __mul__(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="/")
    def __truediv__(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="min")
    def min(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="max")
    def max(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="neg")
    def __neg__(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="abs")
    def __abs__(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="floor")
    def floor(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="ceil")
    def ceil(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="round")
    def round(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="pow")
    def __pow__(self, other: Rational) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="log")
    def log(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="sqrt")
    def sqrt(self) -> Rational:  # type: ignore[empty-body]
        ...

    @BUILTINS.method(egg_fn="cbrt")
    def cbrt(self) -> Rational:  # type: ignore[empty-body]
        ...