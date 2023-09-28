# import requests

# res = requests.get('http://localhost/api/facts/?skip=0&limit=100',
#                    headers={
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY0NDIxOTksInN1YiI6IjIifQ.P2vfWWD0u89kbK7DJ1Nh_xEe-sOQvT-vmAhckVH6Ohw",
#   "token_type": "bearer"
# })
# print(res)

curl -X 'POST' \
  'http://localhost/api/facts/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY0NDIzNDUsInN1YiI6IjIifQ.Dgp1d5KbOorCuiLV6VqbE-N9OdqXalo2U774g1SYFNw' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Chief harpooner of the Pequod, a cannibal companion of Ishmael in Melville's Moby Dick",
    "answer": "Queequeg",
    "deck": "Literature",
    "answer_lines": [
      "Queequeg",
      "{Queequeg}"
    ],
    "identifier": "this character",
    "category": "American",
    "extra": {
      "type": "quizbowl",
      "tournament": "MAGNI",
      "difficulty": "regular_college",
      "dataset": "quizdb.org",
      "proto_id": null,
      "qdb_id": 99512,
      "clue_type": "tokenized_clue",
      "sentence": 5,
      "wiki_page": "Queequeg"
    }
    }'