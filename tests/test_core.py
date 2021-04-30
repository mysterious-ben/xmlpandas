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


# Rows and metadata
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

records_1 = [
    {
        "Library_Name": "Virtual Shore",
        "Shelf_Timestamp": "2020-02-02T05:12:22",
        "title": "Sunny Night",
        "author": "Mysterious Mark",
        "year": "2014",
        "price": "10.2",
    },
    {
        "Library_Name": "Virtual Shore",
        "Shelf_Timestamp": "2020-02-02T05:12:22",
        "title": "Babel-17",
        "author": "Samuel R. Delany",
        "year": "1966",
        "price": "2.32",
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
            records_1,
            dict(
                rows_path=["Shelf", "Book"],
                meta_paths=[["Library", "Name"], ["Shelf", "Timestamp"]],
            ),
        ),
        (xml_2, records_2_0, dict(rows_path=["Book"])),
        (xml_2, records_2_1, dict(rows_path=["Book"], rows_max_depth=1)),
    ],
)
def test_convert(input_xml, expected_output, kwargs):
    records = xmlrecords.parse(input_xml, **kwargs)
    _assert_equal_records(records, expected_output)
