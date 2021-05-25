import pytest

from xmlrecords.src import xmlrecords

# Basic case: rows only
xml_0_0 = b"""\
<Catalog>
    <Book title="Sunny Night" author="Mysterious Mark" year="2014" price="10.2" />
    <Book title="Babel-17" author="Samuel R. Delany" year="1966" price="2.32" />
</Catalog>
"""

xml_0_1 = b"""\
<Catalog>
    <Shelf>
        <Book title="Sunny Night" author="Mysterious Mark" year="2014" price="10.2" />
        <Book title="Babel-17" author="Samuel R. Delany" year="1966" price="2.32" />
    </Shelf>
</Catalog>
"""

xml_0_2 = b"""\
<Catalog>
    <Book>
        <title>Sunny Night</title>
        <author>Mysterious Mark</author>
        <year>2014</year>
        <price>10.2</price>
    </Book>
    <Book>
        <title>Babel-17</title>
        <author>Samuel R. Delany</author>
        <year>1966</year>
        <price>2.32</price>
    </Book>
</Catalog>
"""

xml_0_3 = b"""\
<Catalog>
    <Book title="Sunny Night">
        <author>Mysterious Mark</author>
        <year>2014</year>
        <price>10.2</price>
    </Book>
    <Book title="Babel-17">
        <author>Samuel R. Delany</author>
        <year>1966</year>
        <price>2.32</price>
    </Book>
</Catalog>
"""

xml_0_4 = b"""\
<Catalog xmlns="darkwoodlib:storage">
    <Book title="Sunny Night">
        <author>Mysterious Mark</author>
        <year>2014</year>
        <price>10.2</price>
    </Book>
    <Book title="Babel-17">
        <author>Samuel R. Delany</author>
        <year>1966</year>
        <price>2.32</price>
    </Book>
</Catalog>
"""

records_0 = [
    {"title": "Sunny Night", "author": "Mysterious Mark", "year": "2014", "price": "10.2"},
    {"title": "Babel-17", "author": "Samuel R. Delany", "year": "1966", "price": "2.32"},
]


# Rows, metadata and prefixes
xml_1 = b"""\
<Catalog>
    <Library>
        <Name>Virtual Shore</Name>
    </Library>
    <Shelf>
        <Timestamp>2020-02-02T05:12:22</Timestamp>
        <Book title="Sunny Night" author="Mysterious Mark" year="2014" price="10.2" />
        <Book title="Babel-17" author="Samuel R. Delany" year="1966" price="2.32" />
    </Shelf>
</Catalog>
"""

records_1_0 = [
    {
        "Name": "Virtual Shore",
        "Timestamp": "2020-02-02T05:12:22",
        "title": "Sunny Night",
        "author": "Mysterious Mark",
        "year": "2014",
        "price": "10.2",
    },
    {
        "Name": "Virtual Shore",
        "Timestamp": "2020-02-02T05:12:22",
        "title": "Babel-17",
        "author": "Samuel R. Delany",
        "year": "1966",
        "price": "2.32",
    },
]

records_1_1 = [
    {
        "Library_Name": "Virtual Shore",
        "Shelf_Timestamp": "2020-02-02T05:12:22",
        "Shelf_Book_title": "Sunny Night",
        "Shelf_Book_author": "Mysterious Mark",
        "Shelf_Book_year": "2014",
        "Shelf_Book_price": "10.2",
    },
    {
        "Library_Name": "Virtual Shore",
        "Shelf_Timestamp": "2020-02-02T05:12:22",
        "Shelf_Book_title": "Babel-17",
        "Shelf_Book_author": "Samuel R. Delany",
        "Shelf_Book_year": "1966",
        "Shelf_Book_price": "2.32",
    },
]


# Nested rows
xml_2 = b"""\
<Catalog>
    <Book>
        <title>Sunny Night</title>
        <Author>
            <name>Mysterious Mark</name>
            <alive>no</alive>
        </Author>
        <year>2014</year>
        <price>10.2</price>
    </Book>
    <Book>
        <title>Babel-17</title>
        <Author>
            <name>Samuel R. Delany</name>
            <alive>yes</alive>
        </Author>
        <year>1966</year>
        <price>2.32</price>
    </Book>
</Catalog>
"""

records_2_0 = [
    {
        "title": "Sunny Night",
        "name": "Mysterious Mark",
        "alive": "no",
        "year": "2014",
        "price": "10.2",
    },
    {
        "title": "Babel-17",
        "name": "Samuel R. Delany",
        "alive": "yes",
        "year": "1966",
        "price": "2.32",
    },
]

records_2_1 = [
    {"title": "Sunny Night", "year": "2014", "price": "10.2"},
    {"title": "Babel-17", "year": "1966", "price": "2.32"},
]

records_2_2 = [
    {
        "title": "Sunny Night",
        "name": "Mysterious Mark",
        "alive": "no",
        "year": "2014",
        "price": "10.2",
        "num": "0",
    },
    {
        "title": "Babel-17",
        "name": "Samuel R. Delany",
        "alive": "yes",
        "year": "1966",
        "price": "2.32",
        "num": "1",
    },
]


