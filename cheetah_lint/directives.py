import functools
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

import lxml.etree
from refactorlib.node import ExactlyOneError

from cheetah_lint.imports import CheetahFromImport
from cheetah_lint.imports import CheetahImport
from cheetah_lint.imports import CheetahImportImport

T = TypeVar('T', bound=CheetahImport)


def get_compiler_settings_directive(
        xmldoc: lxml.etree.Element,
) -> Optional[lxml.etree.Element]:
    try:
        return xmldoc.xpath_one('./compiler-settings')
    except ExactlyOneError:
        return None


def _get_special_directive(
        xmldoc: lxml.etree.Element,
        directive: str,
) -> Optional[lxml.etree.Element]:
    try:
        return xmldoc.xpath_one(
            f'./Directive[starts-with(., "{directive}")]',
        )
    except ExactlyOneError:
        return None


get_extends_directive = functools.partial(
    _get_special_directive, directive='#extends',
)
get_implements_directive = functools.partial(
    _get_special_directive, directive='#implements',
)


def _get_import_helper(
        xmldoc: lxml.etree.Element,
        directive_cls: Type[T],
) -> List[T]:
    xml_elements = xmldoc.xpath(
        './Directive['
        '    SimpleExprDirective/UnbracedExpression/Py[1]['
        "        text() = '{}'"
        '    ]'
        ']'.format(
            directive_cls.IMPORT_NAME,
        ),
    )
    return [directive_cls(xml_element) for xml_element in xml_elements]


def get_from_imports(xmldoc: lxml.etree.Element) -> List[CheetahFromImport]:
    return _get_import_helper(xmldoc, CheetahFromImport)


def get_import_imports(
        xmldoc: lxml.etree.Element,
) -> List[CheetahImportImport]:
    return _get_import_helper(xmldoc, CheetahImportImport)


def get_all_imports(xmldoc: lxml.etree.Element) -> List[CheetahImport]:
    return [*get_import_imports(xmldoc), *get_from_imports(xmldoc)]
