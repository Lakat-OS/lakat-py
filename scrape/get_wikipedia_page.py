import requests

base_params = dict(action="query", format="json")

class WikipediaPage:

    def __init__(self, API_URL):
        self.API_URL = API_URL

    def get_page_content(self, title):
        """Fetch the main content of a Wikipedia page."""
        params = dict(
            **base_params, 
            titles=title,
            prop="revisions",
            rvprop="content")
        response = requests.get(self.API_URL, params=params)
        data = response.json()
        page_id = next(iter(data['query']['pages']))
        return data['query']['pages'][page_id]['revisions'][0]['*']

    def get_page_info(self, title):
        """Fetch metadata about a Wikipedia page."""
        params = dict(
            **base_params, 
            titles=title,
            prop= "info")
        response = requests.get(self.API_URL, params=params)
        return response.json()

    def get_page_links(self, title):
        """Fetch links from a Wikipedia page."""
        params = dict(
            **base_params, 
            titles= title,
            prop= "links")
        response = requests.get(self.API_URL, params=params)
        return response.json()

    def get_page_categories(self, title):
        """Fetch category information of a Wikipedia page."""
        params = dict(
            **base_params, 
            titles= title,
            prop="categories")
        response = requests.get(self.API_URL, params=params)
        return response.json()

    def get_page_images(self, title):
        """Fetch images used on a Wikipedia page."""
        params = dict(
            **base_params, 
            titles= title,
            prop="images")
        response = requests.get(self.API_URL, params=params)
        return response.json()

    def get_parsed_content(self, title):
        """Fetch the HTML content of a Wikipedia page."""
        params = dict(
            action= "parse",
            format= "json",
            page= title)
        response = requests.get(self.API_URL, params=params)
        return response.json()


    def get_page_links_paginated(self, title):
        """Fetch all links from a Wikipedia page with pagination handling."""
        links = []
        params = dict(
            **base_params, 
            titles= title,
            prop= "links",
            pllimit= "max"  # Request as many links as possible per query
        )

        while True:
            response = requests.get(self.API_URL, params=params)
            data = response.json()
            pages = data['query']['pages']
            page_id = next(iter(pages))
            page_links = pages[page_id].get('links', [])
            
            links.extend(page_links)

            if 'continue' not in data:
                break  # Break the loop if no more pages to fetch

            # Update the continue parameter for the next request
            params.update(data['continue'])

        return links

    def get_all_content_types(self, title, get_content=True, get_info=True, get_links=True, get_categories=True, get_images=True, get_parsed_content=False):
        """Aggregate all content types into a dictionary."""
        content_types = dict()
        if get_content:
            content_types["Content"] = self.get_page_content(title)
        if get_info:
            content_types["Info"] = self.get_page_info(title)
        # if get_links:
        #     content_types["Links"] = self.get_page_links(title)
        if get_links:
            content_types["Links"] = self.get_page_links_paginated(title)
        if get_categories:
            content_types["Categories"] = self.get_page_categories(title)
        if get_images:
            content_types["Images"] = self.get_page_images(title)
        if get_parsed_content:
            content_types["Parsed"] = get_parsed_content(title)
        return content_types

    def get_edit_history(self, title, limit=500, requests_limit=5):
        """Fetch the edit history of a Wikipedia page."""
        revisions = []
        params = dict(
            **base_params, 
            titles= title,
            prop="revisions",
            rvlimit= ("max" if not limit else limit),  # Maximum revisions per request
            rvprop= "ids|timestamp|user|comment|content")

        for i in range(requests_limit):
            
            response = requests.get(self.API_URL, params=params)
            data = response.json()
            pages = data['query']['pages']
            page_id = next(iter(pages))
            page_revisions = pages[page_id].get('revisions', [])
            
            revisions.extend(page_revisions)
            print('i', i, len(revisions))
            print('data', data.keys())
            if 'continue' not in data:
                break  # Break the loop if no more revisions to fetch

            # Update the continue parameter for the next request
            params.update(data['continue'])

        return revisions


# # Constants
# API_URL = "https://en.wikipedia.org/w/api.php"
# TITLE = "Compartmental models in epidemiology"

# # Fetching all content types
# all_contents = get_all_content_types(TITLE)

# # Example: Print the page content and page info
# print("Page Content:", all_contents["Content"][:500])  # Displaying first 500 characters for brevity
# print("Page Info:", all_contents["Info"])
