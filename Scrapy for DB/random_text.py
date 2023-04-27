import lorem



def generate_descrb():
    # Generate a Lorem Ipsum text
    text = lorem.text()

    # Split the text into words
    words = text.split()

    # Set the maximum number of words in the paragraph
    max_words = 50

    # Create a new paragraph with up to the maximum number of words
    paragraph = ' '.join(words[:max_words])

    # Add a prefix to the paragraph
    prefix = "Nice product with good reviews as "
    paragraph = prefix + paragraph

    # print(paragraph)
    return paragraph


