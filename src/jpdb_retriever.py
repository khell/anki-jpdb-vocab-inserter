from dataclasses import dataclass
from bs4 import BeautifulSoup, ResultSet, Tag
import requests

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0"
    }
)


@dataclass
class Vocab:
    front: str
    back: str
    meaning: str
    reading: str
    example_sentence: str
    vocabulary: str

    @staticmethod
    def get(vocab_str: str, jpdb_sid: str = None) -> "Vocab":
        if jpdb_sid:
            session.cookies.update({"sid": jpdb_sid})

        # Get the vocab info from JPDB
        url = f"https://jpdb.io/search?q={vocab_str}&lang=english#a"
        response = session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Check how many results we have
        results = soup.select("div.results > div")
        print(
            f"[{vocab_str}]: {len(results)} results found, only the top result will be used."
        )

        # Get the first result
        result = results[0]
        return Vocab(
            front=vocab_str,
            back=vocab_str,
            meaning=retrieve_vocab_info_meaning(
                result.select_one("div.subsection-meanings > div.subsection")
            ),
            reading=retrieve_vocab_info_reading(
                result.select("div.primary-spelling > div.spelling ruby.v")
            ),
            example_sentence=retrieve_vocab_info_example_sentence(result, vocab_str),
            vocabulary=vocab_str,
        )


def retrieve_vocab_info_meaning(result: Tag) -> str:
    output = "<div>"
    children = result.children
    for child in children:
        if "part-of-speech" in child.attrs["class"]:
            output += f'<div style="color: #888; font-size: 85%; font-weight: bold">{retrieve_vocab_info_meaning_speech_section(child)}</div>'
        elif "description" in child.attrs["class"]:
            output += retrieve_vocab_info_meaning_meaning_section(child)

    return output + "</div>"


def retrieve_vocab_info_meaning_speech_section(result: Tag) -> str:
    speech_set = result.select("div")
    return ", ".join([speech_result.text for speech_result in speech_set])


def retrieve_vocab_info_meaning_meaning_section(result: Tag) -> str:
    meanings = '<div style="padding-left: 0.5rem">'
    meaning = ""
    for idx, meaning_result_child in enumerate(result.contents):
        if idx > 0:
            meaning += '<br/>&nbsp;&nbsp;&nbsp;&nbsp;<i style="opacity: 0.5; margin-left: 2rem">'  # deliberate indent here to match formatting

        meaning_text = ""
        if isinstance(meaning_result_child, Tag):
            meaning_text = meaning_result_child.text
        else:
            meaning_text += str(meaning_result_child)
        meaning += meaning_text

        if idx > 0:
            meaning += "</i>"
    meanings += meaning + "</div>"
    return meanings


def retrieve_vocab_info_reading(result_set: ResultSet[Tag]) -> str:
    return str(result_set[0])


def retrieve_vocab_info_example_sentence(result: Tag, vocab_str: str) -> str:
    results = result.select("div.subsection-examples div.used-in div.jp")
    if not results:
        print(f"[{vocab_str}]: No example sentences found, trying to find alternative.")
        more_details_present = result.select_one("a.view-conjugations-link")
        if more_details_present:
            # Load the actual page
            more_details_url = f"https://jpdb.io{more_details_present['href']}"
            response = session.get(more_details_url)
            result = BeautifulSoup(response.content, "html.parser")
            results = result.select("div.subsection-examples div.used-in div.jp")
        else:
            print(f"[{vocab_str}]: No example sentences found.")
            return ""

    examples = []
    for example_result in results:
        examples.append("".join([str(child) for child in example_result.children]))

    example_str = "<ul>"
    for example in examples:
        example_str += f"<li>{example}</li>"
    example_str += "</ul>"
    return example_str
