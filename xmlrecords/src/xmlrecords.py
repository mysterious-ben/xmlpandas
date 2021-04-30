from typing import Dict, List, Optional
from xml.etree import ElementTree


def _update_dict_nocollision(d1: dict, d2: dict) -> None:
    expected_length = len(d1) + len(d2)
    d1.update(d2)
    if len(d1) != expected_length:
        common_keys = set(d1.keys()).intersection(set(d2.keys()))
        raise ValueError(
            f"Dictionaries have common keys: {common_keys} (try setting prefix to True)"
        )


def _process_tag(tag: str, remove_namespace: bool) -> str:
    if remove_namespace:
        _, _, tag = tag.rpartition("}")
        if ("{" in tag) or ("}" in tag):
            raise AssertionError(f"Unexpected tag format after namespace removal: {tag}")
    return tag


def _update_dict_from_node(
    d: dict,
    node: ElementTree.Element,
    prefix: Optional[str],
    sep: str,
    max_depth: Optional[int],
    strip: bool,
    rm_namespace: bool,
) -> None:
    if node.text is not None:
        text = node.text.strip() if strip else node.text
        if len(text) > 0:
            k = _process_tag(node.tag, rm_namespace) if prefix is None else prefix
            _update_dict_nocollision(d, {k: text})
    if len(node.attrib) > 0:
        _update_dict_nocollision(
            d, {k if prefix is None else prefix + sep + k: v for k, v in node.attrib.items()}
        )
    if ((max_depth is None) or (max_depth > 0)) and len(node) > 0:
        max_depth = max_depth if max_depth is None else max_depth - 1
        for child in node:
            k_ = None if prefix is None else prefix + sep + _process_tag(child.tag, rm_namespace)
            _update_dict_from_node(d, child, k_, sep, max_depth, strip, rm_namespace)


def _list_to_path(chunks: List[str], ns: str) -> str:
    ns_ = "{" + ns + "}"
    return f"{ns_}" + f"/{ns_}".join(chunks)


def _list_to_prefix(chunks: List[str], sep: str) -> Optional[str]:
    return sep.join(chunks) if len(chunks) > 0 else None


def parse(
    xml: bytes,
    rows_path: List[str],
    meta_paths: Optional[List[List[str]]] = None,
    rows_prefix: bool = False,
    meta_prefix: bool = True,
    sep: str = "_",
    rows_max_depth: Optional[int] = None,
    meta_max_depth: Optional[int] = None,
    strip_text: bool = True,
    namespace: str = "*",
    remove_namespace: bool = True,
) -> List[Dict]:
    """Convert XML data to a list of records

    :param xml: XML bytes object
    :param rows_path: bits to construct XPath to rows
        Rows are XML nodes with the same tag and (usually) the same structure
        Example: ['Library', 'Catalog', 'Book']
    :param meta_paths: bits to construct XPaths to metadata
        Metadata are XML nodes that will be append to every row
        Example: [['Library', 'Name'], ['Library', 'Founder']]
    :param rows_prefix: if true, add a prefix to row fields
        Set to True if dictionary key collide
    :param meta_prefix: if true, add a prefix to metadata fields
        Set to True if dictionary key collide
    :param sep: a separator used in the prefix
    :param rows_max_depth: maximum depth of nested nodes for rows
        None = unlimited
        0 = no nested nodes
    :param meta_max_depth: maximum depth of nested nodes for metadata
    :param strip_text: if true, apply str.strip function to XML values
        Set to True if XML has redundant space or new line characters
    :return: list of records
    """

    tree = ElementTree.fromstring(xml)

    if meta_paths is None:
        meta_paths = []

    meta_d = {}
    for m_path in meta_paths:
        m_node = tree.find(_list_to_path(m_path, namespace), {})
        if m_node is not None:
            prefix = _list_to_prefix(m_path, sep) if meta_prefix else None
            _update_dict_from_node(
                meta_d, m_node, prefix, sep, meta_max_depth, strip_text, remove_namespace
            )

    record_nodes = tree.findall(_list_to_path(rows_path, namespace), {})
    records = []
    prefix = _list_to_prefix(rows_path, sep) if rows_prefix else None
    for r_node in record_nodes:
        records_d = dict(**meta_d)
        _update_dict_from_node(
            records_d, r_node, prefix, sep, rows_max_depth, strip_text, remove_namespace
        )
        records.append(records_d)
    return records
