# mypy: disable-error-code="empty-body"
from __future__ import annotations

from egglog import *
from egglog.exp.program_gen import *


def test_to_string(snapshot_py) -> None:
    egraph = EGraph([program_gen_module])

    @egraph.class_
    class Math(Expr):
        def __init__(self, value: i64Like) -> None:
            ...

        @classmethod
        def var(cls, v: StringLike) -> Math:
            ...

        def __add__(self, other: Math) -> Math:
            ...

        def __mul__(self, other: Math) -> Math:
            ...

        def __neg__(self) -> Math:
            ...

        @egraph.method(cost=1000)
        @property
        def program(self) -> Program:
            ...

    @egraph.function
    def assume_pos(x: Math) -> Math:
        ...

    @egraph.register
    def _rules(
        s: String,
        y_expr: String,
        z_expr: String,
        old_statements: String,
        x: Math,
        i: i64,
        y: Math,
        z: Math,
        old_gensym: i64,
    ):
        yield rewrite(Math.var(s).program).to(Program(s))
        yield rewrite(Math(i).program).to(Program(i.to_string()))
        yield rewrite((y + z).program).to((y.program + " + " + z.program).assign())
        yield rewrite((y * z).program).to((y.program + " * " + z.program).assign())
        yield rewrite((-y).program).to(Program("-") + y.program)
        assigned_x = x.program.assign()
        yield rewrite(assume_pos(x).program).to(assigned_x.statement(Program("assert ") + assigned_x + " > 0"))

    first = assume_pos(-Math.var("x")) + Math.var("y")
    fn = (first + Math(2) + first).program.function_two("my_fn", Math.var("x").program, Math.var("y").program)
    with egraph:
        egraph.register(fn)
        egraph.run(200)
        fn = egraph.extract(fn)
    egraph.register(fn)
    egraph.register(fn.compile())
    egraph.run(200)
    # egraph.display(n_inline_leaves=1)
    expr = egraph.load_object(egraph.extract(PyObject.from_string(fn.expr)))
    assert expr == "my_fn"  # type: ignore
    stmts = egraph.load_object(egraph.extract(PyObject.from_string(fn.statements)))
    assert stmts == snapshot_py  # type: ignore
