from bs4 import BeautifulSoup
import requests
import json
import urllib.parse
import eventlet
from urllib.parse import urlparse
eventlet.monkey_patch()

def get_domain_from_url(url):
	parsed_uri = urlparse(url)
	result = '{uri.netloc}'.format(uri=parsed_uri)
	return result

def get_absolute_url(url, suburl):
	return urllib.parse.urljoin(url, suburl) 

def get_contents(url):
	try:	
		with eventlet.Timeout(3):
			try:
				html_doc = requests.get(url, timeout=1)
			except requests.exceptions.RequestException:
				return None
	except eventlet.Timeout:
		return None

	soup = BeautifulSoup(html_doc.content, 'html.parser')
	url_domain = get_domain_from_url(url)
	links = set()
	for link in soup.find_all('a'):
		suburl = link.get('href')
		suburl = get_absolute_url(url, suburl)
		suburl_domain = get_domain_from_url(suburl);
		if url_domain == suburl_domain:
			links.add(suburl)

	images = set()
	for img in soup.find_all('img'):
		images.add(img.get('src'))

	page = {
		"page_url": url,
		"links": list(links),
		"images": list(images)
	}
	print(url)
	return page

def depth_first_search_over_links(url, depth, max_depth, json_site_map, visited_links, ignored_urls):
	if (depth >= max_depth):
		return

	page = get_contents(url)
	if page is None:
		ignored_urls.add(url)
		return

	json_site_map.append(page)
	visited_links.add(url)
	for link in page['links']:
		if link not in visited_links:
			depth_first_search_over_links(link, depth+1, max_depth, json_site_map, visited_links, ignored_urls)


def build_site_map(starting_url, max_depth):
	json_site_map = []
	visited_links = set() # looking up n list takes a lot more time than set
	ignored_urls = set()
	initial_depth = 0

	print("Crawling URLs till max depth", max_depth)
	depth_first_search_over_links(starting_url, initial_depth, max_depth, json_site_map, visited_links, ignored_urls)
	print(json.dumps(json_site_map, indent=4))
	print("The following urls were not crawled further due to timeout/network issues. Please increase the timeout to crawl them.",json.dumps(list(ignored_urls), indent=4))
	return json_site_map

build_site_map('https://www.mozilla.org', 3);