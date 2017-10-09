import random
from copy import deepcopy
import pickle
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import os

# phrase_extraction('resumption of the session', 'wiederaufnahme der sitzungsperiode', [[0,0], [1,1], [1,2], [2,3]])

# resumption of the session
# wiederaufnahme der sitzungsperiode
# 0-0 1-1 1-2 2-3

# alignments = [[0,0], [1,1], [1,2], [2,3]]
def phrase_extraction(sen1, sen2, alignments):#, en_sub_phrases, de_sub_phrases):
    sen1_words = sen1.split(" ")
    sen2_words = sen2.split(" ")

    smallest_seg = []
    words_with_alignments = [[],[]]
    words_without_alignments = [[],[]]
    #[[12],[]] <- words without alignments example
    for a in alignments:
        left = ""
        right = ""
        for a2 in alignments:
            if a[0] == a2[0]:
                right += a2[1] + " "
            if a[1] == a2[1]:
                left += a2[0] + " "
        add_to_array_if_it_doesnt_contain_reps(int(a[0]), words_with_alignments[0])
        add_to_array_if_it_doesnt_contain_reps(int(a[1]), words_with_alignments[1])
        right = right[:-1]
        left = left[:-1]
        if [left, right] not in smallest_seg:
            smallest_seg.append([left,right])

    # find indexes of words without alignments
    for language_index,language in enumerate(words_with_alignments):
        pass_numbers = 0
        language.sort()
        for i,word_as_num in enumerate(language):
            i += pass_numbers
            if i!=word_as_num:
                while(word_as_num!=i):
                    word_as_num -= 1
                    pass_numbers += 1
                    words_without_alignments[language_index ].append(word_as_num)


    len_smallest_seg = len(smallest_seg)
    aligned_sub_phrases = []
    aligned_sub_phrases_in_words = []
    #seg_aligned_sub_phrases = []
    
    for i, element in enumerate(smallest_seg):
        en_strings = ''
        de_strings = ''
        for index in range(i, len_smallest_seg):
            aligned_words = smallest_seg[i:index+1]

            en_strings = add_string_if_it_doesnt_contain_reps(smallest_seg[index][1], en_strings)
            de_strings = add_string_if_it_doesnt_contain_reps(smallest_seg[index][0], de_strings)
            possibilities = [[de_strings], [en_strings]]

            # add words_without_alignments that are in the middle of the subphrase (always added)
            for l, language in enumerate(words_without_alignments):
                max_l = max([int(poss) for poss in possibilities[l][0].split()])
                min_l = min([int(poss) for poss in possibilities[l][0].split()])
                for word_without_alignment in language:
                    if word_without_alignment < max_l and word_without_alignment > min_l:
                        possibilities[l][0] = add_string_if_it_doesnt_contain_reps(str(word_without_alignment), possibilities[l][0])

            # add words_without_alignments on the borders (all possible combinations)
            for l, language in enumerate(words_without_alignments):
                max_l = max([int(poss) for poss in possibilities[l][0].split()])
                min_l = min([int(poss) for poss in possibilities[l][0].split()])
                left_word_without = []
                right_word_without = []
                word = 0
                while word < len(language):
                    word_without_alignment = language[word]
                    if word_without_alignment == min_l-1:
                        left_word_without.append(word_without_alignment)
                        min_l = word_without_alignment
                        word = -1
                    elif word_without_alignment == max_l+1:
                        right_word_without.append(word_without_alignment)
                        max_l = word_without_alignment
                        word = -1
                    word+=1
                left_word_without.sort()
                right_word_without.sort()
                if len(left_word_without) != 0:
                    possibilities[l] = add_possibilities_left(possibilities[l], left_word_without)
                if len(right_word_without) != 0:
                    possibilities[l] = add_possibilities_right(possibilities[l], right_word_without)
                if len(left_word_without) != 0 and len(right_word_without) != 0:
                    possibilities[l] = add_possibilities_left_right(possibilities[l], left_word_without, right_word_without)

            en_strings = reorder_string(possibilities[1][0])
            de_strings = reorder_string(possibilities[0][0])
            for de_poss in possibilities[0]:
                for en_poss in possibilities[1]:
                    # make sure the longest subphrase is 7 words
                    if len(en_poss.split()) <= 7 and len(de_poss.split()) <= 7:
                        aux_en_strings = reorder_string(en_poss)
                        aux_de_strings = reorder_string(de_poss)
                        if check_continuity(aux_en_strings, aux_de_strings):
                            aux_en_strings = aux_en_strings[:-1]
                            aux_de_strings = aux_de_strings[:-1]
                            #en_sub_phrases[aux_en_strings] = en_sub_phrases.get(aux_en_strings, 0) + 1
                            #de_sub_phrases[aux_de_strings] = de_sub_phrases.get(aux_de_strings, 0) + 1
                            aux_en_strings_in_words = translate_numbers_to_words(aux_en_strings, sen1_words)
                            aux_de_strings_in_words = translate_numbers_to_words(aux_de_strings, sen2_words)
                            aux_en_strings_in_words = aux_en_strings_in_words[:-1]
                            aux_de_strings_in_words = aux_de_strings_in_words[:-1]
                            if aux_en_strings + ' ^ ' + aux_de_strings not in aligned_sub_phrases:
                                aligned_sub_phrases.append(aux_en_strings + ' ^ ' + aux_de_strings)
                                #seg_aligned_sub_phrases.append(aligned_words);#translate_numbers_to_words_aligned(aligned_words, sen1_words, sen2_words))
                                aligned_sub_phrases_in_words.append(aux_en_strings_in_words + ' ^ ' + aux_de_strings_in_words)
                        


    return aligned_sub_phrases, aligned_sub_phrases_in_words#seg_aligned_sub_phrases


