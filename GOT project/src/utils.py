def ner(file_name):
    '''
    Function to process the text from a text file (.txt) using Spacy

    Params:
    file_name -- name of the txt file

    Returs:
    A processed doc file using spacy english language model

    '''
    #Load spacy english model
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 2000000
    book_text = open(book).read()
    book_doc = nlp(book_text)

    return book_doc

def get_ne_list_per_sentence(spcay_doc):
    '''
    Get a list of entities per sentence of a spacy document and store in a dataframe

    Params:
    spacy_doc -- a Spacy processed document

    Returns:
    A dataframe containing sentences and corresponding list of recognised in the entites in the sentences
    '''

    sent_entity_df = []

    #Loop through sentences, stored named entety list for each sentence
    for sent in book_doc.sents:
        entity_list = [ent.text for ent in sent.ents]
        sent_entity_df.append({'sentence': sent, 'entities':entity_list})

    sent_entity_df = pd.DataFrame(sent_entity_df)

    return sent_entity_df

def filter_entity(ent_list, char_df):
    '''
    Function to filter out non-character entites.

    Params:
    ent-list -- list of entities to be filtered
    char_df -- dataframe containing characters names and first names 

    Returns:
    List of entities that are characters (mathing names or first names)
    '''

    filtered_entities = []

    for entity in ent_list:
        # Check if entity exactly matches any DataFrame value after removing parentheses
        if (char_df['character'] == entity).any() or \
           (char_df['char_firstname'] == entity).any():
            filtered_entities.append(entity)

    return filtered_entities if filtered_entities else []

def create_relatioship(df, window_size):
    '''
    Create a dataframe of relatioship

    Params:
    df -- dataframe containing a collumn called char_ent with the characthers for each sentence
    window_size -- size of windows (number of sentences) for creating relationship
    between two adjacent characther in the text

    Returns:
    DataFrame of all relationships containing 3 collumns: source, target and value
    '''
    
    relationship = []

    for i in range(df.index[-1]):
        end_i = min(i+window_size, df.index[-1])
        char_list = sum((df.loc[i:end_i].char_ent), [])

        # Remove duplicated char in the same sentence
        char_unique = [char_list[i] for i in range(len(char_list))
        if (i == 0 ) or char_list[i] != char_list[i-1]]

        if len(char_unique) > 1:
            for idx, a in enumerate(char_unique[:-1]):
                b = char_unique[idx+1]
                relationship.append({'source': a,'target': b})

    relationship_df = pd.DataFrame(relationship)
    # Sort the cases with a->b and b->a
    relationship_df = pd.DataFrame(np.sort(relationship_df.values, axis=1), columns= relationship_df.columns)

    relationship_df['value'] = 1
    relationship_df = relationship_df.groupby(['source','target'], sort= False, as_index=False).sum()


    return relationship_df

