from __future__ import annotations

from collections.abc import Collection, Hashable
from dataclasses import dataclass, field

import egg_smol.bindings as py


@dataclass(frozen=True)
class Kind:
    python_name: str
    egg_name: str
    n_args: int = 0

    def __getitem__(self, args: tuple[Type_, ...]) -> Type:
        if len(args) != self.n_args:
            raise TypeError(f"Expected {self.n_args} arguments, got {len(args)}")
        return Type(self, args)


@dataclass(frozen=True)
class Type:
    kind: Kind
    args: tuple[Type_, ...]


@dataclass(frozen=True)
class TypeVariable:
    identifier: Hashable


Type_ = TypeVariable | Type


@dataclass
class TypeInference:
    _typevar_to_value: dict[TypeVariable, Type] = field(default_factory=dict)

    def infer_return_type(
        self,
        unbound_arg_types: list[Type_],
        unbound_return_type: Type_,
        arg_types: list[Type],
    ) -> Type:
        self._infer_typevars_zip(unbound_arg_types, arg_types)
        return self._subtitute_typevars(unbound_return_type)

    def _infer_typevars_zip(
        self, unbound: Collection[Type_], bound: Collection[Type_]
    ) -> None:
        if len(unbound) != len(bound):
            raise TypeError(f"Expected {len(unbound)} arguments, got {len(bound)}")
        for unbound_arg, bound_arg in zip(unbound, bound):
            self._infer_typevars(unbound_arg, bound_arg)

    def _infer_typevars(self, unbound: Type_, bound: Type_) -> None:
        if isinstance(bound, TypeVariable):
            raise ValueError("Bound type should not be a typevar")
        if isinstance(unbound, Type):
            if unbound.kind != bound.kind:
                raise TypeError(f"Expected {unbound.kind}, got {bound.kind}")
            self._infer_typevars_zip(unbound.args, bound.args)
            return
        if unbound in self._typevar_to_value:
            if self._typevar_to_value[unbound] != bound:
                raise TypeError(f"Typevar {unbound} already bound to {bound}")
        else:
            self._typevar_to_value[unbound] = bound

    def _subtitute_typevars(self, type_: Type_) -> Type:
        if isinstance(type_, TypeVariable):
            return self._typevar_to_value[type_]
        return Type(
            type_.kind, tuple(self._subtitute_typevars(arg) for arg in type_.args)
        )


def test_type_inference():
    import pytest

    i64 = Kind("i64", "i64")[()]
    unit = Kind("Unit", "Unit")[()]
    Map = Kind("Map", "Map", 2)
    K, V = TypeVariable("K"), TypeVariable("V")
    ti = TypeInference()
    assert ti.infer_return_type([i64], i64, [i64]) == i64
    with pytest.raises(TypeError):
        ti.infer_return_type([i64], i64, [unit])
    with pytest.raises(TypeError):
        ti.infer_return_type([], i64, [unit])

    assert ti.infer_return_type([Map[K, V], K], V, [Map[i64, unit], i64]) == unit

    with pytest.raises(TypeError):
        ti.infer_return_type([Map[K, V], K], V, [Map[i64, unit], unit])


@dataclass
class Function:
    python_name: str
    egg_name: str
    arg_types: list[Type_]
    return_type: Type_

    def __call__(self, *args: Expr) -> Expr:
        ti = TypeInference()
        bound_return_type = ti.infer_return_type(
            self.arg_types, self.return_type, [arg.type for arg in args]
        )
        return Expr(
            bound_return_type,
            py.Call(
                self.egg_name,
                [arg.value for arg in args],
            ),
        )


# Ex:
# K, V = TypeVar(0), TypeVar(1)
# get = Function("get", "get", [Map[K, V], K], V)


@dataclass
class Expr:
    type: Type
    value: py._Expr


@dataclass
class Method:
    python_name: str
    egg_name: str
    arg_types: list[Type]
    return_type: Type