def add_string_if_it_doesnt_contain_reps(substring, strings):
    for sub_number in substring.split():
        if sub_number in strings.split():
            pass
        else:
            strings += sub_number + ' '
    return strings

def add_to_array_if_it_doesnt_contain_reps(sub_number, array):
    if sub_number in array:
        pass
    else:
        array.append(sub_number)
    return array

def translate_numbers_to_words(string, sentence_words):
    aux_string = ""
    for substring in string.split():
        aux_string += sentence_words[int(substring)] + " "
    return aux_string

def translate_numbers_to_words_aligned(aligned_words, sen1_words, sen2_words):
    aux = deepcopy(aligned_words)
    for i in range(len(aligned_words)):
        for j in range(len(aligned_words[i])):
            aux_string = ""
            for substring in aligned_words[i][j].split():
                if j == 0: aux_string += sen2_words[int(substring)] + " "
                elif j == 1: aux_string += sen1_words[int(substring)] + " "
            aux[i][j] = aux_string[:-1]
    return aux

def reorder_string(strings):
    aux_string = [int(i) for i in strings.split()]
    aux_string.sort()
    aux_string = [str(i) for i in aux_string]
    return " ".join(aux_string) + " "

def check_continuity(en_strings, de_strings):
    en_it = (int(x) for x in en_strings.split())
    en_first = next(en_it)
    de_it = (int(x) for x in de_strings.split())
    de_first = next(de_it)
    return all(a == b for a, b in enumerate(en_it, en_first + 1)) and all(a == b for a, b in enumerate(de_it, de_first + 1))

def add_possibilities_left_right(possibilities_l, left_words, right_words):
    # left_words and right_words must be sorted
    add_left = []
    add_right = []
    for left_w in reversed(left_words):
        add_left.append(str(left_w))
        possibilities_l.append(' '.join(add_left)+' '+possibilities_l[0])
        for right_w in right_words:
            add_right.append(str(right_w))
            possibilities_l.append(' '.join(add_left)+' '+possibilities_l[0]+' '.join(add_right)+' ')
        add_right = []
    for right_w in right_words:
        add_right.append(str(right_w))
        possibilities_l.append(possibilities_l[0]+' '.join(add_right)+' ')
    return possibilities_l

def add_possibilities_left(possibilities_l, left_words):
    add_left = []
    for left_w in reversed(left_words):
        add_left.append(str(left_w))
        possibilities_l.append(' '.join(add_left)+' '+possibilities_l[0])
    return possibilities_l

def add_possibilities_right(possibilities_l, right_words):
    # left_words and right_words must be sorted
    add_right = []
    for right_w in right_words:
        add_right.append(str(right_w))
        possibilities_l.append(possibilities_l[0]+' '.join(add_right)+' ')
    return possibilities_l

