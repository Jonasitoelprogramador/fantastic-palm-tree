import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re

from objects import Paragraph

# Define the URL for the Wikimedia REST API for the 'Caramel' page
api_url = "https://es.wikipedia.org/api/rest_v1/page/html/caramelo"

# Initialize variables
request_count = 0
total_characters = 0
para_objects = []

import re
from bs4 import NavigableString, Tag

import re
from bs4 import NavigableString, Tag

# Create a regex pattern that excludes these words
# The pattern checks for words that are not in the excluded list and are followed by !, ?, or .
one_char_check = r"(?<!\b[a-z]{1})[!?.]"

# This receives a paragraph element
def convert_to_paragraph_dict(p):
    paragraph = {}
    count = 1

     # Converts the remaing tags to text
    def extract_text_from_elements(elements):
        return ''.join(element.get_text() if isinstance(element, Tag) else str(element) for element in elements)

    # overall, this returns a dictionary where each entry represents a sentence.  Each sentence contains both NavStrings and Tags
    # loop through the children of the para element
    for content in p.contents:
        # if the child is a string and it contails punctuation 
        if isinstance(content, NavigableString):
            previous_index = 0  # Reset for each new NavigableString
            matches = re.finditer(one_char_check, str(content))
            found_punctuation = False

            # iterate through the punctuation matches
            for match in matches:
                found_punctuation = True
                # start a new sentence for each new match
                if count not in paragraph:
                    paragraph[count] = []

                # get the string pertaining to the current match
                individual_sentence = content[previous_index:match.start() + 1]
                # add this to the dictionary
                paragraph[count].append(individual_sentence)
                count += 1
                previous_index = match.start() + 1

            # Handle the remaining part of the string
            # If there is no punctuation, the entire child is added
            if not found_punctuation:
                if count not in paragraph:
                    paragraph[count] = []
                paragraph[count].append(content)
            # if there is still text left after removing all sentences...
            elif previous_index < len(content):
                if count not in paragraph:
                    paragraph[count] = []
                # ...add the remaining bit to the dictionary
                paragraph[count].append(content[previous_index:])

        elif isinstance(content, Tag):
            # Append tags to the current sentence
            if count not in paragraph:
                paragraph[count] = []
            paragraph[count].append(content)

    
    # This removes any entries from the dict if the sentences has a <a></a> tag
    for key in list(paragraph.keys()):
        for element in paragraph[key]:
            if isinstance(element, Tag) and (element.name == 'a' or element.find('a') is not None):
                del paragraph[key]
                break
    
    # if paragraph is empty, return None
    if not paragraph:
        return None

    # Process the dictionary to extract text
    for key in paragraph:
        paragraph[key] = extract_text_from_elements(paragraph[key])
    
    # remove setences that are too short to be useful
    for key in list(paragraph.keys()):
        if len(paragraph[key]) < 5:
            del paragraph[key]
    
    # remove whitespace
    for key in list(paragraph.keys()):
        paragraph[key] = paragraph[key].strip()

    for key in list(paragraph.keys()):
        if paragraph[key][-1:] not in ['.', '!', '?']:
            del paragraph[key]

    return paragraph

#while total_characters < 50000:
    # Send a GET request to the API
response = requests.get(api_url)
request_count += 1

if response.status_code == 200:
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        processed_text = convert_to_paragraph_dict(p)
        if processed_text:
            para_object = Paragraph(processed_text, 'por', 'para')
            para_objects.append(para_object)
            total_characters += para_object.calculate_characters()
                
#if total_characters >= 50000:
print(f'this is number of requests {request_count}')
print(f'this is number of characters {total_characters}')
# Join all sentences to form the full text

for o in para_objects:
    o.por_search()
    o.para_search()
    if o.por_sentences:
        print(o.por_sentences)
    if o.para_sentences:
        print(o.para_sentences)


'''else:
    print(f"Error: Unable to fetch data. Status code: {response.status_code}")'''

