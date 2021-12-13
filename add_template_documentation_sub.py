"""
A template is a wiki page in which contents can be displayed in other locations around the wiki.
This allow an editor to make a change once and have the changes appear numerous places throughout
the wiki. The {{documentation}} template is used on almost every template page to contain that
template's documented instructions and information.

The intent of this is to add documentation to templates missing it.

Notes - Search for the text "#REDIRECT" on the page. If found, skip adding {{<Documentation}}
"""

import json
import re
import requests
import urllib3
import pywikibot

# Template to append to pages
TEMPLATE = "{{documentation subpage}}"

# The namespace to retrieve pages from
# https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces to see available namespaces
NAMESPACE = 10
# Number of pages to extract at a time; used in get_params() in params for "aplimit"
PAGES_LIMIT = 5


# Text file bot will read and write last page title
REV_PAGE = "Powerpedia:add_template_documentation_sub_REV"

#Development enviroment toggle.  Should only be set to true on development machines.
DEVELOPMENT_ENV = True


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def should_verify() -> bool:
    """
    This function acts as an easy way to toggle the verify boolean when using
    requests.get() By default, requests really doesn't like invalid SSL certs.
    But in a development enviroment certs will be invalid.  Thus the need for
    this function. When changing over to QA/Production make sure the associated
    flag (DEVELOPMENT_ENV) is set accordingly.
    """
    return not DEVELOPMENT_ENV

def get_api_url() -> str:
    """
    Retrieves the API URL of the wiki

    :return: String of the path to the API URL of the wiki
    """

    site = pywikibot.Site()
    url = site.protocol() + "://" + site.hostname() + site.apipath()
    return url


def get_params(continue_from="") -> {}:
    """
    Gets the parameters dictionary to make the GET request to the wiki

    :param continue_from: String of page title to continue from; defaults to beginning of wiki
    :return: a dictionary of the parameters
    """

    return {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apcontinue": continue_from,
        "apnamespace": NAMESPACE,
        "aplimit": PAGES_LIMIT
    }


def modify_pages(url: str, last_title: str) -> None:
    """
    Retrieves a Page Generator with all old pages to be tagged

    :param url: String of the path to the API URL of the wiki
    :param last_title: String of the last title scanned
    :return: None
    """

    # Retrieving the JSON and extracting page titles
    session = requests.Session()
    request = session.get(url=url, params=get_params(last_title), verify=should_verify())
    pages_json = request.json()
    pages = pages_json["query"]["allpages"]
    print("Pages to be scanned:", pages)

    # Adds template to the page if needed
    last_title = ""
    for page in pages:
        # Detects if title is already a /doc
        curr_title = page["title"]
        if re.search('/doc$', curr_title):
            print(curr_title, "is a doc subpage. Skipping...")
        else:
            curr_title = page["title"] + "/doc"
            last_title = curr_title
            add_template(curr_title)


    if "continue" in pages_json:
        continue_from_title = last_title
        print("\nContinuing from:", continue_from_title, "next run.")
    else:
        continue_from_title = ""

    update_last_page(continue_from_title)


def has_template(page_text: str) -> bool:
    """
    Checks if the parameter page text has a deconstructed version of TEMPLATE in it

    :param page_text: page text to be searched
    :return: True if 'pattern' is in the text; False if otherwise
    """

    pattern = '{{documentation subpage}}'
    return bool (re.search(pattern, page_text, re.DOTALL | re.IGNORECASE))

def test_redirects() -> bool:
    """
    Runs the function has_redirect through several tests based on the specification from:
    https://www.mediawiki.org/wiki/Help:Redirects
    Ensures redirects are being caught properly
    """

    #The word "redirect" is not case-sensitive, but there must be no space before the "#" symbol.
    valid_redirects = {'#REDIRECT[[Help:Magic_words#Page_names]]',
                       '#redirect [[Help:Magic_words#URL_encoded_page_names]]',
                       '#Redirect [[Manual:$wgConf]]',
                       '#REDIRECT [[MediaWiki/fr]]'}

    invalid_redirects = {'#REDIRECT [[{{ll|Help:Magic_words#Page_names}}]]'}

    is_valid = True

    for test_case in valid_redirects:
        is_valid &=  has_redirect(test_case)
        if not is_valid:
            print("has_redirect failed on test: " + test_case)

    for test_case in invalid_redirects:
        is_valid  &= not has_redirect(test_case)
        if not is_valid:
            print("has_redirect failed on test: " + test_case)

    return is_valid

