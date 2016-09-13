#! /usr/bin/env python3

"""
Perform word-counts on columns of a CSV file.

Created by:     Gonzalo Rolón Morinelli
Last update by: Gonzalo Rolón Morinelli
Creation date:  2016-09-12
Last update:    2016-09-12
"""

import csv
import os
import sys
import traceback


# Globals.

replaceable_chars = {"a": ["á", "ä", "à"],
                     "e": ["é", "ë", "è"],
                     "i": ["í", "ï", "ì"],
                     "o": ["ó", "ö", "ò"],
                     "u": ["ú", "ü", "ù"],
                     "n": ["ñ"]}

OUTPUT_FORMAT = "{}. {}:\t{}\n"

# Core functions.


def read_csv_and_count(t_file, t_cols, tidy_func = {}, replace_dict = {}):
    """
    Read a CSV file and perform word-count on target columns.

    :param t_file:          A CSV file.
    :param t_cols:          A list of indexes of target columns.
    :param tidy_func:       A function to tidy strings.
    :param replace_dict:    A dict with replacements as keys and a list of
                            replaceables for that replacement.
    :return:                A dict containing the results.
    """
    reader = csv.reader(t_file)
    reader.__next__()
    result = {t_col: {} for t_col in t_cols}
    for row in reader:
        for t_col in t_cols:
            add_answer_to_result(result, row, t_col, tidy_func,
                                 replace_dict)
    return result


def add_answer_to_result(result, row, t_col, tidy_func, replace_dict):
    """
    Add answers to the result dict.

    :param result:          A result dict used to store count of answers for
                            target columns.
    :param row:             The current row.
    :param t_col:           The column being analyzed.
    :param tidy_func:       A function to tidy strings.
    :param replace_dict:    A dict with replacements as keys and a list of
                            replaceables for that replacement.
    :return:                None. Modifies result.
    """
    for answer in row[t_col].split(","):
        answer = tidy_func(answer, replace_dict)
        result[t_col][answer] = result[t_col].setdefault(answer, 0) + 1


# Tidy functions.
# TODO: Come up with more tidy functions!

def tidy_string_def(some_string, replace_dict):
    """
    Tidy a string by removing trailing and starting whitespace, enforce
    lowercase and replace chars as defined in REPLACEABLE_CHARS.

    :param some_string:     A string to be tidied
    :param replace_dict:    A dict with replacements as keys and a list of
                            replaceables for that replacement.
    :return:                A tidied string
    """
    some_string = some_string.lower()
    for replacement in replace_dict:
        for replaceable in replace_dict[replacement]:
            some_string = some_string.replace(replaceable, replacement)
    return some_string.strip()


# Create result output.

def sort_and_save_dict(result, out_path):
    """
    Sorts and saves to a txt file a dict of dicts with sortable values.

    :param result:      A result dict used to store count of answers for
                        target columns.
    :param out_path:    The path to the output file.
    :return:            None
    """
    buffer = ""
    for field in result:
        f_dict = result[field]
        buffer += "Results for: {}\n".format(field)
        buffer += "\n"
        buffer += "Alphabetical sorting:\n"
        buffer += "\n"
        for idx, tuple_key in enumerate(sorted(f_dict.items())):
            buffer += OUTPUT_FORMAT.format(idx, tuple_key[0], tuple_key[1])
        buffer += "\n"
        # Ranked
        buffer += "Ranked sorting:\n"
        buffer += "\n"
        sort_val = lambda x: x[1]
        for idx, tuple_key in enumerate(sorted(f_dict.items(), key=sort_val,
                                               reverse=True)):
            buffer += OUTPUT_FORMAT.format(idx, tuple_key[0], tuple_key[1])
        buffer += "\n"
        buffer += "-" * 80
        buffer += "\n"
    with open(out_path, "w") as out_file:
        out_file.write(str(buffer))


# CLI-mode.

if __name__ == "__main__":

    # Core functions of CLI-mode

    def input_target_columns(t_path):
        """Interactive input mode for target columns."""
        print("[+} No target columns provided. Please, choose from the "
              "following list:")
        with open(t_path, encoding="utf-8") as t_file:
            reader = csv.reader(t_file)
            headers = reader.__next__()
            for (idx, header) in enumerate(headers):
                print(str(idx) + ".", header)
        print()
        t_cols = set()
        cols_input = input(
                "Enter comma-separated list of target columns (empty = all "
                "columns): ")
        if cols_input:
            try:
                t_cols = {int(t_col) for t_col in cols_input.split(",")}
            except ValueError as err:
                error_parsing_t_cols(err)
        return t_cols


    # Helpers for CLI-mode

    def print_usage():
        """Print the usage of the tool."""
        print()
        print("usage:   wordcount_csv.py path/to/file.csv [0-indexed "
              "comma-separated list of target column indexes] ["
              "comma-separated list of case-insensitive strings to be omitted "
              "from answers]")


    def error_parsing_t_cols(err):
        """Print the error for parsing target columns along with usage."""
        print("[-] Target columns couldn't be parsed: ", err)
        print_usage()
        sys.exit()


    # The actual script.
    # TODO: Add argv select tidy function to be applied.

    # Unpack target path from argv.
    try:
        t_path = sys.argv[1]
        t_ext = os.path.splitext(t_path)[-1].lower()
        if not os.path.isfile(t_path) and t_ext != ".csv":
            print("[-] Input path isn't a valid CSV file.")
            print_usage()
            sys.exit()
    except IndexError:
        print_usage()
        sys.exit()

    # Unpack target columns from argv or enter interactive mode to select.
    try:
        t_cols = [int(t_col) for t_col in sys.argv[2].split(",")]
    except IndexError:
        t_cols = input_target_columns(t_path)
    except ValueError as err:
        error_parsing_t_cols(err)

    # Unpack omit strings from argv.
    try:
        replaceable_chars[""] = [string.lower() for string in sys.argv[3].split(
                                ",")]
    except IndexError:
        pass

    # Call the core functions.
    result = {}
    try:
        with open(t_path, encoding="UTF-8") as t_file:
            result = read_csv_and_count(t_file, t_cols, tidy_string_def,
                                        replaceable_chars)
    except Exception as err:
        print("[-] There was an error while analyzing:", err)
        traceback.print_exc(flush=True)
    sort_and_save_dict(result, "wordcount_result.txt")






