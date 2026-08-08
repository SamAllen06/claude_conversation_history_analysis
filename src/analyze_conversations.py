from argparse import ArgumentParser
from pathlib import Path

import json
import datetime as dt

from table_handler import MultiDimTable

def split_string(string: str) -> list[str]:
    strings: list[str] = []
    special_chars = ["\\x92"]
    
    current_word = ""
    current_regex = ""
    i = 1
    at_regex = not string[i].isalnum()

    while i < len(string)-1:
        if string[i].isalnum():
            if at_regex:
                strings.append(current_regex)
                current_regex = ""
                at_regex = False
            current_word += string[i]
        elif string[i]=="\\":
            if string[i:i+4] in special_chars:
                if at_regex:
                    strings.append(current_regex)
                    current_regex = ""
                    at_regex = False
                current_word += string[i:i+4]
                i = i+3
            else:
                if not at_regex:
                    strings.append(current_word)
                    current_word = ""
                    at_regex = True
                current_regex += string[i]
                i += 1
        else:
            if not at_regex:
                strings.append(current_word)
                current_word = ""
                at_regex = True
            current_regex += string[i]

        i += 1
    if at_regex:
        strings.append(current_regex)
    else:
        strings.append(current_word) 
    return strings


def check_if_contains_letter(string) -> int:
    is_regex = True
    for char in string:
        if char.isalnum():
            is_regex = False
    if is_regex:
        return 1
    else: 
        return 0


def make_list_of_phrase_dicts(words_and_regexes: list[str]) -> list[dict[str: int]]:
    list_of_phrase_dicts: list[dict[str: int]] = []
    for phrase_length in range(1, 6):
        words_dict: dict[str: int] = {}
        i = check_if_contains_letter(words_and_regexes[0])
        while i < len(words_and_regexes)-(phrase_length*2-2):
            phrase: str = ""
            for j in range(phrase_length*2-1):
                phrase += words_and_regexes[i+j]
            if phrase not in words_dict:
                words_dict[phrase] = 0
            words_dict[phrase] += 1
            i += 2
        list_of_phrase_dicts.append(words_dict)
    return list_of_phrase_dicts