# @dataclass
# class Definitions:


# @dataclass
# class Expr:
#     expr: py._Expr
#     python_tp: PythonTypeID


# @dataclass
# class Function:
#     analysis: Analysis
#     name: str

#     def __call__(self, *args: Expr):
#         egg_name, return_tp = self.analysis.analyze_call(
#             self.name, [arg.python_tp for arg in args]
#         )
#         return Expr(py.Call(egg_name, [arg.expr for arg in args]), return_tp)


# @dataclass
# class BoundMethod:
#     analysis: Analysis
#     name: str
#     owner: Expr

#     def __call__(self, *args: Expr):
#         egg_name, return_tp = self.analysis.analyze_call(
#             (self.owner.python_tp, False, self.name),
#             [self.owner.python_tp] + [arg.python_tp for arg in args],
#         )
#         return Expr(
#             py.Call(egg_name, [self.owner.expr] + [arg.expr for arg in args]), return_tp
#         )


# @dataclass
# class BoundClassMethod:
#     analysis: Analysis
#     egg_name: str
#     owner: PythonTypeID

#     def __call__(self, *args: Expr) -> Expr:
#         egg_name, return_tp = self.analysis.analyze_call(
#             self.egg_name, [self.owner] + [arg.python_tp for arg in args]
#         )
#         return Expr(py.Call(egg_name, [arg.expr for arg in args]), return_tp)


# @dataclass
# @dataclass
# class Analysis:
#     # Mapping so that we can understand the corresponding egg names and types
#     # for the python types.
#     _python_callables: dict[PythonCallableID, PythonCallableValue] = field(
#         default_factory=dict
#     )
#     # Mapping of python type id and whether is_classmethod to a list of method names
#     _tp_to_methods: dict[tuple[str, bool], list[str]] = field(
#         default_factory=lambda: defaultdict(list)
#     )

#     def analyze_call(
#         self, callable_id: PythonCallableID, arg_type_ids: list[PythonTypeID]
#     ) -> tuple[str, PythonTypeID]:
#         """
#         Given some Python function and its argument types, returns the return type of the function
#         as well as the egg function name.

#         Raises NotImplementedError if the function is not supported.
#         """
#         if callable_id not in self._python_callables:
#             raise NotImplementedError

#         egg_name, generate_tp = self._python_callables[callable_id]
#         return egg_name, generate_tp(arg_type_ids)

#     def dir(self, tp_name: str, is_classmethod: bool) -> list[str]:
#         """
#         Return a list of method names for a given type.
#         """
#         return self._tp_to_methods[tp_name, is_classmethod]

#     def register_callable(
#         self, id: PythonCallableID, egg_name: str, generate_tp: GenerateReturnTp
#     ) -> None:
#         """
#         Register a Python function. Pass in it's egg name and a function which takes a list of
#         Python type ids and returns a Python type id.
#         """
#         self._python_callables[id] = egg_name, generate_tp
#         if isinstance(id, tuple):
#             tp_name, is_classmethod, method_name = id
#             self._tp_to_methods[tp_name, is_classmethod].append(method_name)


# # A python type is identified by either its name or a tuple of its name and any argument
# # types, for generic types.
# PythonTypeID: TypeAlias = Union[str, tuple[str, tuple["PythonTypeID", ...]]]

# # A Python callable is either a function, with a name, or a method of a class,
# # either a classmethod or a regular method.
# # These are described by either a str of the fn name or a tuple of the class name, whether
# # its a classmethod, and the fn name.
# PythonMethodID = tuple[str, bool, str]
# PythonCallableID: TypeAlias = Union[str, PythonMethodID]

# # A callable which given a list of Python type ids returns a Python type id of the result.
# GenerateReturnTp = Callable[[list[PythonTypeID]], PythonTypeID]

# # A tuple of the egg function name and a callable which computes the return type
# PythonCallableValue: TypeAlias = tuple[str, GenerateReturnTp]
