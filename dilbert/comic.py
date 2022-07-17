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
from typing import Optional

from bs4 import BeautifulSoup
from requests import get

from .endpoints import BASE_URL


class Comic:

    """
    A class that represents a comic.

    :param date: The comic's date.
    :type date: Optional[:class:`datetime`]

    :ivar date: The comic's date.
    :ivar image: The URL of the comic's image.
    :ivar title: The title of the comic.
    :ivar rating: The comic's rating.
    :ivar url: The comic's URL.
    :ivar tags: The tags associated with the comic.
    :ivar transcript: The comic's transcript.
    """

    def __init__(self, date: Optional[datetime] = None) -> None:

        now = datetime.now()

        if (date is not None) and ((now.year < date.year) or (now.year == date.year and now.month < date.month) or (now.year == date.year and now.month == date.month and now.day < date.day)):
            raise ValueError("Date must be in the past.")

        self.date = date if date else now
        self.url = f"{BASE_URL}strip/{self.date.strftime('%Y-%m-%d')}"

        if not date and get(self.url).url != self.url:
            latest = datetime(now.year, now.month, now.day - 1)
            self.date = latest
            self.url = f"{BASE_URL}strip/{latest.strftime('%Y-%m-%d')}"

        page = Request(self.url)
        with urlopen(page) as result:
            soup = BeautifulSoup(result.read(), "html.parser")

        tag = soup.find("img", {"class": "img-responsive img-comic"})
        self.image = tag.attrs["src"]
        self.title = soup.find("span", {"class": "comic-title-name"}).text.strip()

        if self.title == "":
            self.title = None

        formatted_date = self.date.strftime("%Y-%m-%d")
        self.rating = float(soup.find("div", {"class": f"comic-rating-{formatted_date}"}).attrs["data-total"])

        try:
            self.tags = soup.find("p", {"class": "small comic-tags"}).text[5:].replace("\n", "").split(",")
            for index, element in enumerate(self.tags):
                self.tags[index] = element.strip()[1:]
        except AttributeError:
            self.tags = None

        try:
            self.transcript = soup.find("div", {"class": "comic-transcript"}).text[11:]
        except AttributeError:
            self.transcript = None

    def __eq__(self, __o: Comic) -> bool:
        return self.url == __o.url
