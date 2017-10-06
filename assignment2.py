import random
from copy import deepcopy

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
					words_without_alignments[language_index	].append(word_as_num)


	len_smallest_seg = len(smallest_seg)
	aligned_sub_phrases = []
	seg_aligned_sub_phrases = []
	
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
					#if len(en_poss.split()) <= 7 and len(de_poss.split()) <= 7:
					aux_en_strings = reorder_string(en_poss)
					aux_de_strings = reorder_string(de_poss)
					if check_continuity(aux_en_strings, aux_de_strings):
						#aux_en_strings = translate_numbers_to_words(aux_en_strings, sen1_words)
						#aux_de_strings = translate_numbers_to_words(aux_de_strings, sen2_words)
						aux_en_strings = aux_en_strings[:-1]
						aux_de_strings = aux_de_strings[:-1]
						#en_sub_phrases[aux_en_strings] = en_sub_phrases.get(aux_en_strings, 0) + 1
						#de_sub_phrases[aux_de_strings] = de_sub_phrases.get(aux_de_strings, 0) + 1
						if aux_en_strings + ' ^ ' + aux_de_strings not in aligned_sub_phrases:
							aligned_sub_phrases.append(aux_en_strings + ' ^ ' + aux_de_strings)
							#seg_aligned_sub_phrases.append(translate_numbers_to_words_aligned(aligned_words, sen1_words, sen2_words))

	return aligned_sub_phrases


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
		
		aligned_sub_phrases = phrase_extraction(en_sen[:-1], de_sen[:-1], alignment)#, en_dic, de_dic)

		subphrases_dic[en_sen[:-1]] = aligned_sub_phrases;

	return subphrases_dic


# assuming subphrases_dic['sentence (in english)'] = [['e_sub_1 ^ f_sub_1'], ['e_sub_2 ^ f_sub_2'], ['e_sub_3 ^ f_sub_3']]
# 												   = [['0 1 2 ^ 2 3 4'],...]
def count_reorderings(en_sentences, de_sentences, subphrases_dic):
	# is this the phrase model?
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
	for en_sen, de_sen in zip(en_sentences, de_sentences):
		#
		subphrases = subphrases_dic[en_sen[:-1]]
		#sent_split = sent.split()
		for s_id, subphr in enumerate(subphrases):
			[en1, de1] = subphr.split(" ^ ")
			if len(en1.split()) <= 7 and len(de1.split()) <= 7:
					subphr_in_words = translate_numbers_to_words(en1, en_sen.split()) + " ^ " + translate_numbers_to_words(de1, de_sen.split())
					subphr_in_words = subphr
					last_word_en1  = en1.split()[-1]
					first_word_en1 = en1.split()[0]

					'''if w_id != len(sent_split):#left to right
						if int(last_word_en) == w_id:'''
					for s_id2 in range(len(subphrases)):#not assuming its in order
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

	return p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dr_phrase_based, p_l_r_dl_phrase_based,\
		p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dr_phrase_based, p_r_l_dl_phrase_based

if __name__ == '__main__':

    sentence_start  = 5#0
    no_of_sentences = 1#50000
    no_of_sentences = no_of_sentences+sentence_start

    e = open("en.txt", 'r')
    d = open("de.txt", 'r')
    a = open("aligned.txt", 'r')
    en_txt = e.readlines()
    de_txt = d.readlines()
    alignments = a.readlines()

    subphrases_dic = create_dicts(en_txt,de_txt,alignments, no_of_sentences, sentence_start)

    #print subphrases_dic

    p_l_r_m_phrase_based, p_l_r_s_phrase_based, p_l_r_dr_phrase_based, p_l_r_dl_phrase_based,\
    p_r_l_m_phrase_based, p_r_l_s_phrase_based, p_r_l_dr_phrase_based, p_r_l_dl_phrase_based =\
    count_reorderings(en_txt[sentence_start:no_of_sentences], de_txt[sentence_start:no_of_sentences], subphrases_dic)

    print 'p_l_r_m_phrase_based'
    print p_l_r_m_phrase_based
    print 'p_l_r_s_phrase_based'
    print p_l_r_s_phrase_based
    print 'p_l_r_dr_phrase_based'
    print p_l_r_dr_phrase_based
    print 'p_l_r_dl_phrase_based'
    print p_l_r_dl_phrase_based
    print 'p_r_l_m_phrase_based'
    print p_r_l_m_phrase_based
    print 'p_r_l_s_phrase_based'
    print p_r_l_s_phrase_based
    print 'p_r_l_dr_phrase_based'
    print p_r_l_dr_phrase_based
    print 'p_r_l_dl_phrase_based'
    print p_r_l_dl_phrase_based