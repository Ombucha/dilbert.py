"""
MIT License

Copyright (c) 2022 Omkaar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

from datetime import datetime
from urllib.request import Request, urlopen
from string import ascii_uppercase
from typing import List, Literal, Optional

from bs4 import BeautifulSoup
from requests.utils import requote_uri

from .endpoints import BASE_URL
from .comic import Comic


def search(text: str, *, month: datetime = None, year: datetime = None, page: Optional[int] = None, sort: Optional[Literal["relevance", "ascending", "descending"]] = "relevance") -> List[Comic]:
    """
    Searches Dilbert.

    :param text: The text to search for.
    :type text: str
    :param category: The category to search in.
    :type category: Optional[Literal["comic", "feature"]]
    :param page: The page number.
    :type page: Optional[:class:`int`]
    :param sort: The method of sorting results (based on date).
    :type sort: Optional[Literal["ascending", "descending"]]
    """

    def _encode(base: str, parameters: dict) -> str:
        url = base
        for key, value in parameters.items():
            if value is not None:
                url += f"{key}={value}&"
        return url[:-1]

    month = month.month if month else None
    year = year.year if year else None

    sorts = {"relevance": "relevance", "ascending": "date_asc", "descending": "date_desc"}
    parameters = {"terms": text, "page": page, "sort": sorts[sort.lower()], "month": month, "year": year}
    url = requote_uri(_encode(f"{BASE_URL}search_results?", parameters))

    page = Request(url)
    with urlopen(page) as result:
        soup = BeautifulSoup(result.read(), "html.parser")

    comics = []

    urls = [tag.attrs["href"] for tag in soup.find_all("a", {"class": "img-comic-link"})]
    for url in urls:
        comic = Comic(datetime.strptime(url[26:], "%Y-%m-%d"))
        comics.append(comic)

    return comics


def keywords(letter: str) -> List[str]:
    """
    Fetches popular keywords from Dilbert.

    :param letter: The first letter of the keywords.
    :type letter: str
    """
    letter = letter.upper()

    if letter not in ascii_uppercase:
        raise ValueError("'letter' should be a valid alphabet.")

    url = f"{BASE_URL}search/keywords/{letter}"
    page = Request(url)
    with urlopen(page) as result:
        soup = BeautifulSoup(result.read(), "html.parser")

    tags = soup.find_all("ul")[6].text[2:-2].split("\n\n\n")
    return tags
