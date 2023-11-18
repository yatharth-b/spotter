import pickle

# Load the dictionary back from the pickle file.

with open("recommendation_links_dictionary.pickle", 'rb') as file:
    scraped = pickle.load(file)
    print(len([i for i in scraped if scraped[i][0] != []]))