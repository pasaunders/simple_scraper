"""A simple web scraper for king county restaurant data."""

from bs4 import BeautifulSoup
import requests
import sys
import re


def get_inspection_page(**kwargs):
    INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
    INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
    INSPECTION_PARAMS = {
        'Output': 'W',
        'Business_Name': '',
        'Business_Address': '',
        'Longitude': '',
        'Latitude': '',
        'City': '',
        'Zip_Code': '',
        'Inspection_Type': 'All',
        'Inspection_Start': '',
        'Inspection_End': '',
        'Inspection_Closed_Business': 'A',
        'Violation_Points': '',
        'Violation_Red_Points': '',
        'Violation_Descr': '',
        'Fuzzy_Search': 'N',
        'Sort': 'H'
    }
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    parameters = INSPECTION_PARAMS.copy()
    for key, value in kwargs.items():
        if key in INSPECTION_PARAMS:
            parameters[key] = value
    response = requests.get(url, params=parameters)
    return response.content, response.encoding

def load_inspection_page(**kwargs):
    """Load a recorded search response."""
    with open('inspection_page.html', 'r') as file:
        content = file.read()
        encoding = 'utf-8'
    return content, encoding


def parse_source(html, encoding='utf-8'):
    """Parsed search report."""
    html_soup = BeautifulSoup(html, 'html5lib', from_encoding=encoding)
    return html_soup


def extract_data_listings(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(elem):
    """Check if element is a table with two <td>s """
    is_tr = elem.name == 'tr'
    td_children = elem.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two


def clean_data(td):
    data = td.string
    try:
        return data.strip(" \n:-")
    except AttributeError:
        return u""


def extract_restaurant_metadata(elem):
    """Add resturant data to dict."""
    metadata_rows = elem.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for row in metadata_rows:
        key_cell, val_cell = row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata


def is_inspection_row(elem):
    """Filter function, finds rows."""
    is_tr = elem.name == 'tr'
    if not is_tr:
        return False
    td_children = elem.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_tr and has_four and contains_word and does_not_start


def extract_score_data(elem):
    """Extract inpsection scores by restraunt."""
    inspection_rows = elem.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += intval
            high_score = intval if intval > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'High Score': high_score,
        u'Total Inspections': samples
    }
    return data


if __name__=="__main__":
    kwargs = {
        'Inspection_Start': '2/1/2013',
        'Inspection_End': '2/1/2015',
        'Zip_Code': '98109'
    }
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = load_inspection_page()
    else:
        html, encoding = get_inspection_page(**kwargs)
    doc = parse_source(html, encoding)
    listings = extract_data_listings(doc)
    # for listing in listings[:5]:
    #     metadata = extract_restaurant_metadata(listing)
    #     inspection_rows = listing.find_all(is_inspection_row)
    #     for row in inspection_rows:
    #         print(row.text)
    for listing in listings:
        metadata = extract_restaurant_metadata(listing)
        inspection_row = listing.find_all(is_inspection_row)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        for key, value in metadata.items():
            print(key, value)
        print()