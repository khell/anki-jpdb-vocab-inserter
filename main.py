from typing import List
from src.jpdb_retriever import Vocab
import argparse
import json
import requests


def get_vocab_for_import(file_path: str) -> List[str]:
    with open(file_path, "r") as file:
        # Skip blank lines
        lines = [line.strip() for line in file if line.strip()]
        return lines


def add_to_anki_connect(
    vocab: Vocab, deck_name: str, uri: str = "http://localhost:8765"
):
    print(f"[{vocab.vocabulary}] Adding to Anki deck '{deck_name}' using AnkiConnect.")
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Wanikani Vocab Style",
                "fields": {
                    "Front": vocab.front,
                    "Back": vocab.back,
                    "Meaning": vocab.meaning,
                    "Reading": vocab.reading,
                    "Example Sentence": vocab.example_sentence,
                    "Vocabulary": vocab.vocabulary,
                    "Extra": "",
                },
                "options": {"allowDuplicate": True, "duplicateScope": "deck"},
                "tags": ["automatically-added"],
            }
        },
    }
    response = requests.post(uri, data=json.dumps(payload))
    response_json = response.json()
    if response_json["error"]:
        print(f"[{vocab.vocabulary}] Error: {response_json['error']}")
    else:
        print(
            f"[{vocab.vocabulary}] Successfully added as note {response_json['result']}"
        )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("vocab_list", help="Path to the vocab list file.")
    argparser.add_argument(
        "deck_name", help="Name of the Anki deck to add the vocab to."
    )
    argparser.add_argument(
        "jpdb_sid",
        help="JPDB session ID. If not supplied, not all example sentences will be fetched.",
    )
    args = argparser.parse_args()

    vocab_list = get_vocab_for_import(args.vocab_list)
    for vocab_str in vocab_list:
        ret = Vocab.get(vocab_str, jpdb_sid=args.jpdb_sid)
        add_to_anki_connect(ret, args.deck_name)
