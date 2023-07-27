import argparse
import certifi
import json
import pycurl
import re

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

from tabulate import tabulate

def get_stations_given_searchstr(key: str, search_str: str, max_results: int = 10, stations_only: bool = True):
    headers = {}
    def header_function(header_line):
        """ from http://pycurl.io/docs/latest/quickstart.html """

        # HTTP standard specifies that headers are encoded in iso-8859-1.
        # On Python 2, decoding step can be skipped.
        # On Python 3, decoding step is required.
        header_line = header_line.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines...
        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        # Note: this only works when headers are not duplicated, see below.
        headers[name] = value

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, f"https://api.sl.se/api2/typeahead.json?key={key}&searchstring={search_str}&stationsonly={stations_only}&maxresults={max_results}")
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.HEADERFUNCTION, header_function)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()

    # Figure out encoding
    # Figure out what encoding was sent with the response, if any.
    # Check against lowercased header name.
    encoding = None
    if 'content-type' in headers:
        content_type = headers['content-type'].lower()
        match = re.search('charset=(\S+)', content_type)
        if match:
            encoding = match.group(1)

    if encoding is None:
        # Default encoding for HTML is iso-8859-1.
        # Other content types may have different default encoding,
        # or in case of binary data, may have no encoding at all.
        encoding = 'iso-8859-1'


    body = buffer.getvalue()
    # Decode using the encoding we figured out.
    data = json.loads(body.decode(encoding))

    search_result = data['ResponseData']
    print(tabulate(search_result, headers="keys"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="blubb"
    )

    parser.add_argument("key", help="The API key.")

    parser.add_argument("search_string", help="The search string.")

    parser.add_argument(
        "max_result", help="The number of search results.", type=int, default=10
    )

    args = parser.parse_args()

    get_stations_given_searchstr(args.key, args.search_string, args.max_result)

