# pylint: skip-file
import pytest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch
from process import get_total_sub_tags, get_article_title, get_article_year, get_email, get_postcode


def test_get_total_sub_tags():
    test_ET_1 = ET.fromstring("<a><b></b><c></c></a>")
    test_ET_2 = ET.fromstring("<a><b><d>fake info</d></b><c></c></a>")
    test_ET_empty = ET.fromstring("<a></a>")

    assert get_total_sub_tags(test_ET_1) == 2
    assert get_total_sub_tags(test_ET_2) == 2
    assert get_total_sub_tags(test_ET_empty) == 0


def test_get_article_title():
    test_article = ET.fromstring(
        "<Article><ArticleTitle>Fake Title</ArticleTitle></Article>")
    test_article_null = ET.fromstring(
        "<Article><b><ArticleTitle>Fake Title</ArticleTitle></b></Article>")

    assert get_article_title(test_article) == "Fake Title"
    assert get_article_title(test_article_null) == None


def test_get_article_year_no_year():
    test_article_no_year = ET.fromstring(
        "<Article><ArticleDate>Fake Title</ArticleDate></Article>")
    assert get_article_year(test_article_no_year) == None


def test_get_article_year_no_ArticleDate():
    test_article = ET.fromstring(
        "<Article><a><year>0000</year></a></Article>")
    assert get_article_year(test_article) == None


def test_get_article_year():
    test_article = ET.fromstring(
        "<Article><ArticleDate><Year>0000</Year></ArticleDate></Article>")
    assert get_article_year(test_article) == '0000'


def test_get_email():
    text = "fjdskhjk kjdflk fake-email@gmail.com. jdlkj"
    assert get_email(text) == "fake-email@gmail.com"


def test_get_email_numeric():
    text = "jjdkjf dhkjf39 dj 2fake_email9@jds.com"
    assert get_email(text) == '2fake_email9@jds.com'


def test_get_email_country_code():
    text_1 = "jjdkjf dhkjf39 dj 2fake_email9@jds.co.uk"
    text_2 = "jjdkjf dhkjf39 dj 2fake_email9@jds.org.us"

    assert get_email(text_1) == "2fake_email9@jds.co.uk"
    assert get_email(text_2) == "2fake_email9@jds.org.us"


def test_get_email_incorrect_format():
    text = "jjdkjf dhkjf39 dj 2fake_email9@jds"

    assert get_email(text) is None


def test_get_postcode_invalid_country():
    country = "FAKEUK"
    affiliation = "Fake University SE19 8SD"

    assert get_postcode(country, affiliation) is None


def test_get_postcode_UK_valid_format():
    test_code_1 = "Fake organisation address street AA9A 9AA."
    test_code_2 = "djfhkj A9A 9AA fdhskljhflk"
    test_code_3 = "ahkljdh.djfkljA9 9AA jdkhsjk"
    test_code_4 = "ahhj37hdfhsn kejsl A99 9AA kdhf3 hfd33"
    test_code_5 = "dshjkf yieAA9 9AA, ljdsiaiojf"
    test_code_6 = "ajlkdjfAA99 9AA.dkljfdas"

    assert get_postcode("UK", test_code_1) == "AA9A 9AA"
    assert get_postcode("UK", test_code_2) == "A9A 9AA"
    assert get_postcode("UK", test_code_3) == "A9 9AA"
    assert get_postcode("UK", test_code_4) == "A99 9AA"
    assert get_postcode("UK", test_code_5) == "AA9 9AA"
    assert get_postcode("UK", test_code_6) == "AA99 9AA"


def test_get_postcode_UK_invalid_format():
    test_code_1 = "dfkljds. 9A9 9AA."
    test_code_2 = "djskl 9AA9A 999. "

    assert get_postcode("UK", test_code_1) is None
    assert get_postcode("UK", test_code_2) is None


def test_get_postcode_USA_valid_format():
    test_code_1 = "Fake ville Street 12345."
    test_code_2 = "Fake ville Street 12345-1234."
    assert get_postcode("USA", test_code_1) == "12345"
    assert get_postcode("USA", test_code_2) == "12345-1234"


def test_get_postcode_USA_invalid_format():
    test_code_1 = "Fake ville Street 112345."
    test_code_2 = "Fake ville Street 112345-1234."
    assert get_postcode("USA", test_code_1) == None
    assert get_postcode("USA", test_code_2) == None


def test_get_postcode_Canada_valid_format():
    test_code = "Fake-toronto A1A 1A1."

    assert get_postcode("Canada", test_code) == "A1A 1A1"


def test_get_postcode_Canada_invalid_format():
    test_code_1 = "dfkljds. 9A9 9AA."
    test_code_2 = "djskl AA1A 1A1. "

    assert get_postcode("Canada", test_code_1) is None
    assert get_postcode("Canada", test_code_2) is None
