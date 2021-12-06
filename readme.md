# add_template_documentation_sub
Adds the {{documentation subpage}} tag to Template Subpages.

## Class variables for customization
### TEMPLATE
The template that will be used to tag pages (e.g. `{{documentation subpage}}`).

### NAMESPACE
The namespace that the program will extract pages from (e.g. 0 for (Main)).
https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces to see available namespaces.

### PAGES_LIMIT
The number of pages that will be extracted at a time. Used in get_params() in params for "aplimit".

### TEXT_FILE
The text file that the program reads and writes the last page title to continue from.

#Function Information
#### def should_verify() -> bool:
    

This function acts as an easy way to toggle the verify boolean when using
requests.get() By default, requests really doesn't like invalid SSL certs.
But in a development enviroment certs will be invalid.  Thus the need for
this function. When changing over to QA/Production make sure the associated
flag (DEVELOPMENT_ENV) is set accordingly.

#### def get_api_url() -> str:
    

Retrieves the API URL of the wiki

:return: String of the path to the API URL of the wiki

#### def get_params(continue_from="") -> {}:
    

Gets the parameters dictionary to make the GET request to the wiki

:param continue_from: String of page title to continue from; defaults to beginning of wiki
:return: a dictionary of the parameters

#### def modify_pages(url: str, last_title: str) -> None:
    

Retrieves a Page Generator with all old pages to be tagged

:param url: String of the path to the API URL of the wiki
:param last_title: String of the last title scanned
:return: None

#### def has_template(page_text: str) -> bool:
    

Checks if the parameter page text has a deconstructed version of TEMPLATE in it

:param page_text: page text to be searched
:return: True if 'pattern' is in the text; False if otherwise

#### def test_redirects() -> bool:
    

Runs the function has_redirect through several tests based on the specification from:
https://www.mediawiki.org/wiki/Help:Redirects
Ensures redirects are being caught properly

#### def has_redirect(page_text: str) -> bool:
    

Checks f the parameter page text has the pattern "#REDIRECT[[**]]"
where ** cannot have {{}} strucutres in it

:param page_text: page text to be searched
:return: True if 'pattern' is in the text; False if otherwise

#### def add_template(title: str) -> None:
    

Checks if the parameter page title has TEMPLATE, adds it if it doesn't

:param title: string of the page title to be checked and modified
:return: None

#### def get_revisions(page_title: str) -> list:
    

Gets the revision information from a page specifed by its page title.

:param page_title: string of the page title to get the revisions of
:return: list containing user, time, and title of last revision on
this page.

#### def check_last_page() -> str:
    

Checks to see if REV_PAGE has any useful last page to start the script from
If it does return that page as the last_page, and if not return an empty string.
Need to query the wiki for page rev information.
Using this: https://www.mediawiki.org/wiki/API:Revisions

:param: none
:return: page last modified. Stored at REV_PAGE on wiki.  returns empty string if
no information is available at that page.

#### def update_last_page(current_page: str) -> None:
    

Sets the page text of REV_PAGE to the latest revision information from current_page

:param: current_page title of page to set revision information of
:return: none

#### def main() -> None:
    

Driver. Iterates through the wiki and adds TEMPLATE where needed.