def create_dicts(en_txt,de_txt,alignments, no_of_sentences=50000, sentence_start=0):
    '''en_dic = {}
                de_dic = {}
                en_de_dic = {}
                aligns_dic = {}
                # KMO dictionaries
                count_ef = {}# count of appeareances of single words aligned to other language words
                we = {}# appearance of single words (english)
                wf = {}# appearance of single words (deutsch)'''
    # assignment 2: dictionary['sentence']=[[subphrases]]
    subphrases_dic = {}
    # dictionary containing every subphrase
    list_of_subphrases_dic = {}

    j = 0
    k = 0

    for en_sen, de_sen, alignment in zip(en_txt[sentence_start:no_of_sentences], de_txt[sentence_start:no_of_sentences], alignments[sentence_start:no_of_sentences]):   
        if j % 100 == 0:
            print(float(j)/no_of_sentences)
        j += 1

        # alignments = [[0,0], [1,1], [1,2], [2,3]]
        alignment = alignment.split()#.split('-')
        for i, el in enumerate(alignment):
            alignment[i] = el.split('-')
        
        aligned_sub_phrases, aligned_sub_phrases_in_words = phrase_extraction(en_sen[:-1], de_sen[:-1], alignment)#, en_dic, de_dic)

        subphrases_dic[en_sen[:-1]+" ^ "+de_sen[:-1]] = aligned_sub_phrases;

        for al in aligned_sub_phrases_in_words:
            list_of_subphrases_dic[al] = 0

        '''for al, alignments, al_in_words in zip(aligned_sub_phrases, seg_aligned_sub_phrases, aligned_sub_phrases_in_words):
                                    if al_in_words not in aligns_dic:
                                        # Stores alignments of the sub_phrase. Used in lexical_translation_probabilities(). Example:
                                        # aligns_dic["session of the ^ sitzungsperiode des"] = [['sitzungsperiode', 'session'], ['des', 'of the']]
                                        aligns_dic["".join(al_in_words)] = alignments'''

    return subphrases_dic, list_of_subphrases_dic#, aligns_dic


