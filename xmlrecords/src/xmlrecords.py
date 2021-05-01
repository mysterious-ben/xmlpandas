from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict
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


# TODO: add option to specify text, attributes and child nodes to parse
# @dataclass
# class Fields:
#     text: bool = True
#     attributes: Optional[List[str]] = None
#     nodes: Optional[List[str]] = None


def _update_dict_from_node(
    d: dict,
    node: ElementTree.Element,
    prefix: Optional[str],
    sep: str,
    max_depth: Optional[int],
    strip: bool,
    rm_namespace: bool,
    skip_child_tag: Optional[str],
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
            ctag = _process_tag(child.tag, rm_namespace)
            if (skip_child_tag is None) or (ctag != skip_child_tag):
                k_ = None if prefix is None else prefix + sep + ctag
                _update_dict_from_node(d, child, k_, sep, max_depth, strip, rm_namespace, None)


def _list_to_path(chunks: List[str], ns: str) -> str:
    ns_ = "{" + ns + "}"
    return "/".join(ns_ + c for c in chunks)


def _list_to_prefix(chunks: List[str], sep: str) -> Optional[str]:
    return sep.join(chunks) if len(chunks) > 0 else None


def parse(
    xml: bytes,
    rows_path: List[str],
    subrow_tag: Optional[str] = None,
    meta_paths: Optional[List[List[str]]] = None,
    rows_prefix: bool = False,
    meta_prefix: bool = False,
    sep: str = "_",
    rows_max_depth: Optional[int] = None,
    meta_max_depth: Optional[int] = None,
    strip_text: bool = True,
    namespace: str = "*",
    remove_namespace: bool = True,
) -> List[Dict]:
    """Convert XML data to a list of records

    :param xml: XML bytes object
    :param rows_path: bits to construct XPath to a "row" node
        Rows are XML nodes with the same tag and (usually) the same structure
    :param subrow_tag: tag of a "subrow" node
        Subrow are nested "row" nodes (children of a "row" node)
    :param meta_paths: bits to construct XPaths to metadata
        Metadata are XML nodes that will be append to every row
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
    :param namespace: XML namespace to search
        * = all namespaces
    :param remove_namespace: if true, do not include namespace in the record key
    :return: list of records
    """

    tree = ElementTree.fromstring(xml)

    if meta_paths is None:
        meta_paths = []

    meta_d: dict = {}
    for m_path in meta_paths:
        m_path_ = _list_to_path(m_path, namespace)
        m_node = tree.find(m_path_)
        if m_node is not None:
            prefix = _list_to_prefix(m_path, sep) if meta_prefix else None
            _update_dict_from_node(
                d=meta_d,
                node=m_node,
                prefix=prefix,
                sep=sep,
                max_depth=meta_max_depth,
                strip=strip_text,
                rm_namespace=remove_namespace,
                skip_child_tag=None,
            )

    rows_path_ = _list_to_path(rows_path, namespace)
    subrows_path_ = _list_to_path([subrow_tag], namespace) if subrow_tag is not None else None
    row_nodes = tree.findall(rows_path_)
    records = []
    prefix = _list_to_prefix(rows_path, sep) if rows_prefix else None
    for r_node in row_nodes:
        row_d = dict(**meta_d)
        _update_dict_from_node(
            d=row_d,
            node=r_node,
            prefix=prefix,
            sep=sep,
            max_depth=rows_max_depth,
            strip=strip_text,
            rm_namespace=remove_namespace,
            skip_child_tag=subrow_tag,
        )
        if subrow_tag is None:
            records.append(row_d)
        else:
            subrow_nodes = r_node.findall(subrows_path_)
            for sr_node in subrow_nodes:
                subrow_d = dict(**row_d)
                _update_dict_from_node(
                    d=subrow_d,
                    node=sr_node,
                    prefix=prefix,
                    sep=sep,
                    max_depth=rows_max_depth,
                    strip=strip_text,
                    rm_namespace=remove_namespace,
                    skip_child_tag=None,
                )
                records.append(subrow_d)
    return records


class XMLValidationError(ValueError):
    pass


def validate(records: List[dict], expected_keys: List[str]):
    """Validate that records have all expected keys

    :raises: XMLParsingError
    """
    for i, r in enumerate(records):
        if list(r.keys()) != expected_keys:
            raise XMLValidationError(f"record {i}: {list(r.keys())} != {expected_keys}")
