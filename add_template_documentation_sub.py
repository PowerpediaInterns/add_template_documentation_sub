import pywikibot
import requests
import re
import urllib3

# Template to append to pages
TEMPLATE = "{{documentation subpage}}"

# The namespace to retrieve pages from
# https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces to see available namespaces
NAMESPACE = 10
# Number of pages to extract at a time; used in get_params() in params for "aplimit"
PAGES_LIMIT = 5
# Text file bot will read and write last page title
TEXT_FILE = "docBotSub_last_page.txt"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
	request = session.get(url=url, params=get_params(last_title), verify=False)
	pages_json = request.json()
	pages = pages_json["query"]["allpages"]
	print("Pages to be scanned:", pages)

	# Adds template to the page if needed
	for page in pages:
		# Detects if title is already a /doc
		curr_title = page["title"]
		if re.search('/doc$', curr_title):
			print(curr_title, "is a doc subpage. Skipping...")
		else:
			curr_title = page["title"] + "/doc"
			add_template(curr_title)

	if "continue" in pages_json:
		continue_from_title = pages_json["continue"]["apcontinue"]
		print("\nContinuing from:", continue_from_title, "next run.")
	else:
		continue_from_title = ""

	with open(TEXT_FILE, "w+") as f:
		f.write(continue_from_title)
		print("Wrote", continue_from_title, "in", TEXT_FILE)


def has_template(page_text: str) -> bool:
	"""
	Checks if the parameter page text has a deconstructed version of TEMPLATE in it

	:param page_text: page text to be searched
	:return: True if 'pattern' is in the text; False if otherwise
	"""

	pattern = '{{documentation subpage}}'
	if re.search(pattern, page_text, re.DOTALL | re.IGNORECASE):
		return True
	else:
		return False


def add_template(title: str) -> None:
	"""
	Checks if the parameter page title has TEMPLATE, adds it if it doesn't

	:param title: string of the page title to be checked and modified
	:return: None
	"""

	site = pywikibot.Site()
	page = pywikibot.Page(site, title)
	page_text = page.text

	if not(has_template(page_text)):
		print("'%s' not in '%s'... Adding" % (TEMPLATE, page))
		page_text = u'\n\n'.join((TEMPLATE, page_text))
		page.text = page_text
		page.save(u"Tagged with: " + TEMPLATE, botflag=True)
	else:
		print("'%s' already in '%s'... Skipping." % (TEMPLATE, page))


def main() -> None:
	"""
	Driver. Iterates through the wiki and adds TEMPLATE where needed.
	"""

	# Retrieving the wiki URL
	url = get_api_url()
	print(url)

	# Creates file if it does not exist
	open(TEXT_FILE, "a")

	with open(TEXT_FILE, "r") as f:
		last_title = f.readline().strip()
		print("Starting from:", last_title)

	modify_pages(url, last_title)

	print("\nNo pages left to be tagged")


if __name__ == '__main__':
	main()
