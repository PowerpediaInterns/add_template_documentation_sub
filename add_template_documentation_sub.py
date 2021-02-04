import pywikibot
import requests
import re
import urllib3

# Template to append to pages
TEMPLATE = "{{documentation subpage}}"
# Used to prevent a lot of empty space when printing to the console
TEMPLATE_NO_NEWLINE = TEMPLATE.replace("\n", "")

# The namespace to retrieve pages from
# https://www.mediawiki.org/wiki/Manual:Namespace#Built-in_namespaces to see available namespaces
NAMESPACE = 10
# Number of pages to extract at a time; used in get_params() in params for "aplimit"
PAGES_LIMIT = 3

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


def modify_pages(url: str) -> None:
	"""
	Retrieves a Page Generator with all old pages to be tagged

	:param url: String of the path to the API URL of the wiki
	:return: None
	"""

	# Retrieving the JSON and extracting page titles
	session = requests.Session()
	request = session.get(url=url, params=get_params(), verify=False)
	pages_json = request.json()
	pages = pages_json["query"]["allpages"]
	print("Pages to be scanned:", pages)

	# Adds template to the page if needed
	for page in pages:
		curr_title = page["title"] + "/doc"
		add_template(curr_title)

	if "continue" in pages_json:
		continue_from = pages_json["continue"]["apcontinue"]
		print("\nContinuing from:", continue_from)
	else:
		continue_from = ""

	# Continue iterating through wiki
	while continue_from:
		# Retrieving the JSON and extracting page titles
		request = session.get(url=url, params=get_params(continue_from), verify=False)
		pages_json = request.json()
		pages = pages_json["query"]["allpages"]
		print("Pages to be scanned:", pages)

		# Adds template to the page if needed
		for page in pages:
			curr_title = page["title"] + "/doc"
			add_template(curr_title)

		# Extracting title to continue iterating from
		if "continue" in pages_json:
			continue_from = pages_json["continue"]["apcontinue"]
			print("\nContinuing from:", continue_from)
		else:
			continue_from = ""


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
		print("'%s' not in '%s'... Adding" % (TEMPLATE_NO_NEWLINE, page))
		# page_text = u''.join((page_text, TEMPLATE))
		# page.text = page_text
		# page.save(u"Tagged with: " + TEMPLATE_NO_NEWLINE, botflag=True)
	else:
		print("'%s' already in '%s'... Skipping." % (TEMPLATE_NO_NEWLINE, page))


def main() -> None:
	"""
	Driver. Iterates through the wiki and adds TEMPLATE where needed.
	"""

	# Retrieving the wiki URL
	url = get_api_url()
	print(url)

	modify_pages(url)

	print("\nNo pages left to be tagged")


if __name__ == '__main__':
	main()
