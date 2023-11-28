import re
from functools import partial

class Paragraph:
    def __init__(self, paragraph, *args):
        self.sentences = paragraph
        for a in args:
            setattr(self, f'{a}_sentences', {})
            method = self.create_dynamic_method(a)
            bound_method = partial(method, self)
            setattr(self, f'{a}_search', bound_method)  
    
    def create_dynamic_method(self, search_term):  
        # Define the body of the new method
        def dynamic_method(self):
            sentences = {}
            for key, value in self.sentences.items():
                if re.search(rf'\b{search_term}\b', value, re.IGNORECASE):
                    sentences[key] = value
            setattr(self, f'{search_term}_sentences', sentences)
        return dynamic_method
    
    def calculate_characters(self):
        total_characters = sum(len(value) for value in self.sentences.values())
        return total_characters

    

    '''def por_search(self):
        por_sentences = {}
        for key, value in self.sentences.items():
            if re.search(r'\bpor\b', value, re.IGNORECASE):
                por_sentences[key] = value
        self.por_sentences = por_sentences'''