# Nested repeated rows (= subrows)
xml_3 = b"""\
<Catalog>
    <Book>
        <title>Sunny Night</title>
        <Author>
            <name>Mysterious Mark</name>
            <alive>no</alive>
        </Author>
        <Author>
            <name>Mysterious Joe</name>
            <alive>no</alive>
        </Author>
        <Author>
            <name>Mysterious Pete</name>
            <alive>yes</alive>
        </Author>
        <year>2014</year>
    </Book>
    <Book>
        <title>Babel-17</title>
        <Author>
            <name>Samuel R. Delany</name>
            <alive>yes</alive>
        </Author>
        <year>1966</year>
    </Book>
</Catalog>
"""

records_3_0 = [
    {
        "title": "Sunny Night",
        "name": "Mysterious Mark",
        "alive": "no",
        "year": "2014",
    },
    {
        "title": "Sunny Night",
        "name": "Mysterious Joe",
        "alive": "no",
        "year": "2014",
    },
    {
        "title": "Sunny Night",
        "name": "Mysterious Pete",
        "alive": "yes",
        "year": "2014",
    },
    {
        "title": "Babel-17",
        "name": "Samuel R. Delany",
        "alive": "yes",
        "year": "1966",
    },
]


records_3_1 = [
    {
        "title": "Sunny Night",
        "name": "Mysterious Mark",
        "alive": "no",
        "year": "2014",
        "num": "0",
    },
    {
        "title": "Sunny Night",
        "name": "Mysterious Joe",
        "alive": "no",
        "year": "2014",
        "num": "1",
    },
    {
        "title": "Sunny Night",
        "name": "Mysterious Pete",
        "alive": "yes",
        "year": "2014",
        "num": "2",
    },
    {
        "title": "Babel-17",
        "name": "Samuel R. Delany",
        "alive": "yes",
        "year": "1966",
        "num": "0",
    },
]


records_3_2 = [
    {
        "title": "Sunny Night",
        "name_0": "Mysterious Mark",
        "alive_0": "no",
        "name_1": "Mysterious Joe",
        "alive_1": "no",
        "name_2": "Mysterious Pete",
        "alive_2": "yes",
        "year": "2014",
    },
    {
        "title": "Babel-17",
        "name_0": "Samuel R. Delany",
        "alive_0": "yes",
        "year": "1966",
    },
]

# TODO: add option to collapse sub-rows
# records_3_3 = [
#     {
#         "title": "Sunny Night",
#         "author": [
#             {
#                 "name": "Mysterious Mark",
#                 "alive": "no",
#             },
#             {
#                 "name": "Mysterious Joe",
#                 "alive": "no",
#             },
#             {
#                 "name": "Mysterious Pete",
#                 "alive": "yes",
#             },
#         ],
#         "year": "2014",
#     },
#     {
#         "title": "Babel-17",
#         "author": [
#             {
#                 "name": "Samuel R. Delany",
#                 "alive": "yes",
#             },
#         ],
#         "year": "1966",
#     },
# ]


def _assert_equal_records(records1, records2):
    assert len(records1) == len(records2), "Different length"
    for r1, r2 in zip(records1, records2):
        assert r1 == r2, "Dict mis-match"


@pytest.mark.parametrize(
    "input_xml,expected_output,kwargs",
    [
        (xml_0_0, records_0, dict(rows_path=["Book"])),
        (xml_0_1, records_0, dict(rows_path=["Shelf", "Book"])),
        (xml_0_2, records_0, dict(rows_path=["Book"])),
        (xml_0_3, records_0, dict(rows_path=["Book"])),
        (xml_0_4, records_0, dict(rows_path=["Book"])),
        (
            xml_1,
            records_1_0,
            dict(
                rows_path=["Shelf", "Book"],
                meta_paths=[["Library", "Name"], ["Shelf", "Timestamp"]],
            ),
        ),
        (
            xml_1,
            records_1_1,
            dict(
                rows_path=["Shelf", "Book"],
                meta_paths=[["Library", "Name"], ["Shelf", "Timestamp"]],
                rows_prefix=True,
                meta_prefix=True,
            ),
        ),
        (xml_2, records_2_0, dict(rows_path=["Book"])),
        (xml_2, records_2_1, dict(rows_path=["Book"], rows_max_depth=1)),
        (xml_2, records_2_2, dict(rows_path=["Book"], enumerate_rows="num")),
        (xml_3, records_3_0, dict(rows_path=["Book"], subrow_tag="Author")),
        (
            xml_3,
            records_3_1,
            dict(rows_path=["Book"], subrow_tag="Author", enumerate_subrows="num"),
        ),
        (xml_3, records_3_2, dict(rows_path=["Book"], subrow_tag="Author", subrow_explode=False)),
        # (xml_3, records_3_3, dict(rows_path=["Book"], subrow_tag="Author")),
    ],
)
def test_parse(input_xml, expected_output, kwargs):
    records = xmlrecords.parse(input_xml, **kwargs)
    _assert_equal_records(records, expected_output)


@pytest.mark.parametrize(
    "input_xml,expected_output,kwargs",
    [
        (xml_0_0, records_0, dict(rows_path=["Book"])),
    ],
)
def test_validate(input_xml, expected_output, kwargs):
    records = xmlrecords.parse(input_xml, **kwargs)
    xmlrecords.validate(records, list(expected_output[0].keys()))


@pytest.mark.parametrize(
    "input_xml,expected_output,kwargs",
    [
        (xml_0_0, records_0, dict(rows_path=["Book"])),
    ],
)
def test_validate_error(input_xml, expected_output, kwargs):
    records = xmlrecords.parse(input_xml, **kwargs)
    with pytest.raises(xmlrecords.XMLValidationError):
        xmlrecords.validate(records, list(expected_output[0].keys())[:-1])
