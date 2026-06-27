from codespec.core.ids import CSRIdGenerator
from codespec.core.graph import CSRGraph

from codespec.model.entities.module import Module
from codespec.model.entities.routine import Routine
from codespec.model.entities.variable import Variable

from codespec.model.statements.block import Block
from codespec.model.statements.return_ import Return

from codespec.model.expressions.variable_reference import VariableReference
from codespec.model.expressions.binary_operation import BinaryOperation


def build_csr_from_code(code: str, language: str, graph: CSRGraph):
    """
    VERY SIMPLIFIED DEMO BUILDER.

    In production:
    - Replace with Tree-sitter AST traversal
    """

    id_gen = CSRIdGenerator()

    module = Module(
        id=id_gen.new("MODULE"),
        name=f"{language}_module"
    )

    graph.add_node(module, is_root=True)

    # ---------------------------
    # Fake parsing: detect "add"
    # ---------------------------

    routine = Routine(
        id=id_gen.new("ROUTINE"),
        name="add"
    )

    a = Variable(id=id_gen.new("VARIABLE"), name="a", kind="VARIABLE")
    b = Variable(id=id_gen.new("VARIABLE"), name="b", kind="VARIABLE")

    routine.add_parameter(a)
    routine.add_parameter(b)

    # Expression: a + b
    expr = BinaryOperation(
        id=id_gen.new("EXPR"),
        left=VariableReference(id=id_gen.new("EXPR"), variable=a),
        right=VariableReference(id=id_gen.new("EXPR"), variable=b),
        operator="ADD"
    )

    ret = Return(
        id=id_gen.new("STMT"),
        value=expr
    )

    block = Block(id=id_gen.new("BLOCK"))
    block.add_statement(ret)

    routine.set_body(block)

    module.add_routine(routine)

    graph.add_node(routine)
    graph.add_node(block)

    return graph