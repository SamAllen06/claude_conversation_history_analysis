from argparse import ArgumentParser
from pathlib import Path

import math
import json
import datetime as dt

import pdb


# initialize global vars
all_data = {}
all_time = 'All Time'
per_month = "Per Month"
raw_data = 'Raw Data'
analyzed_data = 'Analyzed Data'
file_types = 'File Types'
all_file_types: list[str] = []


def calc_median(ints: list[int]) -> int:
    middle_position = len(ints)//2
    if len(ints)%2==0:
        return (ints[middle_position-1] + ints[middle_position])/2
    else:
        return ints[middle_position]


def calc_mmmr_box_plot(ints: list[int]) -> dict[str, float]:
    ints.sort()
    item_counts = dict()
    mmmr = 'MMMR'
    data = {}
    data[mmmr] = {}

    for item in ints:
        if item not in item_counts:
            item_counts.update({item: 0})
        item_counts[item] += 1

    mean = sum(ints)/len(ints)
    data[mmmr]['mean'] = mean
    data[mmmr]['median'] = calc_median(ints)

    mode_count = 0
    mode: list[int] = []
    for item in item_counts:
        if item_counts[item]>mode_count:
            mode_count = item_counts[item]
            mode = [item]
        elif item_counts[item]==mode_count:
            mode.append(item)
    data[mmmr]['mode'] = mode

    range = ints[-1]-ints[0]
    data[mmmr]['range'] = range

    if len(ints) >=5:
        box_plot = 'Box Plot'
        data[box_plot] = {}

        data[box_plot]['Minimum'] = ints[0]
        data[box_plot]['First Quartile'] = calc_median(ints[:len(ints)//2])
        data[box_plot]['Median'] = data[mmmr]['median']
        data[box_plot]['Mean'] = data[mmmr]['mean']
        data[box_plot]['Third Quartile'] = calc_median(ints[math.ceil(len(ints)/2):])
        data[box_plot]['Maximum'] = ints[-1]

    return data


def create_list_from_dict(dict: dict[str: dict[str: int]]) -> list[int]:
    result: list[int] = []
    for year in dict.values():
        for month in year.values():
            result.append(month)
    return result


def calc_mmmr_box_plot_for_all_months(data_name: str, dict: dict[str: dict[str: list[int]]]):
    all_data[analyzed_data][per_month][data_name] = {}
    for year in dict:
        all_data[analyzed_data][per_month][data_name][year] = {}
        for month in dict[year]:
            all_data[analyzed_data][per_month][data_name][year][month] = calc_mmmr_box_plot(dict[year][month])


def calc_mmmr_box_plot_for_all_months_all_file_types(data_name: str, dictionary: dict[str: dict[str: dict[str: int]]]):
    all_data[analyzed_data][per_month][file_types][data_name] = {}
    monthly_data_by_file_type: dict[str: list[int]] = {}
    for year in dictionary:
        for month in dictionary[year]:
            for file_type in dictionary[year][month]:
                if file_type not in monthly_data_by_file_type:
                    monthly_data_by_file_type.update({file_type: []})
                monthly_data_by_file_type[file_type].append(dictionary[year][month][file_type])
    for file_type in monthly_data_by_file_type:
        all_data[analyzed_data][per_month][file_types][data_name][file_type] = calc_mmmr_box_plot(monthly_data_by_file_type[file_type])


def append_int_to_dict_for_year_month(int, dict: dict[str: dict[str: list[int]]], year, month) -> dict[str: dict[str: list[int]]]:
    if year not in dict:
        dict.update({year: {}})
    if month not in dict[year]:
        dict[year].update({month: []})
    dict[year][month].append(int)
    return dict


def init_output_data_vars(list1: list[str], list2: list[str]):
    for list1_item in list1:
        all_data[list1_item] = {}
        for list2_item in list2:
            all_data[list1_item][list2_item] = {}


def add_missing_file_types(dictionary: dict[str: dict[str: dict[str: int]]]) -> dict[str: dict[str: dict[str: int]]]:
    for year in dictionary:
            for month in dictionary[year]:
                for file_type in all_file_types:
                    if file_type not in dictionary[year][month]:
                        dictionary[year][month].update({file_type: 0})
    return dictionary


def split_message(string: str) -> list[str]:
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


def add_to_single_words_dict(words_and_regexes: list[str], dictionary: dict[str: int]) -> dict[str:int]:
    i = check_if_contains_letter(words_and_regexes[0])
    while i < len(words_and_regexes):
        if words_and_regexes[i] not in dictionary:
            dictionary.update({words_and_regexes[i]: 0})
        dictionary[words_and_regexes[i]] += 1
        i += 2
    return dictionary


def add_to_double_words_dict(words_and_regexes: list[str], dictionary: dict[str: int]) -> dict[str:int]:
    i = check_if_contains_letter(words_and_regexes[0])
    while i < len(words_and_regexes)-2:
        three_strings: str = words_and_regexes[i] + words_and_regexes[i+1] + words_and_regexes[i+2]
        if three_strings not in dictionary:
            dictionary.update({three_strings: 0})
        dictionary[three_strings] += 1
        i += 2
    return dictionary


def add_to_triple_words_dict(words_and_regexes: list[str], dictionary: dict[str: int]) -> dict[str:int]:
    i = check_if_contains_letter(words_and_regexes[0])
    while i < len(words_and_regexes)-4:
        five_strings: str = words_and_regexes[i] + words_and_regexes[i+1] + words_and_regexes[i+2] + words_and_regexes[i+3] + words_and_regexes[i+4]
        if five_strings not in dictionary:
            dictionary.update({five_strings: 0})
        dictionary[five_strings] += 1
        i += 2
    return dictionary


def add_to_quadruple_words_dict(words_and_regexes: list[str], dictionary: dict[str: int]) -> dict[str:int]:
    i = check_if_contains_letter(words_and_regexes[0])
    while i < len(words_and_regexes)-6:
        seven_strings: str = words_and_regexes[i] + words_and_regexes[i+1] + words_and_regexes[i+2] + words_and_regexes[i+3] + words_and_regexes[i+4] + words_and_regexes[i+5] + words_and_regexes[i+6]
        if seven_strings not in dictionary:
            dictionary.update({seven_strings: 0})
        dictionary[seven_strings] += 1
        i += 2
    return dictionary


def add_to_quintuple_words_dict(words_and_regexes: list[str], dictionary: dict[str: int]) -> dict[str:int]:
    i = check_if_contains_letter(words_and_regexes[0])
    while i < len(words_and_regexes)-8:
        nine_strings: str = words_and_regexes[i] + words_and_regexes[i+1] + words_and_regexes[i+2] + words_and_regexes[i+3] + words_and_regexes[i+4] + words_and_regexes[i+5] + words_and_regexes[i+6] + words_and_regexes[i+7] + words_and_regexes[i+8]
        if nine_strings not in dictionary:
            dictionary.update({nine_strings: 0})
        dictionary[nine_strings] += 1
        i += 2
    return dictionary
    

def read_path() -> Path:
    parser = ArgumentParser(prog="anlyze_claude_data", description="Analyzes conversation history from Claude to get interesting data")
    parser.add_argument("input_json")
    args = parser.parse_args()
    return Path(args.input_json)


class main():
    input = read_path()
    with open(input, mode = "r", encoding = "utf-8") as infile:
        conversations = json.load(infile)

        # initialize input data vars
        # # initialize all time vars, lists, and dictionaries
        all_time_number_of_conversations = len(conversations)
        format = '%Y-%m-%dT%H:%M:%S.%f'
        days_using_claude = (dt.datetime.strptime(conversations[-1]['created_at'][0:-2], format) - dt.datetime.strptime(conversations[0]['created_at'][0:-2], format)).days
        all_time_ave_number_of_conversations_per_day = len(conversations) / days_using_claude
        all_time_number_of_messages = 0

        all_time_human_messages_lengths: list[int] = []
        all_time_first_human_messages_lengths: list[int] = []
        all_time_assistant_messages_lengths: list[int] = []
        all_time_conversations_lengths: list[int] = []
        all_time_files_per_conversation: list[int] = []
        all_time_files_per_conversation_from_human: list[int] = []
        all_time_files_per_conversation_from_assistant: list[int] = []

        all_time_file_numbers: dict[str, int] = {}
        all_time_file_numbers_from_human: dict[str, int] = {}
        all_time_file_numbers_from_assistant: dict[str, int] = {}
        # all_time_words_in_convo_titles: dict[str, int] = {}
        # all_time_two_word_combos_in_convo_titles: dict[str, int] = {}
        # all_time_three_word_combos_in_convo_titles: dict[str, int] = {}
        # all_time_four_word_combos_in_convo_titles: dict[str, int] = {}
        # all_time_five_word_combos_in_convo_titles: dict[str, int] = {}
        all_time_words_in_human_messages: dict[str, int] = {}
        # all_time_two_word_combos_in_human_messages: dict[str, int] = {}
        # all_time_three_word_combos_in_human_messages: dict[str, int] = {}
        # all_time_four_word_combos_in_human_messages: dict[str, int] = {}
        # all_time_five_word_combos_in_human_messages: dict[str, int] = {}
        # all_time_words_in_assistant_messages: dict[str, int] = {}
        # all_time_two_word_combos_in_assistant_messages: dict[str, int] = {}
        # all_time_three_word_combos_in_assistant_messages: dict[str, int] = {}
        # all_time_four_word_combos_in_assistant_messages: dict[str, int] = {}
        # all_time_five_word_combos_in_assistant_messages: dict[str, int] = {}

        # # initialize per month vars, lists, and dictionaries
        per_month_number_of_conversations: dict[str, dict[str, int]] = {}
        # initialize per_month_number_of_conversations with all months set to 0 conversations
        start_year = dt.datetime.strptime(conversations[0]['created_at'][0:-2], format).year
        start_year_start_month = dt.datetime.strptime(conversations[0]['created_at'][0:-2], format).month
        end_year = dt.datetime.strptime(conversations[-1]['created_at'][0:-2], format).year
        end_year_end_month = dt.datetime.strptime(conversations[-1]['created_at'][0:-2], format).month
        per_month_number_of_conversations.update({start_year: {}})
        while start_year_start_month <= 12:
            per_month_number_of_conversations[start_year].update({start_year_start_month: 0})
            start_year_start_month += 1
        start_year += 1
        while start_year < end_year:
            per_month_number_of_conversations.update({start_year: {}})
            month = 1
            while month <= 12:
                per_month_number_of_conversations[start_year].update({month: 0})
                month += 1
            start_year += 1
        per_month_number_of_conversations.update({end_year: {}})
        month = 1
        while month <= end_year_end_month:
            per_month_number_of_conversations[end_year].update({month: 0})
            month += 1

        per_month_human_messages_lengths: dict[str, dict[str, list[int]]] = {}
        per_month_first_human_messages_lengths: dict[str, dict[str, list[int]]] = {}
        per_month_assistant_messages_lengths: dict[str, dict[str, list[int]]] = {}
        per_month_conversations_lengths: dict[str, dict[str, list[int]]] = {}
        per_month_files_per_conversation: dict[str, dict[str, list[int]]] = {}
        per_month_files_per_conversation_from_human: dict[str, dict[str, list[int]]] = {}
        per_month_files_per_conversation_from_assistant: dict[str, dict[str, list[int]]] = {}

        per_month_file_numbers: dict[str, dict[str, dict[str, int]]] = {}
        per_month_file_numbers_from_human: dict[str, dict[str, dict[str, int]]] = {}
        per_month_file_numbers_from_assistant: dict[str, dict[str, dict[str, int]]] = {}
        # per_month_words_in_convo_titles: dict[str, dict[str, int]] = {}
        # per_month_two_word_combos_in_convo_titles: dict[str, dict[str, int]] = {}
        # per_month_three_word_combos_in_convo_titles: dict[str, dict[str, int]] = {}
        # per_month_four_word_combos_in_convo_titles: dict[str, dict[str, int]] = {}
        # per_month_five_word_combos_in_convo_titles: dict[str, dict[str, int]] = {}
        # per_month_words_in_human_messages: dict[str, dict[str, int]] = {}
        # per_month_two_word_combos_in_human_messages: dict[str, dict[str, int]] = {}
        # per_month_three_word_combos_in_human_messages: dict[str, dict[str, int]] = {}
        # per_month_four_word_combos_in_human_messages: dict[str, dict[str, int]] = {}
        # per_month_five_word_combos_in_human_messages: dict[str, dict[str, int]] = {}
        # per_month_words_in_assistant_messages: dict[str, dict[str, int]] = {}
        # per_month_two_word_combos_in_assistant_messages: dict[str, dict[str, int]] = {}
        # per_month_three_word_combos_in_assistant_messages: dict[str, dict[str, int]] = {}
        # per_month_four_word_combos_in_assistant_messages: dict[str, dict[str, int]] = {}
        # per_month_five_word_combos_in_assistant_messages: dict[str, dict[str, int]] = {}

        # get every conversation
        for conversation in range(0, len(conversations)):
            # make sure conversation not empty
            if (not conversations[conversation]['name']==""):
                # get date
                date = conversations[conversation]['created_at'][0:-2]
                year = dt.datetime.strptime(date, format).year
                month = dt.datetime.strptime(date, format).month
                # increase conversation number for its month
                per_month_number_of_conversations[year][month] += 1

                # get human first message length
                if conversations[conversation]['chat_messages']:
                    first_message_length = len(conversations[conversation]['chat_messages'][0]['text'])
                    all_time_first_human_messages_lengths.append(first_message_length)
                    per_month_first_human_messages_lengths = append_int_to_dict_for_year_month(first_message_length, per_month_first_human_messages_lengths, year, month)
                # get conversation length
                conversation_length = len(conversations[conversation]['chat_messages'])
                all_time_conversations_lengths.append(conversation_length)
                per_month_conversations_lengths = append_int_to_dict_for_year_month(conversation_length, per_month_conversations_lengths, year, month)
                # initialize variables to hold number of files in conversation
                conversation_number_of_files = 0
                conversation_number_of_files_from_human = 0
                conversation_number_of_files_from_assistant = 0
                # get every message
                for message in range(0, len(conversations[conversation]['chat_messages'])):
                    # get basic message info
                    words_and_regexes = split_message(repr(conversations[conversation]['chat_messages'][message]['text']))
                    all_time_number_of_messages += 1
                    message_length = len(conversations[conversation]['chat_messages'][message]['text'])
                    # get length of message from human
                    if conversations[conversation]['chat_messages'][message]['sender'] == "human":
                        all_time_human_messages_lengths.append(message_length)
                        per_month_human_messages_lengths = append_int_to_dict_for_year_month(message_length, per_month_human_messages_lengths, year, month)
                        all_time_words_in_human_messages = add_to_single_words_dict(words_and_regexes, all_time_words_in_human_messages)
                    # get length of message from assistant
                    if conversations[conversation]['chat_messages'][message]['sender'] == "assistant":
                        all_time_assistant_messages_lengths.append(message_length)
                        per_month_assistant_messages_lengths = append_int_to_dict_for_year_month(message_length, per_month_assistant_messages_lengths, year, month)
                    # get all files
                    for file in range(0, len(conversations[conversation]['chat_messages'][message]['files'])):
                        conversation_number_of_files += 1
                        #record file type
                        if "." not in conversations[conversation]['chat_messages'][message]['files'][file]['file_name']:
                            file_type = 'other'
                        else:
                            file_type = conversations[conversation]['chat_messages'][message]['files'][file]['file_name'].split('.')[-1]
                        if file_type not in all_file_types:
                            all_file_types.append(file_type)
                        # record number of each file
                        if file_type not in all_time_file_numbers:
                            all_time_file_numbers.update({file_type: 0})
                        all_time_file_numbers[file_type] += 1
                        if year not in per_month_file_numbers:
                            per_month_file_numbers.update({year: {}})
                        if month not in per_month_file_numbers[year]:
                            per_month_file_numbers[year].update({month: {}})
                        if file_type not in per_month_file_numbers[year][month]:
                            per_month_file_numbers[year][month].update({file_type:0})
                        per_month_file_numbers[year][month][file_type] += 1
                        # record number of each file from human
                        if conversations[conversation]['chat_messages'][message]['sender'] == "human":
                            if file_type not in all_time_file_numbers_from_human:
                                all_time_file_numbers_from_human.update({file_type: 0})
                            all_time_file_numbers_from_human[file_type] += 1
                            conversation_number_of_files_from_human += 1
                            if year not in per_month_file_numbers_from_human:
                                per_month_file_numbers_from_human.update({year: {}})
                            if month not in per_month_file_numbers_from_human[year]:
                                per_month_file_numbers_from_human[year].update({month: {}})
                            if file_type not in per_month_file_numbers_from_human[year][month]:
                                per_month_file_numbers_from_human[year][month].update({file_type:0})
                            per_month_file_numbers_from_human[year][month][file_type] += 1
                        # record number of each file from assistant
                        elif conversations[conversation]['chat_messages'][message]['sender'] == 'assistant':
                            if file_type not in all_time_file_numbers_from_assistant:
                                all_time_file_numbers_from_assistant.update({file_type: 0})
                            all_time_file_numbers_from_assistant[file_type] += 1
                            conversation_number_of_files_from_assistant += 1
                            if year not in per_month_file_numbers_from_assistant:
                                per_month_file_numbers_from_assistant.update({year: {}})
                            if month not in per_month_file_numbers_from_assistant[year]:
                                per_month_file_numbers_from_assistant[year].update({month: {}})
                            if file_type not in per_month_file_numbers_from_assistant[year][month]:
                                per_month_file_numbers_from_assistant[year][month].update({file_type:0})
                            per_month_file_numbers_from_assistant[year][month][file_type] += 1
                # save number of files from conversation
                all_time_files_per_conversation.append(conversation_number_of_files)
                all_time_files_per_conversation_from_human.append(conversation_number_of_files_from_human)
                all_time_files_per_conversation_from_assistant.append(conversation_number_of_files_from_assistant)
                per_month_files_per_conversation = append_int_to_dict_for_year_month(conversation_number_of_files, per_month_files_per_conversation, year, month)
                per_month_files_per_conversation_from_human = append_int_to_dict_for_year_month(conversation_number_of_files_from_human, per_month_files_per_conversation_from_human, year, month)
                per_month_files_per_conversation_from_assistant = append_int_to_dict_for_year_month(conversation_number_of_files_from_assistant, per_month_files_per_conversation_from_assistant, year, month)

        # initialize naming vars
        overall = 'Overall'
        from_human = 'From Human'
        from_assistant = 'From Assistant'
        per_conversation = 'Per Conversation'
        misc = 'Miscellaneous'

        # initialize output data vars
        all_data[misc] = {}
        init_output_data_vars([analyzed_data, raw_data], [all_time, per_month])
        all_data[raw_data][per_conversation] = {}

        # save miscellaneous data
        all_data[misc]['Number of Conversations'] = all_time_number_of_conversations
        all_data[misc]['Average Number of Conversations per Day'] = all_time_ave_number_of_conversations_per_day
        all_data[misc]['Average Number of Messages per Day'] = all_time_number_of_messages / days_using_claude

        # save raw data
        #TODO Make sure I've gotten ALL OF THE RAW DATA FROM DATA BELOW
        all_data[raw_data][all_time][file_types] = {}
        all_data[raw_data][all_time][file_types][overall] = all_time_file_numbers
        all_data[raw_data][all_time][file_types][from_human] = all_time_file_numbers_from_human
        all_data[raw_data][all_time][file_types][from_assistant] = all_time_file_numbers_from_assistant
        all_data[raw_data][per_month]['Conversations by Month'] = per_month_number_of_conversations
        #TODO MAKE LISTS IN THIS RAW DATA NOT SORTED. Whenever you save a list of ints to a json, it automatically sorts it
        all_data[raw_data][per_month]['Length of Messages from Human'] = per_month_human_messages_lengths
        all_data[raw_data][per_month]['Length of First Conversation Message from Human'] = per_month_first_human_messages_lengths
        all_data[raw_data][per_month]['Length of Messages from Assistant'] = per_month_assistant_messages_lengths
        all_data[raw_data][per_month]['Number of Files per Conversation'] = per_month_files_per_conversation
        all_data[raw_data][per_month]['Number of Files from Human per Conversation'] = per_month_files_per_conversation_from_human
        all_data[raw_data][per_month]['Number of Files from Assistant per Conversation'] = per_month_files_per_conversation_from_assistant
        all_data[raw_data][per_month][file_types] = {}
        all_data[raw_data][per_month][file_types][overall] = add_missing_file_types(per_month_file_numbers)
        all_data[raw_data][per_month][file_types][from_human] = add_missing_file_types(per_month_file_numbers_from_human)
        all_data[raw_data][per_month][file_types][from_assistant] = add_missing_file_types(per_month_file_numbers_from_assistant)
        all_data[raw_data][per_conversation]['Length of Messages from Human'] = all_time_human_messages_lengths
        all_data[raw_data][per_conversation]['Length of First Conversation Message from Human'] = all_time_first_human_messages_lengths
        all_data[raw_data][per_conversation]['Length of Messages from Assistant'] = all_time_assistant_messages_lengths
        all_data[raw_data][per_conversation]['Length of Conversations'] = all_time_conversations_lengths
        all_data[raw_data][per_conversation]['Number of Files'] = all_time_files_per_conversation
        all_data[raw_data][per_conversation]['Number of Files from Human'] = all_time_files_per_conversation_from_human
        all_data[raw_data][per_conversation]['Number of Files from Assistant'] = all_time_files_per_conversation_from_assistant

        # calculate mean, median, mode, and range for data
        all_data[analyzed_data][all_time]['Length of Messages from Human']                       = calc_mmmr_box_plot(all_time_human_messages_lengths)
        all_data[analyzed_data][all_time]['Length of First Conversation Message from Human']     = calc_mmmr_box_plot(all_time_first_human_messages_lengths)
        all_data[analyzed_data][all_time]['Length of Messages from Assistant']                   = calc_mmmr_box_plot(all_time_assistant_messages_lengths)
        all_data[analyzed_data][all_time]['Length of Conversations']                             = calc_mmmr_box_plot(all_time_conversations_lengths)
        all_data[analyzed_data][all_time]['Number of Files per Conversation']                    = calc_mmmr_box_plot(all_time_files_per_conversation)
        all_data[analyzed_data][all_time]['Number of Files from Human per Conversation']         = calc_mmmr_box_plot(all_time_files_per_conversation_from_human)
        all_data[analyzed_data][all_time]['Number of Files from Assistant per Conversation']     = calc_mmmr_box_plot(all_time_files_per_conversation_from_assistant)
        #TODO extrapolate this out
        all_data['Words and Phrases'] = {}
        all_data['Words and Phrases'][all_time] = {}
        all_data['Words and Phrases'][all_time]['From Human'] = {}
        all_data['Words and Phrases'][all_time]['From Human']['Singles'] = all_time_words_in_human_messages
        all_data[analyzed_data][per_month]['Number of Conversations']                            = calc_mmmr_box_plot(create_list_from_dict(per_month_number_of_conversations))
        calc_mmmr_box_plot_for_all_months('Length of Messages from Human', per_month_human_messages_lengths)
        calc_mmmr_box_plot_for_all_months('Length of First Conversation Message from Human', per_month_first_human_messages_lengths)
        calc_mmmr_box_plot_for_all_months('Length of Messages from Assistant', per_month_assistant_messages_lengths)
        calc_mmmr_box_plot_for_all_months('Number of Files per Conversation', per_month_files_per_conversation)
        calc_mmmr_box_plot_for_all_months('Number of Files from Human per Conversation', per_month_files_per_conversation_from_human)
        calc_mmmr_box_plot_for_all_months('Number of Files from Assistant per Conversation', per_month_files_per_conversation_from_assistant)
        all_data[analyzed_data][per_month][file_types] = {}
        calc_mmmr_box_plot_for_all_months_all_file_types(overall, per_month_file_numbers)
        calc_mmmr_box_plot_for_all_months_all_file_types(from_human, per_month_file_numbers_from_human)
        calc_mmmr_box_plot_for_all_months_all_file_types(from_assistant, per_month_file_numbers_from_assistant)
                
        with open("../output/output.json", mode='w', encoding='utf-8') as outfile:
            json.dump(all_data, outfile, indent=2)

if __name__=='__main__':
    main()

#TODO make sure output_json_data_structure.png is fully updated