def has_redirect(page_text: str) -> bool:
    """
    Checks f the parameter page text has the pattern "#REDIRECT[[**]]"
    where ** cannot have {{}} strucutres in it

    :param page_text: page text to be searched
    :return: True if 'pattern' is in the text; False if otherwise
    """
    pattern = '#redirect'
    return_value = bool(re.search(pattern, page_text, re.DOTALL | re.IGNORECASE))

    #need to check against another regex...
    #looking for everything that doesnt look like this #redirect[[{{*}}]]
    return_value &= not re.search(r"#redirect[ ]*\[\[\{\{.*\}\}\]\]", page_text, re.IGNORECASE)
    return return_value

def add_template(title: str) -> None:
    """
    Checks if the parameter page title has TEMPLATE, adds it if it doesn't

    :param title: string of the page title to be checked and modified
    :return: None
    """

    site = pywikibot.Site()
    page = pywikibot.Page(site, title)
    page_text = page.text

    if has_redirect(page_text):
        print("page '%s' has redirect... Skipping", page)

    elif not has_template(page_text):
        print("'%s' not in '%s'... Adding" % (TEMPLATE, page))
        page_text = u'\n\n'.join((TEMPLATE, page_text))
        page.text = page_text
        page.save(u"Tagged with: " + TEMPLATE, botflag=True)
    else:
        print("'%s' already in '%s'... Skipping." % (TEMPLATE, page))


def get_revisions(page_title: str) -> list:
    """
    Gets the revision information from a page specifed by its page title.

    :param page_title: string of the page title to get the revisions of
    :return: list containing user, time, and title of last revision on
    this page.
    """

    session = requests.Session()
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "rvprop": "timestamp|user",
        "rvslots": "main",
        "formatversion": "2",
        "format": "json"
    }

    request = session.get(url=get_api_url(), params=params, verify=should_verify())
    data = request.json()

    #Need to make sure key values 'query' and 'pages' are in the data dict.
    if not ('query' in data and 'pages' in data['query']):
        print("No valid page found...")
        return ""

    page = data['query']['pages'][0]

    #Checking for 'missing' or no 'revisions' if so that means nothing of value
    #is page and should just return ""
    if 'missing' in page or not 'revisions' in page:
        print("No revision information found for page " + page_title + "\n")
        return ""
    rev_info = page['revisions'][0]

    return {"user": rev_info['user'],
            "time": rev_info['timestamp'],
            "title": page_title}


def check_last_page() -> str:
    """
    Checks to see if REV_PAGE has any useful last page to start the script from
    If it does return that page as the last_page, and if not return an empty string.
    Need to query the wiki for page rev information.
    Using this: https://www.mediawiki.org/wiki/API:Revisions

    :param: none
    :return: page last modified. Stored at REV_PAGE on wiki.  returns empty string if
    no information is available at that page.
    """

    page = pywikibot.Page(pywikibot.Site(), title=REV_PAGE)

    #Check to make sure the revision page exists.  If it doesn't create a new empty page and return
    #an empty string.
    if not page.exists():
        print("Revision page \""+ REV_PAGE +"\" not found...  Adding")
        page.text = ""
        page.save()
        return ""

    if not page.get():
        print("No valid revision on this page found\n")
        return ""


    #Need to replace ' with " so json.loads() can properly change it from a string to a dict.
    page_text = page.get().replace('\'', '\"')
    page_contents = json.loads(page_text)

    if page_contents['title']:
        return page_contents['title']

    print("No valid revision page found\n")
    return ""


def update_last_page(current_page: str) -> None:
    """
    Sets the page text of REV_PAGE to the latest revision information from current_page

    :param: current_page title of page to set revision information of
    :return: none
    """
    rev = get_revisions(current_page)
    page = pywikibot.Page(pywikibot.Site(), title=REV_PAGE)
    page.text = rev
    page.save()



def main() -> None:
    """
    Driver. Iterates through the wiki and adds TEMPLATE where needed.
    """
    # Retrieving the wiki URL
    url = get_api_url()
    if not should_verify():
        print(test_redirects())
        print(url)



    last_title = check_last_page()

    if last_title:
        print("last page found")
    else:
        print("No last page found")

    modify_pages(url, last_title)


    print("\nNo pages left to be tagged")


if __name__ == '__main__':
    main()