# assuming subphrases_dic['sentence (in english)'] = [['e_sub_1 ^ f_sub_1'], ['e_sub_2 ^ f_sub_2'], ['e_sub_3 ^ f_sub_3']]
#                                                  = [['0 1 2 ^ 2 3 4'],...]
def count_reorderings(en_sentences, de_sentences, subphrases_dic, alignments):
    # only phrase-based for now
    # ASSUMING SUBPHRASES IN DICTIONARY ARE IN ORDER (in order of english words)
    # ASSUMING EVERYTHING IS NUMBERS
    p_l_r_m_phrase_based  = {}
    p_l_r_s_phrase_based  = {}
    p_l_r_dl_phrase_based = {}
    p_l_r_dr_phrase_based = {}
    p_r_l_m_phrase_based  = {}
    p_r_l_s_phrase_based  = {}
    p_r_l_dl_phrase_based = {}
    p_r_l_dr_phrase_based = {}
    p_l_r_m_word_based    = {}
    p_l_r_s_word_based    = {}
    p_l_r_dl_word_based   = {}
    p_l_r_dr_word_based   = {}
    p_r_l_m_word_based    = {}
    p_r_l_s_word_based    = {}
    p_r_l_dl_word_based   = {}
    p_r_l_dr_word_based   = {}
    j=0
    for en_sen, de_sen, aligns in zip(en_sentences, de_sentences, alignments):
        if j % 100 == 0:
            print(float(j)/50000)
        j += 1
        #
        subphrases = subphrases_dic[en_sen[:-1]+" ^ "+de_sen[:-1]]
        for s_id, subphr in enumerate(subphrases):
            [en1, de1] = subphr.split(" ^ ")
            if len(en1.split()) <= 7 and len(de1.split()) <= 7:
                subphr_in_words = translate_numbers_to_words(en1, en_sen[:-1].split(" "))[:-1] + " ^ " + translate_numbers_to_words(de1, de_sen[:-1].split(" "))[:-1]
                #subphr_in_words = subphr
                last_word_en1  = en1.split()[-1]
                first_word_en1 = en1.split()[0]

                '''if w_id != len(sent_split):#left to right
                    if int(last_word_en) == w_id:'''
                #phrase-based
                for s_id2 in range(len(subphrases)):
                    [en2, de2] = subphrases[s_id2].split(" ^ ")
                    first_word_en2 = en2.split()[0]
                    last_word_en2  = en2.split()[-1]
                    if first_word_en2 == str(int(last_word_en1)+1):#left to right
                        last_word_de1  = de1.split()[-1]
                        first_word_de2 = de2.split()[0]
                        jump_size = int(first_word_de2)-int(last_word_de1)
                        if jump_size == 1:#monotonous
                            p_l_r_m_phrase_based[subphr_in_words]  = p_l_r_m_phrase_based.get(subphr_in_words, 0)  + 1
                        elif jump_size > 1:#discontinous
                            p_l_r_dr_phrase_based[subphr_in_words] = p_l_r_dr_phrase_based.get(subphr_in_words, 0) + 1
                        first_word_de1 = de1.split()[0]
                        last_word_de2  = de2.split()[-1]
                        jump_size = int(first_word_de1)-int(last_word_de2)
                        if jump_size == 1:#swap
                            p_l_r_s_phrase_based[subphr_in_words]  = p_l_r_s_phrase_based.get(subphr_in_words, 0)  + 1
                        elif jump_size > 1:#discontinous
                            p_l_r_dl_phrase_based[subphr_in_words] = p_l_r_dl_phrase_based.get(subphr_in_words, 0) + 1

                    if last_word_en2 == str(int(first_word_en1)-1):#right to left
                        first_word_de1 = de1.split()[0]
                        last_word_de2  = de2.split()[-1]
                        jump_size = int(first_word_de1)-int(last_word_de2)
                        if jump_size == 1:#monotonous
                            p_r_l_m_phrase_based[subphr_in_words]  = p_r_l_m_phrase_based.get(subphr_in_words, 0)  + 1
                        elif jump_size > 1:#discontinous
                            p_r_l_dl_phrase_based[subphr_in_words] = p_r_l_dl_phrase_based.get(subphr_in_words, 0) + 1
                        last_word_de1  = de1.split()[-1]
                        first_word_de2 = de2.split()[0]
                        jump_size = int(first_word_de2)-int(last_word_de1)
                        if jump_size == 1:#swap
                            p_r_l_s_phrase_based[subphr_in_words]  = p_r_l_s_phrase_based.get(subphr_in_words, 0)  + 1
                        elif jump_size > 1:#discontinous
                            p_r_l_dr_phrase_based[subphr_in_words] = p_r_l_dr_phrase_based.get(subphr_in_words, 0) + 1

                    #word-based
                    found_left  = 0
                    found_right = 0
                    addition_left = 1
                    addition_right = 1
                    if int(first_word_en1) == 0: found_left = 1
                    if int(last_word_en1)  == len(en_sen.split()): found_right = 1
                    while(found_left == 0 and found_right == 0):
                        for align in aligns.split():
                            word_en2 = align.split('-')[1]
                            word_de2 = align.split('-')[0]
                            if found_right == 0:
                                if word_en2 == str(int(last_word_en1)+addition_right):#left to right
                                    found_right = 1
                                    last_word_de1 = de1.split()[-1]
                                    jump_size = int(word_de2)-int(last_word_de1)
                                    if jump_size == 1:#monotonous
                                        p_l_r_m_word_based[subphr_in_words]  = p_l_r_m_word_based.get(subphr_in_words, 0)  + 1
                                    elif jump_size > 1:#discontinous
                                        p_l_r_dr_word_based[subphr_in_words] = p_l_r_dr_word_based.get(subphr_in_words, 0) + 1
                                    first_word_de1 = de1.split()[0]
                                    jump_size = int(first_word_de1)-int(word_de2)
                                    if jump_size == 1:#swap
                                        p_l_r_s_word_based[subphr_in_words]  = p_l_r_s_word_based.get(subphr_in_words, 0)  + 1
                                    elif jump_size > 1:#discontinous
                                        p_l_r_dl_word_based[subphr_in_words] = p_l_r_dl_word_based.get(subphr_in_words, 0) + 1

                            if found_left == 0:
                                if word_en2 == str(int(first_word_en1)-addition_left):#right to left
                                    found_left = 1
                                    first_word_de1 = de1.split()[0]
                                    jump_size = int(first_word_de1)-int(word_de2)
                                    if jump_size == 1:#monotonous
                                        p_r_l_m_word_based[subphr_in_words]  = p_r_l_m_word_based.get(subphr_in_words, 0)  + 1
                                    elif jump_size > 1:#discontinous
                                        p_r_l_dl_word_based[subphr_in_words] = p_r_l_dl_word_based.get(subphr_in_words, 0) + 1
                                    last_word_de1  = de1.split()[-1]
                                    jump_size = int(word_de2)-int(last_word_de1)
                                    if jump_size == 1:#swap
                                        p_r_l_s_word_based[subphr_in_words]  = p_r_l_s_word_based.get(subphr_in_words, 0)  + 1
                                    elif jump_size > 1:#discontinous
                                        p_r_l_dr_word_based[subphr_in_words] = p_r_l_dr_word_based.get(subphr_in_words, 0) + 1

                        if found_left  == 0: addition_left  += 1
                        if found_right == 0: addition_right += 1


    return p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dr_phrase_based, p_l_r_dl_phrase_based,\
        p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dr_phrase_based, p_r_l_dl_phrase_based,\
        p_l_r_m_word_based, p_l_r_s_word_based, p_l_r_dr_word_based, p_l_r_dl_word_based,\
        p_r_l_m_word_based, p_r_l_s_word_based, p_r_l_dr_word_based, p_r_l_dl_word_based

