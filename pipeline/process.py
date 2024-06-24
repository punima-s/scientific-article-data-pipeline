from datetime import datetime
import xml.etree.ElementTree as ET
import re
import glob
import pandas as pd
import spacy
from geonamescache import GeonamesCache
import csv
from dotenv import load_dotenv
from os import environ, remove
from rapidfuzz import process, distance, utils
from tqdm import tqdm


def parse_xml_data(filepath: str) -> ET:
    """Parses xml data file into an ET instance."""
    return ET.parse(filepath)


def get_total_sub_tags(root: ET) -> int:
    """Returns the total number of sub element in Element."""
    return len(root) if root is not None else 0


def get_article_title(article_tag: ET.Element) -> str | None:
    """Returns Article Title from Article Element. """
    for info in article_tag.iterfind("./"):
        if info.tag == 'ArticleTitle':
            return info.text
    return None


def get_article_year(article_tag: ET.Element) -> str | None:
    """Returns Year from Article Date in Article Element. """
    for date in article_tag.iterfind("./ArticleDate/"):
        if date.tag == 'Year':
            return date.text
    return None


def get_article_data(root: ET.Element, index: int) -> dict:
    """Returns Article Field from Article Element. """
    article = root[index]
    field = {'PMID': None,
             'Title': None,
             'Year': None,
             'Keywords': None,
             'MESH': None}

    for v in article.iterfind("./MedlineCitation/"):
        if v.tag == 'PMID':
            field['PMID'] = v.text
        if v.tag == 'Article':
            field['Title'] = get_article_title(v)
            field['Year'] = get_article_year(v)
        if v.tag == 'KeywordList':
            key_list = [word.text for word in v.iterfind(
                "./") if word.tag == 'Keyword']
            field['Keywords'] = key_list
        if v.tag == 'MeshHeadingList':
            mesh_list = [info.attrib['UI']
                         for info in v.iterfind(".//") if info.tag == 'DescriptorName']
            field['MESH'] = mesh_list
    return field


def get_author_data(root: ET.Element, article_index: int, author_index: int) -> dict:
    """Return Author field from Article Element. """
    field = {'Firstname': None,
             'Lastname': None,
             'Initials': None,
             'GRID': [],
             'Affiliation': []}

    article = root[article_index]
    author = article.find("./MedlineCitation/Article/AuthorList")[author_index]

    for info in author.iterfind("./"):
        if info.tag == 'ForeName':
            field['Firstname'] = info.text
        if info.tag == 'LastName':
            field['Lastname'] = info.text
        if info.tag == 'Initials':
            field['Initials'] = info.text
        if info.tag == 'AffiliationInfo':
            for institute in info.iterfind("./"):
                if institute.tag == "Affiliation":
                    field['Affiliation'].append(institute.text)
                if institute.tag == "Identifier" and institute.attrib['Source'] == 'GRID':
                    field['GRID'].append(institute.text)

    field['GRID'] = None if field['GRID'] == [] else field['GRID']

    return field


def get_fullname(firstname: str, lastname: str) -> str:
    """Joins firstname and lastname to return a fullname."""
    return f"{firstname.capitalize()} {lastname.capitalize()}" if firstname is not None and lastname is not None else None


def get_email(affiliation: str) -> str:
    """Get email from affiliation."""
    if affiliation is None:
        return None
    email_struc_one = r"([\w?\-\.|]+@[\w]+\.[\w]{2,3}\.[\w]{2})"
    email_struc_two = r"([\w?\-\.|]+@[\w]+\.[\w]{3})"
    x = re.search(email_struc_one, affiliation)
    if x is None:
        x = re.search(email_struc_two, affiliation)
    return x.group() if x is not None else None


def get_country(affiliation, countries_info: dict, nlp_lang: spacy.Language) -> str:
    """Return country if provided in the affiliation."""
    if affiliation is None:
        return None

    doc = nlp_lang(affiliation)
    geo_words = []
    for token in doc:
        if token.ent_type_ == "GPE":
            geo_words.append(token.text)

    for country in countries_info:
        for word in geo_words:
            if (word == countries_info[country][0]
                or word == countries_info[country][1]
                    or word == countries_info[country][2]):
                return word
    return None


def get_postcode(country: str, affiliation: str) -> str:
    """Search for postcode or zipcode in affiliation."""
    recognised_country = ["UK", "USA", "Canada"]
    if country not in recognised_country:
        return None

    if country == "UK":
        code_regex = r"(?<=[\s|a-z])([A-Z]{1,2}\d{1,2}\s\d{1}[A-Z]{2})"
    elif country == "USA":
        code_regex = r"(?<!\d)(\d{5}(-{1}\d{4})?)(?!\d)"
    elif country == "Canada":
        code_regex = r"(?<=[\s|a-z])([A-Z][0-9][A-Z]\s[0-9][A-Z][0-9])"
    else:
        return None

    x = re.search(code_regex, affiliation)

    if country == "UK" and x is None:
        x = re.search(
            r"(?<=[\s|a-z])([A-Z]{1,2}\d{1}[A-Z]{1}\s\d{1}[A-Z]{2})", affiliation)
    return x.group() if x is not None else None