def extract_data(input):
    with open(input, mode = "r", encoding = "utf-8") as infile:
        conversations = json.load(infile)

        # initialize misc. vars
        misc_output: dict[str: int] = {}

        ## initialize tables' first dimension headers with all possible months and years
        date_coords: list[str] = []

        format = '%Y-%m-%dT%H:%M:%S.%f'
        start_year = dt.datetime.strptime(conversations[0]['created_at'][0:-2], format).year
        start_year_start_month = dt.datetime.strptime(conversations[0]['created_at'][0:-2], format).month
        end_year = dt.datetime.strptime(conversations[-1]['created_at'][0:-2], format).year
        end_year_end_month = dt.datetime.strptime(conversations[-1]['created_at'][0:-2], format).month

        for year in range(start_year, end_year+1):
            if year == start_year:
                for month in range(start_year_start_month, 13):
                    date_coords.append(str(month) + "/" + str(year))
            elif year == end_year:
                for month in range(1, end_year_end_month+1):
                    date_coords.append(str(month) + "/" + str(year))
            else:
                for month in range(1, 13):
                    date_coords.append(str(month) + "/" + str(year))

        ## initialize 2nd dimensions
        number_of_conversations = "Number of conversations"
        user_message_lengths = "Lengths of messages from user"
        first_user_message_lengths = "Lengths of first messages from user"
        assistant_message_lengths = "Lengths of messages from assistant"
        per_conversation_user_messages = "Number of messages from user per conversation"
        numeric_category_coords: list[str] = [number_of_conversations, first_user_message_lengths, per_conversation_user_messages, user_message_lengths, assistant_message_lengths]

        from_user = "From user"
        from_assistant = "From assistant"
        file_type_categories: list[str] = [from_user, from_assistant]

        phrases_in_convo_names = "Phrases from generated conversation names"
        phrases_in_user_messages = "Phrases from user's messages"
        phrases_in_assistant_messages = "Phrases from assistant's messages"
        phrase_categories: list[str] = [phrases_in_convo_names, phrases_in_user_messages, phrases_in_assistant_messages]

        # initialize phrase length categories
        singles = "One Word Phrases"
        doubles = "Two Word Phrases"
        triples = "Three Word Phrases"
        quads = "Four Word Phrases"
        quints = "Five Word Phrases"
        phrase_lengths: list[str] = [singles, doubles, triples, quads, quints]

        ## initialize tables' 3rd dimension headers
        # this will need to be updated as the conversation is read, as different users will have different file types
        file_types_3rd_dim: list[str] = []

        ## initialize output tables
        # 3D table: Date x Category x Conversation Data (of various lengths, doesn't need a header, order is irrelevant) with the data type int
        # numeric_output: list[list[list[int]]] = []
        # for _ in range(len(date_coords)):
        #     row: list[list[int]] = []
        #     for _ in range(len(numeric_category_coords)):
        #         row.append(None)
        #     numeric_output.append(row)

        numeric_output = MultiDimTable({"Date": date_coords, "Category": numeric_category_coords})
        import pdb; pdb.set_trace()

        # 4D table: Date x Category x Phrase Length x Conversation Data with the data type dict[str: int]
        phrase_output: list[list[list[list[dict[str: int]]]]] = []
        for _ in range(len(date_coords)):
            row: list[list[list[dict[str: int]]]] = []
            for _ in range(len(phrase_categories)):
                row2: list[list[dict[str: int]]] = []
                for _ in range(len(phrase_lengths)):
                    row2.append(None)
                row.append(row2)
            phrase_output.append(row)

        # 4D table: Date x Category x File Type
        file_output: list[list[list[list[list[int]]]]] = []
        # 3rd dim will be initialized as needed, as different users will have different file types
        for _ in range(len(date_coords)):
            row: list[list[list[list[int]]]] = []
            for _ in range(len(file_type_categories)):
                row.append([])
            file_output.append(row)
        
        for conversation in range(0, len(conversations)):
            # make sure conversation not empty
            if not conversations[conversation]['name'] == "":
                # get date
                # date = dt.datetime.strptime(conversations[conversation]['created_at'][0:-2], format).strftime("%m/%Y")
                unstripped_date = conversations[conversation]['created_at'][0:-2]
                year = dt.datetime.strptime(unstripped_date, format).year
                month = dt.datetime.strptime(unstripped_date, format).month
                date = str(month) + "/" + str(year)

                # increase conversation count for its month
                if numeric_output[date_coords.index(date)][numeric_category_coords.index(number_of_conversations)] is None:
                    numeric_output[date_coords.index(date)][numeric_category_coords.index(number_of_conversations)] = 0
                numeric_output[date_coords.index(date)][numeric_category_coords.index(number_of_conversations)] += 1

                # get first message length
                if conversations[conversation]['chat_messages']:
                    first_message_length = len(conversations[conversation]['chat_messages'][0]['text'])
                    if numeric_output[date_coords.index(date)][numeric_category_coords.index(first_user_message_lengths)] is None:
                        numeric_output[date_coords.index(date)][numeric_category_coords.index(first_user_message_lengths)] = []
                    numeric_output[date_coords.index(date)][numeric_category_coords.index(first_user_message_lengths)].append(first_message_length)

                # get number of messages from user in the conversation
                if numeric_output[date_coords.index(date)][numeric_category_coords.index(per_conversation_user_messages)] is None:
                    numeric_output[date_coords.index(date)][numeric_category_coords.index(per_conversation_user_messages)] = []
                numeric_output[date_coords.index(date)][numeric_category_coords.index(per_conversation_user_messages)].append(len(conversations[conversation]['chat_messages'])/2)

                # get conversation name phrases
                title_words_and_regexes = split_string(repr(conversations[conversation]['name']))
                phrase_output[date_coords.index(date)][phrase_categories.index(phrases_in_convo_names)] = make_list_of_phrase_dicts(title_words_and_regexes)

                # get every message in the conversation
                for message in range(0, len(conversations[conversation]['chat_messages'])):
                    # get basic message info
                    message_words_and_regexes = split_string(repr(conversations[conversation]['chat_messages'][message]['text']))
                    message_length = len(conversations[conversation]['chat_messages'][message]['text'])

                    # save to info about messages from user
                    if conversations[conversation]['chat_messages'][message]['sender'] == 'human':
                        if numeric_output[date_coords.index(date)][numeric_category_coords.index(user_message_lengths)] is None:
                            numeric_output[date_coords.index(date)][numeric_category_coords.index(user_message_lengths)] = []
                        numeric_output[date_coords.index(date)][numeric_category_coords.index(user_message_lengths)].append(message_length)

                        # get phrases from message
                        phrase_output[date_coords.index(date)][phrase_categories.index(phrases_in_user_messages)] = make_list_of_phrase_dicts(message_words_and_regexes)

                        # get all files in message from user
                        for file in range(0, len(conversations[conversation]['chat_messages'][message]['files'])):
                            # record file type
                            if "." not in conversations[conversation]['chat_messages'][message]['files'][file]['file_name']:
                                file_type = 'other'
                            else:
                                file_type = conversations[conversation]['chat_messages'][message]['files'][file]['file_name'].split('.')[-1]
                            if file_type not in file_types_3rd_dim:
                                file_types_3rd_dim.append(file_type)
                                for temp_date in range(len(date_coords)):
                                    for temp_sender in range(len(file_type_categories)):
                                        file_output[temp_date][temp_sender].append(0)
                            file_output[date_coords.index(date)][file_type_categories.index(from_user)][file_types_3rd_dim.index(file_type)] += 1

                    elif conversations[conversation]['chat_messages'][message]['sender'] == 'assistant':
                        if numeric_output[date_coords.index(date)][numeric_category_coords.index(assistant_message_lengths)] is None:
                            numeric_output[date_coords.index(date)][numeric_category_coords.index(assistant_message_lengths)] = []
                        numeric_output[date_coords.index(date)][numeric_category_coords.index(assistant_message_lengths)].append(message_length)

                        # get phrases from message
                        phrase_output[date_coords.index(date)][phrase_categories.index(phrases_in_assistant_messages)] = make_list_of_phrase_dicts(message_words_and_regexes)

                        for file in range(0, len(conversations[conversation]['chat_messages'][message]['files'])):
                            # record file type
                            if "." not in conversations[conversation]['chat_messages'][message]['files'][file]['file_name']:
                                file_type = 'other'
                            else:
                                file_type = conversations[conversation]['chat_messages'][message]['files'][file]['file_name'].split('.')[-1]
                            if file_type not in file_types_3rd_dim:
                                file_types_3rd_dim.append(file_type)
                                for temp_date in range(len(date_coords)):
                                    for temp_sender in range(len(file_type_categories)):
                                        file_output[temp_date][temp_sender].append(0)
                            file_output[date_coords.index(date)][file_type_categories.index(from_user)][file_types_3rd_dim.index(file_type)] += 1

        # save raw data
        with open("claude_conversation_history_analysis/output/numeric_output.json", mode='w', encoding='utf-8') as outfile:
            json.dump(numeric_output, outfile, indent=2)

        with open("claude_conversation_history_analysis/output/phrase_output.json", mode='w', encoding='utf-8') as outfile:
            json.dump(phrase_output, outfile, indent=2)

        with open("claude_conversation_history_analysis/output/file_output.json", mode='w', encoding='utf-8') as outfile:
            json.dump(file_output, outfile, indent=2)


def read_path() -> Path:
    parser = ArgumentParser(prog="anlyze_claude_data", description="Analyzes conversation history from Claude to get interesting data")
    parser.add_argument("input_json")
    args = parser.parse_args()
    return Path(args.input_json)


def main():
    input = read_path()
    extract_data(input)


if __name__ == "__main__":
    main()
