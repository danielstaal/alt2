import random
from copy import deepcopy

# phrase_extraction('resumption of the session', 'wiederaufnahme der sitzungsperiode', [[0,0], [1,1], [1,2], [2,3]])

# resumption of the session
# wiederaufnahme der sitzungsperiode
# 0-0 1-1 1-2 2-3

# alignments = [[0,0], [1,1], [1,2], [2,3]]
def phrase_extraction(sen1, sen2, alignments, en_sub_phrases, de_sub_phrases):
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
					# make sure the longest subphrase is 5 words
					if len(en_poss.split()) <= 5 and len(de_poss.split()) <= 5:
						aux_en_strings = reorder_string(en_poss)
						aux_de_strings = reorder_string(de_poss)
						if check_continuity(aux_en_strings, aux_de_strings):
							aux_en_strings = translate_numbers_to_words(aux_en_strings, sen1_words)
							aux_de_strings = translate_numbers_to_words(aux_de_strings, sen2_words)
							aux_en_strings = aux_en_strings[:-1]
							aux_de_strings = aux_de_strings[:-1]
							en_sub_phrases[aux_en_strings] = en_sub_phrases.get(aux_en_strings, 0) + 1
							de_sub_phrases[aux_de_strings] = de_sub_phrases.get(aux_de_strings, 0) + 1
							if aux_en_strings + ' ^ ' + aux_de_strings not in aligned_sub_phrases:
								aligned_sub_phrases.append(aux_en_strings + ' ^ ' + aux_de_strings)
								seg_aligned_sub_phrases.append(translate_numbers_to_words_aligned(aligned_words, sen1_words, sen2_words))

	return en_sub_phrases, de_sub_phrases, aligned_sub_phrases, seg_aligned_sub_phrases


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

def create_dicts(en_txt,de_txt,alignments, no_of_sentences=50000):
	en_dic = {}
	de_dic = {}
	en_de_dic = {}
	aligns_dic = {}
	# KMO dictionaries
	count_ef = {}# count of appeareances of single words aligned to other language words
	we = {}# appearance of single words (english)
	wf = {}# appearance of single words (deutsch)
	# assignment 2: dictionary['sentence']=[[subphrases]]
	subphrases_dic = {}

	j = 0
	k = 0

	for en_sen, de_sen, alignment in zip(en_txt[:no_of_sentences], de_txt[:no_of_sentences], alignments[:no_of_sentences]):	
		if j % 100 == 0:
			print(float(j)/len(en_txt))
		j += 1

		# alignments = [[0,0], [1,1], [1,2], [2,3]]
		alignment = alignment.split()#.split('-')
		for i, el in enumerate(alignment):
			alignment[i] = el.split('-')
		en_dic, de_dic, aligned_sub_phrases, seg_aligned_sub_phrases = phrase_extraction(en_sen[:-1], de_sen[:-1], alignment, en_dic, de_dic)
		
		for al, alignments in zip(aligned_sub_phrases, seg_aligned_sub_phrases):
			if al in en_de_dic:
				en_de_dic["".join(al)] += 1
			else:
				en_de_dic["".join(al)] = 1
				# Stores alignments of the sub_phrase. Used in lexical_translation_probabilities(). Example:
				# aligns_dic["session of the ^ sitzungsperiode des"] = [['sitzungsperiode', 'session'], ['des', 'of the']]
				aligns_dic["".join(al)] = alignments

		subphrases_dic[en_sen[:-1]] = aligned_sub_phrases;


	# fill KMO dictionaries
	for pairs,counts in en_de_dic.items():
		[en,de] = pairs.split(" ^ ")
		en_split = en.split()
		de_split = de.split()
		for en_word in en_split:
			for de_word in de_split:
				ende = en_word + ' ' + de_word
				count_ef[ende] = count_ef.get(ende, 0) + 1
		for en_word in en_split:
			we[en_word] = we.get(en_word, 0) + 1
		for de_word in de_split:
			wf[de_word] = wf.get(de_word, 0) + 1

	return en_dic,de_dic,en_de_dic,aligns_dic,count_ef,we,wf,subphrases_dic


# assuming subphrases_dic['sentence'] = [['e_sub_1 ^ f_sub_1'], ['e_sub_2 ^ f_sub_2'], ['e_sub_3 ^ f_sub_3']]
def count_reorderings(sentences, subphrases_dic):
	p_l_r_m  = {}
	p_l_r_s  = {}
	p_l_r_dl = {}
	p_l_r_dr = {}
	p_r_l_m  = {}
	p_r_l_s  = {}
	p_r_l_dl = {}
	p_r_l_dr = {}
	for sent in sentences:
		# left to right




if __name__ == '__main__':

    e = open("en.txt", 'r')
    d = open("de.txt", 'r')
    a = open("aligned.txt", 'r')
    en_txt = e.readlines()
    de_txt = d.readlines()
    alignments = a.readlines()