def create_base_dataframe(root: ET, countries_data: dict, nlp_lang: spacy.Language, grid_institutes: list, match_limit: float) -> pd.DataFrame:
    """Creates a base dataframe of author and affiliations."""
    number_of_article = get_total_sub_tags(root)
    data_to_find = []

    for i in tqdm(range(number_of_article)):

        article_info = get_article_data(root, i)
        author_list = root[i].find("./MedlineCitation/Article/AuthorList")
        number_of_authors = get_total_sub_tags(author_list)

        for n in range(number_of_authors):

            author_info = get_author_data(root, i, n)

            fullname = get_fullname(
                author_info["Firstname"], author_info["Lastname"])
            affiliations = author_info['Affiliation']

            for affiliation in affiliations:

                email = get_email(
                    affiliation)

                country = get_country(
                    affiliation, countries_data, nlp_lang)

                postcode = get_postcode(
                    country, affiliation)

                organisation_name = get_organisation_name(
                    affiliation, nlp_lang)

                grid_aff_name = get_matches(
                    organisation_name, grid_institutes, match_limit)

                data_to_find.append({
                    'Article_PMID': article_info["PMID"],
                    'Article_title': article_info["Title"],
                    'Article_keywords': article_info["Keywords"],
                    'Article_MESH': article_info["MESH"],
                    'Article_year': article_info["Year"],
                    'Author_firstname': author_info["Firstname"],
                    'Author_lastname': author_info["Lastname"],
                    'Author_initials': author_info["Initials"],
                    'Author_fullname': fullname,
                    'Author_email': email,
                    'Affiliation_name_PubMed': affiliation,
                    'Affiliation_name_GRID': grid_aff_name,
                    'Affiliation_zipcode': postcode,
                    'Affiliation_country': country,
                    'Affiliation_GRID_identifier': author_info["GRID"]
                })

    base_df = pd.DataFrame(data=data_to_find)
    return base_df


def list_of_countries() -> dict:
    """Get a dictionary of countries with a list of the name, iso3 and fips codes. """
    gc = GeonamesCache()
    countries = gc.get_countries_by_names()
    countries_list = {}
    for country in countries:
        countries_list[country] = [
            countries[country]['name'], countries[country]['iso3'], countries[country]['fips']]
    return countries_list


def get_organisation_name(affiliation: str, nlp_lang: spacy.Language) -> str:
    """Get name of organisation name from affiliation"""
    if affiliation is None:
        return None
    doc = nlp_lang(affiliation)
    span = doc[0:len(doc)-1]
    ents = list(span.ents)
    org_entities = []
    for entity in ents:
        doc_1 = nlp_lang(entity.text)
        entity_tk = 0
        for token in doc_1:
            entity_tk += 1 if token.ent_type_ == "ORG" else 0
        if len(doc_1) == entity_tk:
            org_entities.append(entity.text)
    if org_entities is not None:
        organisation = "".join(org_entities).split(
            ",")
        if len(organisation) > 1:
            return organisation[-1]
    return organisation[0] if organisation is not None else None


def load_grid_institute_names(filepath: str):
    """Loading grid institute data."""
    institutes = []
    with open(filepath, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            institutes.append(row['name'])
    return institutes


def get_matches(organisation: str, institute_names: list, match_limit: float) -> str:
    """Returns the best matches for grid institute name."""
    if organisation is None:
        return None
    best_match = process.extractOne(organisation, institute_names,
                                    score_cutoff=match_limit, scorer=distance.Levenshtein.normalized_similarity, processor=utils.default_process)
    return best_match[0] if best_match is not None else None


def main(filename: str) -> pd.DataFrame:
    """Main run of function to create the dataframe"""
    load_dotenv()
    MIN_MATCH_VAL = 0.9
    tree = parse_xml_data(filename)
    root = tree.getroot()
    nlp = spacy.load("en_core_web_sm")

    countries_data = list_of_countries()
    grid_institute_names = load_grid_institute_names(
        environ["GRID_INSTITUTE_FILEPATH"])

    result = create_base_dataframe(
        root, countries_data, nlp, grid_institute_names, match_limit=MIN_MATCH_VAL)

    result.to_csv(f"""Punima_{datetime.now().date()}_{
                  datetime.now().minute}.csv""", index=False)

    return result


def get_filename() -> str:
    """Get the filename. """
    files = glob.glob("PubmedArticle_*.xml")
    return files[0] if files else None


def process_main():
    """Main run of functions for processing file data from S3. """
    file = get_filename()
    if file:
        print(file)
        main(file)
        remove(file)
    else:
        print("No new files")


if __name__ == "__main__":
    main("sample.xml")