def calculate_probabilities(c_l_r_phrase_based_array, c_r_l_phrase_based_array, c_l_r_word_based_array, c_r_l_word_based_array, list_of_subphrases_dic):
    dictionaries_array = [c_l_r_phrase_based_array, c_r_l_phrase_based_array, c_l_r_word_based_array, c_r_l_word_based_array]

    j=0
    for subphrase in list_of_subphrases_dic:
        if j % 500 == 0:
            print(float(j)/no_of_sentences)
        j += 1
        #print(subphrase)
        [en,de]=subphrase.split(" ^ ")
        if len(en.split()) <= 7 and len(de.split()) <= 7:
            for dic_array in dictionaries_array:
                total_count = 0
                for dic in dic_array:
                    total_count += dic.get(subphrase, 0)
                if total_count > 0:
                    for dic in dic_array:
                        dic[subphrase] = float(dic.get(subphrase, 0))/total_count

    return dictionaries_array

# create count histogram
def count_barchart(dictionaries_array):
    data = []

    print(len(dictionaries_array))
    # now for phrase based
    dict_data = dictionaries_array[0] + dictionaries_array[1]
    # for word based
    dict_data = dictionaries_array[2] + dictionaries_array[3]

    for dic in dict_data:
        data.append(sum(dic.values()))
        print(sum(dic.values()))

    categories = ["p1", "p2", "p3", "p4","p5","p6","p7","p8"]
    no_of_categories = range(len(data))

    plt.bar(no_of_categories, data)
    plt.xticks(no_of_categories, categories)
    plt.show()

# 
def phraselength_orientation(counts_dic):
    monotone_lr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    swap_lr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    discontinuous_l_lr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    discontinuous_r_lr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # monotone_rl = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # swap_rl = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # discontinuous_l_rl = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # discontinuous_r_rl = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]

    orientation_list = [monotone_lr, swap_lr, discontinuous_l_lr, discontinuous_r_lr]
    # monotone_rl, swap_rl, discontinuous_l_rl, discontinuous_r_rl]

    # print(counts_dic)

    for subphrase, counts in counts_dic.items():
        subphrase_split = subphrase.split(" ^ ")
        # for english
        len_subphrase = len(subphrase_split[0].split(" ")) - 1
        if len_subphrase > 6:
            len_subphrase = 6

        # for german
        # len_subphrase = len(subphrase[1].split(" ")) - 1
        monotone_lr[len_subphrase] += counts[0]
        swap_lr[len_subphrase] += counts[1]
        discontinuous_l_lr[len_subphrase] += counts[2]
        discontinuous_r_lr[len_subphrase] += counts[3]
        # monotone_rl[len_subphrase] += counts[4]
        # swap_rl[len_subphrase] += counts[5]
        # discontinuous_l_rl[len_subphrase] += counts[6]
        # discontinuous_r_rl[len_subphrase] += counts[7]

    # print(orientation_list)

    total_counts = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # for each sentence length
    sentence_length = 7
    no_of_classes_compared = 4
    for j in range(sentence_length):
	    for i in range(no_of_classes_compared):
	    	total_counts[j] += orientation_list[i][j]

    # print(total_counts)

    for cl in orientation_list[0:no_of_classes_compared]:
        for i in range(sentence_length):
            cl[i] /= total_counts[i]

    # print(orientation_list)


    N = 7
    # men_means = (20, 35, 30, 35, 27)
    # men_std = (2, 3, 4, 1, 2)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.15       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind-width, monotone_lr, width, color='g')
    rects2 = ax.bar(ind, swap_lr, width, color='r')

    rects3 = ax.bar(ind + width, discontinuous_l_lr, width, color='y')
    rects4 = ax.bar(ind + 2*width, discontinuous_r_lr, width, color='b')


    # add some text for labels, title and axes ticks
    ax.set_ylabel('Frequency')
    ax.set_title('Frequencies of orientations per sentence length')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(('1', '2', '3', '4', '5','6','7'))
    ax.autoscale(tight=True)
    ax.set_ylim((0.0, 1.0))

    
    ax.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('Monotone_lr', 'Swap_lr', 'Discontinous_l_lr', 'Discontinous_r_lr'))

    plt.show()

