# XML Records

This package extracts tabular data from XML.

>>> This data provider sends all his data in... XML. You know nothing about XML, except that it looks kind of weird and you would *definitely* never use it for tabular data. You don't know what "tags", "attributes" and "XPaths" are, and you don't want to know it. Could you just transform this XML nightmare into a sensible tabular format, like a DataFrame? Don't worry: you are in the right place!


# Installation

```shell script
pip install xmlrecords
```

- The package requires `python 3.7+` and no external dependencies.
- The package uses `xml.etree.ElementTree` so it's vulnerable to [billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack).

# Usage

## Basic example

Usually, you only need to specify path to table rows; optionally, you can specify paths to any extra data you'd like to add to your table:

```python
# XML object
xml_bytes = b"""\
<?xml version="1.0" encoding="utf-8"?>
<Catalog>
    <Library>
        <Name>Virtual Shore</Name>
    </Library>
    <Shelf>
        <Timestamp>2020-02-02T05:12:22</Timestamp>
        <Book>
            <Title>Sunny Night</Title>
            <Author alive="no" name="Mysterious Mark"/>
            <Year>2017</Year>
            <Price>112.34</Price>
        </Book>
        <Book>
            <Title>Babel-17</Title>
            <Author alive="yes" name="Samuel R. Delany"/>
            <Year>1963</Year>
            <Price>10</Price>
        </Book>
    </Shelf>
</Catalog>
"""

# Transform XML to records (= a list of key-value pairs)
import xmlrecords
records = xmlrecords.parse(
    xml=xml_bytes, 
    records_path=['Shelf', 'Book'],  # The rows are XML nodes with the repeating tag <Book>
    meta_paths=[['Library', 'Name'], ['Shelf', 'Timestamp']]  # Optionally, you can add more data
)
for r in records:
    print(r)

# Output:
# {'Library_Name': 'Virtual Shore', 'Shelf_Timestamp': '2020-02-02T05:12:22', 'Title': 'Sunny Night', 'alive': 'no', 'name': 'Mysterious Mark', 'Year': '2017', 'Price': '112.34'}
# {'Library_Name': 'Virtual Shore', 'Shelf_Timestamp': '2020-02-02T05:12:22', 'Title': 'Babel-17', 'alive': 'yes', 'name': 'Samuel R. Delany', 'Year': '1963', 'Price': '10'}
``` 

## With Pandas

You can easily transform records to a pandas DataFrame:

```python
import pandas as pd
df = pd.DataFrame(records)
```

## With SQL

You can use records directly with INSERT statements if your SQL database is [PEP 249 compliant](https://www.python.org/dev/peps/pep-0249/). Most SQL databases are.

SQLite is an exception. There, you'll have to transform records (= a list of dictionaries) into a list of lists:

```python
import sqlite3
with sqlite3.connect('maindev.db') as conn:
    c = conn.cursor()
    c.execute("""\
        CREATE TABLE BOOKS (
           LIBRARY_NAME TEXT,
           SHELF_TIMESTAMP TEXT,
           TITLE TEXT,
           AUTHOR_ALIVE TEXT,
           AUTHOR_NAME TEXT,
           YEAR INT,
           PRICE FLOAT,
           PRIMARY KEY (TITLE, AUTHOR_NAME)
        )
        """
    )
    c.executemany(
        """INSERT INTO BOOKS VALUES (?,?,?,?,?,?,?)""",
        [list(x.values()) for x in records],
    )
    conn.commit()
```

# FAQ

(This section is left empty as I haven't yet received any question)
