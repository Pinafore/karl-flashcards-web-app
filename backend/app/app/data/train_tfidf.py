from sklearn.feature_extraction.text import TfidfVectorizer
import tqdm
import pickle
import json

def main():
  tfidf = TfidfVectorizer(ngram_range=(1, 5), analyzer='char')
  corpus = []
  with open('./formatted.train.clues.json') as in_file:
    questions = json.loads(in_file.read())
    for q in tqdm.tqdm(questions):
        corpus = corpus + q["answer_lines"]
  
  tfidf.fit(corpus)
  pickle.dump(tfidf, open("./tfidf.pkl", "wb"))

if __name__ == '__main__':
    main()
