import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import pdb

# Define the URL for the Wikimedia REST API
api_url = "https://es.wikipedia.org/api/rest_v1/page/random/html/"

# Initialize variables
accumulated_text = ""
request_count = 0

# This receives a paragraph element
def process_paragraph(paragraph):
    sentences = {}
    count = 1
    pattern = '[!?.]'
    previous_index = 0

    # loop through the children of the para element
    for content in paragraph.contents:
        # if the current count value is not a key already, create a new key value pair
        if count not in sentences:
            sentences[count] = []

        # If the content is a NavString and its text ends with the given punctuation, start a new sentence
        if isinstance(content, NavigableString) and str(content).endswith(('!', '?', '.')):
            sentences[count].append(content)
            count += 1
        # If the content is a NavString and contains the given puntuation
        elif isinstance(content, NavigableString):
            matches =  re.finditer(pattern, str(content))
            for match in matches:
                individual_sentence = content[previous_index:match.start() + 1]
                sentences[count].append(individual_sentence)
                previous_index = match.start() + 1
                count += 1
    
    print(f'A paragraph: {sentences}')

    # this reuturns the same dictionary structure but just without the offending sentences
    for key in list(sentences.keys()):  # Use list() to create a copy of keys for safe iteration
        for element in sentences[key]:
            # Check if the element is a Tag and is an <a> tag
            if isinstance(element, Tag) and element.name == 'a':
                del sentences[key]  # Delete the entire entry
                break  # Exit the loop as we've already removed this entry

    text_sentences = {}

    # goes through all of the remaining setences in a partuclar paragrah
    for key in sentences:
        # Initialize an empty string for the current sentence
        sentence_text = ""

        # goes through each element of each sentence
        for element in sentences[key]:
            # Check if the element is NavigableString or Tag
            if isinstance(element, NavigableString):
                sentence_text += str(element)
            elif isinstance(element, Tag):
                sentence_text += element.get_text()

        # Store the concatenated text in the new dictionary
        if sentence_text != "":
            text_sentences[key] = sentence_text

    # text_sentences now contains each sentence as a string
    #print(text_sentences)

# Use a while loop to keep making requests until the accumulated text length is at least 1000 characters
while len(accumulated_text) < 50000:
    # Send a GET request to the API
    response = requests.get(api_url)
    request_count += 1

    # Check if the request was successful
    if response.status_code == 200:
        # Get the HTML content of the page
        html_content = response.content

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Process each paragraph
        paragraphs = soup.find_all('p')
        list_of_dicts = []
        #processed_text = process_paragraph(paragraphs[0])
        for p in paragraphs:
            processed_text = process_paragraph(p)
            list_of_dicts.append(processed_text)
            '''accumulated_text += processed_text + " "'''
        
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        break

# Once the desired length is reached
if len(accumulated_text) >= 50000:
    # Count the occurrences of 'por' as a separate word
    por_count = len(re.findall(r'\bpor\b', accumulated_text, re.IGNORECASE))

    # Save the text to a file
    with open('wikimedia_text.txt', 'w', encoding='utf-8') as file:
        file.write(accumulated_text)

    print(f"Text saved after {request_count} requests.")
    print(f"The word 'por' occurs {por_count} times in the text.")
else:
    print("Unable to retrieve sufficient text.")