def read_counts_and_probs():
    counts_dic = {}
    probs_dic = {}

    f = open("counts", 'r')
    lines = f.readlines()
    lines = lines[2:]
    for i, subphrase in enumerate(lines):
        split = subphrase.split(" ||| ")
        split2 = split[-1].split(" ")
        counts = []
        for count in split2:
            counts.append(float(count))
        counts_dic[split[0] + ' ^ ' + split[1]] = counts

    f = open("probabilities", 'r')
    lines = f.readlines()
    lines = lines[2:]
    for i, subphrase in enumerate(lines):
        split = subphrase.split(" ||| ")
        split2 = split[-1].split(" ")
        probs = []
        for prob in split2:
            probs.append(float(prob))
        probs_dic[split[0] + ' ^ ' + split[1]] = probs

    return counts_dic, probs_dic

if __name__ == '__main__':
<<<<<<< HEAD
    sentence_start  = 0#0
    no_of_sentences = 50000#50000
=======
    sentence_start  = 5
    no_of_sentences = 300
>>>>>>> 18a721aa9be69e3d60510229091ae7f432274435
    no_of_sentences = no_of_sentences+sentence_start

    e = open("en.txt", 'r')
    d = open("de.txt", 'r')
    a = open("aligned.txt", 'r')
    en_txt = e.readlines()
    de_txt = d.readlines()
    alignments = a.readlines()
    '''
    subphrases_dic, list_of_subphrases_dic = create_dicts(en_txt,de_txt,alignments, no_of_sentences, sentence_start)

    with open('subphrases_dic.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(subphrases_dic, f)

    with open('list_of_subphrases_dic.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(list_of_subphrases_dic, f)'''

    print('Loading subphrases_dic...')
    subphrases_dic = {}
    with open('subphrases_dic.pickle', 'rb') as f:
        subphrases_dic = pickle.load(f)

    print('subphrases_dic loaded. Loading list_of_subphrases_dic...')
    list_of_subphrases_dic = {}
    with open('list_of_subphrases_dic.pickle', 'rb') as f:
        list_of_subphrases_dic = pickle.load(f)

    print('list_of_subphrases_dic loaded. Counting reorderings...')

    # counts, probs = read_counts_and_probs()
    # print(counts)

    #NOTE: we probably dont even need aligns_dic
    #rint subphrases_dic
    #print aligns_dic
    #print alignments[sentence_start:no_of_sentences]
    
    p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dr_phrase_based, p_l_r_dl_phrase_based,\
    p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dr_phrase_based, p_r_l_dl_phrase_based,\
    p_l_r_m_word_based, p_l_r_s_word_based, p_l_r_dr_word_based, p_l_r_dl_word_based,\
    p_r_l_m_word_based, p_r_l_s_word_based, p_r_l_dr_word_based, p_r_l_dl_word_based =\
    count_reorderings(en_txt[sentence_start:no_of_sentences], de_txt[sentence_start:no_of_sentences], subphrases_dic, alignments[sentence_start:no_of_sentences])
    
    print('Counted reorderings. Calculating probabilities...')
    # write to output file
    # f = open("counts", "w")

    # f.write("f ||| e ||| p1 p2 p3 p4 p5 p6 p7 p8\n\n")

    # for subphrase in list_of_subphrases_dic:
    #     e,d = subphrase.split(" ^ ")
    #     f.write(d + " ||| " + e + " |||")

    #     for dic_array in dictionaries_array:
    #         for dic in dic_array:
    #             f.write(" " + str(dic.get(subphrase,0.0)))

    #     f.write("\n")

    count_barchart(dictionaries_array)

    # phraselength_orientation(counts)


    [[p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dl_phrase_based, p_l_r_dr_phrase_based],\
    [p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dl_phrase_based, p_r_l_dr_phrase_based],\
    [p_l_r_m_word_based, p_l_r_s_word_based, p_l_r_dl_word_based, p_l_r_dr_word_based],\
    [p_r_l_m_word_based, p_r_l_s_word_based, p_r_l_dl_word_based, p_r_l_dr_word_based]]=\
    calculate_probabilities([p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dl_phrase_based, p_l_r_dr_phrase_based],\
    [p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dl_phrase_based, p_r_l_dr_phrase_based],\
    [p_l_r_m_word_based, p_l_r_s_word_based, p_l_r_dl_word_based, p_l_r_dr_word_based],\
    [p_r_l_m_word_based, p_r_l_s_word_based, p_r_l_dl_word_based, p_r_l_dr_word_based], list_of_subphrases_dic)

    print('Probabilities calculated.')

    # print('-----------------p_l_r_m_phrase_based-----------------')
    # print(p_l_r_m_phrase_based)
    # print('-----------------p_l_r_s_phrase_based-----------------')
    # print(p_l_r_s_phrase_based)
    # print('-----------------p_l_r_dr_phrase_based-----------------')
    # print(p_l_r_dr_phrase_based)
    # print('-----------------p_l_r_dl_phrase_based-----------------')
    # print(p_l_r_dl_phrase_based)
    # print('-----------------p_r_l_m_phrase_based-----------------')
    # print(p_r_l_m_phrase_based)
    # print('-----------------p_r_l_s_phrase_based-----------------')
    # print(p_r_l_s_phrase_based)
    # print('-----------------p_r_l_dr_phrase_based-----------------')
    # print(p_r_l_dr_phrase_based)
    # print('-----------------p_r_l_dl_phrase_based-----------------')
    # print(p_r_l_dl_phrase_based)

    # print('-----------------p_l_r_m_word_based-----------------')
    # print(p_l_r_m_word_based)
    # print('-----------------p_l_r_s_word_based-----------------')
    # print(p_l_r_s_word_based)
    # print('-----------------p_l_r_dr_word_based-----------------')
    # print(p_l_r_dr_word_based)
    # print('-----------------p_l_r_dl_word_based-----------------')
    # print(p_l_r_dl_word_based)
    # print('-----------------p_r_l_m_word_based-----------------')
    # print(p_r_l_m_word_based)
    # print('-----------------p_r_l_s_word_based-----------------')
    # print(p_r_l_s_word_based)
    # print('-----------------p_r_l_dr_word_based-----------------')
    # print(p_r_l_dr_word_based)
    # print('-----------------p_r_l_dl_word_based-----------------')
    # print(p_r_l_dl_word_based)


    dictionaries_array_phrase_based = [[p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dl_phrase_based, p_l_r_dr_phrase_based],\
    [p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dl_phrase_based, p_r_l_dr_phrase_based]]
    dictionaries_array_word_based   = [[p_l_r_m_word_based, p_l_r_s_word_based, p_l_r_dl_word_based, p_l_r_dr_word_based],\
    [p_r_l_m_word_based, p_r_l_s_word_based, p_r_l_dl_word_based, p_r_l_dr_word_based]]

    # write to phrase based output file
    f_pb = open("results_phrase_based.txt", "w")
    f_wb = open("results_word_based.txt", "w")

    f_pb.write("f ||| e ||| p1 p2 p3 p4 p5 p6 p7 p8\n\n")
    f_wb.write("f ||| e ||| p1 p2 p3 p4 p5 p6 p7 p8\n\n")

    for subphrases in list_of_subphrases_dic:
        e,d = subphrases.split(" ^ ")
        if len(e.split()) <= 7 and len(d.split()) <= 7:

            f_pb.write(d + " ||| " + e + " |||")
            f_wb.write(d + " ||| " + e + " |||")

            for dic_array in dictionaries_array_phrase_based:
                for dic in dic_array:
                    f_pb.write(" " + str(dic.get(subphrases,0.0)))

            for dic_array in dictionaries_array_word_based:
                for dic in dic_array:
                    f_wb.write(" " + str(dic.get(subphrases,0.0)))

            f_pb.write("\n")
            f_wb.write("\n")


    with open('dictionaries_array_phrase_based.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(dictionaries_array_phrase_based, f)

    with open('dictionaries_array_word_based.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(dictionaries_array_word_based, f)
