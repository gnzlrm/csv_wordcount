#! /usr/bin/env python3

"""
Perform word-counts on columns of a CSV file.

Created by:     Gonzalo Rolón Morinelli
Last update by: Gonzalo Rolón Morinelli
Creation date:  2016-09-12
Last update:    2016-09-21
"""

import csv
import re
from unidecode import unidecode


# Tidy functions.

def tidy_strings(string_list):
    """
    Tidy a list of strings by removing trailing and starting whitespace, enforce
    lowercase and replace characters.

    :param string_list:     A string to be tidied
    :param repl_dict:       A dict with replacements as keys and a list of
                            replaceables for that replacement as values.
    :return:                A tidied string
    """
    res = []
    for string in string_list:
        string = unidecode(string.lower())
        res.append(string.strip())
    return res


# Core functions.

def csv_wordcount(file, cols, tidy_func=tidy_strings):
    """
    Read a CSV file and perform word-count on target columns.

    :param file:            A CSV file.
    :param cols:            A list of indexes of target columns.
    :param tidy_func:       A function to tidy a list of strings.
    :param del_exp:         A string with delimiter characters to split
    answers.
    :return:                A dict containing the results.
    """

    def add_answers():
        """Add the answers to the result."""
        for answ in set(tidy_func(
                        filter(None, re.split("[\W]+", row[target[0]])))):
            result[target][answ] = result[target].setdefault(answ, 0) + 1

    reader = csv.reader(file)
    headers = reader.__next__()
    headers = [headers[col] for col in cols]
    result = {(col, header): {} for col, header in zip(cols, headers)}
    for row in reader:
        for target in result:
            add_answers()
    return result


# Create result output.

def sort_and_write_result(result, file, out_format, sort_func=lambda x: x[1],
                          desc=True):
    """
    Sorts and saves to a txt file a dict of dicts with sortable values.

    :param result:      A result dict used to store count of answers for
                        target columns.
    :param file:    The output file.
    :param out_format:  A string modeling the output format for result rows
                        that contains three placeholders for idx, word and
                        count.
    :param sort_func:   A function to perform sorting. Defaults to sorting by
                        frequency.
    :param desc         Boolean for sorting in descending order.
    :return:            None
    """
    buffer = "\n" + "-" * 80 + "\n\n"
    for field in result:
        f_dict = result[field]
        buffer += "Results for: {}\n\n".format(field[1])
        for idx, tuple_key in enumerate(sorted(f_dict.items(), key=sort_func,
                                               reverse=desc)):
            buffer += out_format.format(idx + 1, tuple_key[1], tuple_key[0])
        buffer += "\n" + "-" * 80 + "\n\n"
    file.write(buffer)


# CLI-mode.

if __name__ == "__main__":

    import argparse
    import os
    import sys
    import traceback

    IN_FILE = 'file'
    OUT_FILE = 'out'
    COLS = 'cols'

    DES_PARSER = "Count words on the columns of a CSV file."
    DES_COLS = "list of target columns indexes"
    DES_OUT = "Path to output file (created if it doesn't exists)"

    OUT_FORMAT = "{}. {} times: {}\n"

    # Core functions of CLI-mode

    def close_file_and_exit():
        """Pretty self explanatory."""
        args[IN_FILE].close()
        sys.exit()


    def input_target_columns(args):
        """Interactive input mode for target columns."""
        print("No target columns provided. Please, choose from the "
              "following list:")
        reader = csv.reader(args[IN_FILE])
        headers = reader.__next__()

        for (idx, header) in enumerate(headers):
            print("\t" + str(1 + idx) + ".", header)
        cols_input = input(
            "Enter a list of target columns indexes (empty = all "
            "columns): ")
        if cols_input:
            try:
                cols = [int(t_col) - 1 for t_col in cols_input.split(" ")]
                for col in cols:
                    if col not in range(len(headers)):
                        print("error: Invalid column index provided: ", col)
                        close_file_and_exit()
                args[COLS] = cols
            except ValueError as err:
                print("error: Columns indexes couldn't be parsed: ", err)
                close_file_and_exit()
        else:
            args[COLS] = range(len(headers))

    # Args registration and validation.

    parser = argparse.ArgumentParser(description=DES_PARSER)
    parser.add_argument("--cols", nargs="*", dest=COLS,
                        type=int, metavar="N", help=DES_COLS)
    parser.add_argument(IN_FILE, metavar="path/to/file.csv",
                        type=argparse.FileType('r', encoding="utf-8"))
    parser.add_argument("--out", metavar="path/to/output", help=DES_OUT,
                        type=argparse.FileType('w+', encoding="utf-8"),
                        default=sys.stdout, dest=OUT_FILE)
    args = vars(parser.parse_args())

    if os.path.splitext(args[IN_FILE].name)[-1] != ".csv":
        print("error: Input file isn't a valid CSV file.")
        parser.print_help()
        close_file_and_exit()
    if not args[COLS]:
        input_target_columns(args)

    # Call to core functions.

    wordcount_dict = {}
    try:
        wordcount_dict = csv_wordcount(args[IN_FILE], args[COLS], tidy_strings)
    except Exception as err:
        print("There was an error while analyzing:", err)
        traceback.print_exc()
        close_file_and_exit()
    args[IN_FILE].close()
    sort_and_write_result(wordcount_dict, args[OUT_FILE], OUT_FORMAT)
    args[OUT_FILE].close()






