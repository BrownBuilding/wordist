#!/bin/python3

from sys import argv
from sys import stderr


class Store:
    def __init__(self):
        self.data = {}

    def add_to_relation(self, word1: str, word2: str, summand: float) -> None:
        word_tuple = tuple(sorted((word1, word2)))
        self.data[word_tuple] = self.data.get(word_tuple, 0) + summand

    def relations(self, word: str):
        for word_tuple, relation_value in self.data.items():
            other_word = None
            if word_tuple[0] == word:
                other_word = word_tuple[1]
            elif word_tuple[1] == word:
                other_word = word_tuple[0]
            else:
                continue
            yield (other_word, relation_value)

    def relation(word1: str, word2: str) -> float:
        return self.data.get(tuple(sorted((word1, word2))), 0.0)

    def words(self) -> set:
        print("doing words", file=stderr)
        words = set()
        for word_tuple in self.data.keys():
            word1, word2 = word_tuple
            words.add(word1)
            words.add(word2)
        print("doing words", file=stderr)
        return words


def calculate_relation(distance: int) -> float:
    return abs(1.0 / float(distance))


def split_words(text: str):
    for word in text.split():
        yield ''.join(c.lower() for c in word if c.isalnum())


def analyze(store: Store, text: str, limit: int=100, stop_words: set=set()):
    # Simple past of 'split' is 'split' so 'splited' it is.
    splited_words = list(split_words(text))
    for i in range(0, len(splited_words)):
        word1 = splited_words[i]
        if word1 in stop_words:
            continue
        for j in range(i + 1, min(i + limit, len(splited_words))):
            word2 = splited_words[j]
            if word2 in stop_words:
                continue
            store.add_to_relation(word1, word2, calculate_relation(i - j))


def parse_args(argv: list) -> tuple:
    it = iter(argv)
    correct_argc = len(argv) <= 3
    bin = next(it)
    file_name = next(it, None)
    stop_word_list_file = next(it, None)
    return (correct_argc, bin, file_name, stop_word_list_file)


def print_as_json(store: Store) -> None:
    def detect_last(iterable):
        it = iter(iterable)
        prev = next(it)
        for e in it:
            yield (False, prev)
            prev = e
        yield (True, prev)
    for is_last_word, word in detect_last(store.words()):
        print(f"\"{word}\": {{")
        relations_sorted = store.relations(word)
        for is_last, (k, v) in detect_last(relations_sorted):
            print(f"  \"{k}\": {v}{'' if is_last else ','}")
        print(f"}}{'' if is_last_word else ','}")


def print_usage(bin_name):
    print(f"USAGE: {bin_name} <file> [<stop-word-list-file>]", file=stderr)


def main():
    store = Store()

    correct_argc, bin_name, file_name, stop_word_list_file = parse_args(argv)

    if not correct_argc:
        print_usage(bin_name)
        print("too many arguments", file=stderr)
        return

    stopwords = None
    if stop_word_list_file is not None:
        with open(stop_word_list_file) as custom:
            stopwords = custom.read().splitlines()
            stopwords = set(stopwords)

    if not file_name:
        print_usage(bin_name)
        print("missing <file>", file=stderr)

    file_content = None
    try:
        with open(file_name) as file:
            file_content = file.read()
    except FileNotFoundError as e:
        print(f"\'{e.filename}\' not found", file=stderr)
        return

    stopwords = set()
    if stop_word_list_file:
        try:
            with open(stop_word_list_file) as file:
                stopwords = set(filter(lambda line: line.lower(), file.read().split_lines()))
        except FileNotFoundError as e:
            print(f"stop word list file \'{e.filename}\' not found", file=stderr)
            return

    analyze(store, file_content, limit=100, stop_words=stopwords)
    print_as_json(store)


if __name__ == '__main__':
    main()
