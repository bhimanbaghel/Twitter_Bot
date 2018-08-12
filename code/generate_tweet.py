import pysolr
from random import randint
from random import shuffle
from nltk.tag.stanford import StanfordPOSTagger as POSTagger
from nltk.internals import find_file, find_jar, config_java, java, _java_options
config_java(options='-xmx2G')


# These rules all independent, order of
# escaping doesn't matter
escapeRules = {'+': r'\+',
               '-': r'\-',
               '&': r'\&',
               '|': r'\|',
               '!': r'\!',
               '(': r'\(',
               ')': r'\)',
               '{': r'\{',
               '}': r'\}',
               '[': r'\[',
               ']': r'\]',
               '^': r'\^',
               '~': r'\~',
               '*': r'\*',
               '?': r'\?',
               ':': r'\:',
               '"': r'\"',
               ';': r'\;',
               ' ': r'\ '}

def escapedSeq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escapeRules.keys():
            yield escapeRules[char]
        else:
            yield char

def escapeSolrArg(term):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = term.replace('\\', r'\\')   # escape \ first
    return "".join([nextStr for nextStr in escapedSeq(term)])


def search_next_words(keyword, solr, template, english_postagger):
	next_str = ""
	r_list = []
	if len(template)==0:
		return ''
	# print "next"
	# print template
	# print template
	for i in range(len(template)):
		found_flag = 0
		search_key = "first:"+str(escapeSolrArg(keyword) )
		results = solr.search(search_key, rows=50, sort="count desc")
		# results = [x['first'] for x in results ]
		# results_tag = english_postagger.tag(results)
		for result in results:
			r_tag = english_postagger.tag([result['second']])
			# print r_tag
			r_tag = r_tag[0][1]

			if r_tag == template[i]:
				keyword = result['second']
				# keyword = r_val
				# print keyword
				found_flag =1
				break
		if(found_flag==0):
			return "NILL"
			# r_list.append(result['second'])
		# random_num = randint(0,len(r_list)-1)
		# keyword = r_list[random_num]
		next_str += keyword + " "
	if len(next_str) == 0:
		return "NILL"
	else:
		return next_str

def search_prev_words(keyword, solr, template, english_postagger):
	prev_list = []
	r_list = []
	if len(template)==0:
		return ''
	# print "prev"
	# print template
	for i in xrange(len(template)-1, -1, -1):
		found_flag = 0
		search_key = "second:"+str(escapeSolrArg(keyword) )
		results = solr.search(search_key, rows=50, sort="count desc")
		#results = [x['first'] for x in results ]
		#results_tag = english_postagger.tag(results)
		# print results_tag
		for result in results:
			
			r_tag = english_postagger.tag([result['first']])
			# print r_tag
			r_tag = r_tag[0][1]

			# r_list.append(result['first'])
			if r_tag == template[i]:
				keyword = result['first']
				# keyword = r_val
				# print keyword
				found_flag =1
				break
		if(found_flag==0):
			return "NILL"
		# random_num = randint(0,len(r_list)-1)
		# keyword = r_list[random_num]
		prev_list.append(keyword)
	prev_list.reverse()
	if le(prev_list) == 0:
		return "NILL"
	else:
		return " ".join(prev_list)

def search_middel_words(first_word, last_word, solr, template, english_postagger):
	middel_str = ""
	middel_str += first_word
	keyword = first_word
	for i in range(len(template)):
		found_flag = 0
		search_key = "first:"+str(escapeSolrArg(keyword) )
		results = solr.search(search_key, rows=50, sort="count desc")
		for result in results:
			r_tag = english_postagger.tag([result['second']])
			r_tag = r_tag[0][1]

			if r_tag == template[i]:
				if i == (len(template) -1):
					search_key = "first:"+str(escapeSolrArg(result['second']))
					temp_results = solr.search(search_key, rows=100, sort="count desc")
					temp_results = [x['second'] for x in temp_results]
					if last_word in temp_results:
						keyword = result['second']
						found_flag = 1
						break
				else:
					keyword = result['second']
					found_flag =1
					break
		if(found_flag==0):
			return "NILL"
		middel_str += keyword + " "
	middel_str = middel_str + " " + last_word
	return middel_str

def load_grammar():
	grammar_file = open("../data/good_lines_tags.txt", "r")
	lines = grammar_file.readlines();
	grammar_file.close()
	tag_list = []
	for line in lines:
		# tag_line = []
		tag_list.append(line.split('\n')[0].split(' '))
		# tag_list.append(tag_line)
	for tag in tag_list:
		if len(tag) < 1:
			tag_list.remove(tag)
	return tag_list

def main():
	solr = pysolr.Solr('http://localhost:8983/solr/unicore', timeout=10)
	english_postagger = POSTagger('../postagger/models/english-bidirectional-distsim.tagger', '../postagger/stanford-postagger.jar')
	grammar_template = load_grammar()
	#print grammar_template
	print "Grammar Template Loaded"
	generated_sentence_list = []
	keyword = raw_input("Enter any word : ")
	keyword = keyword.lower()
	# print keyword
	keyword = keyword.split("\n")[0]
	keyword = keyword.split(" ")
	print keyword
	
	key_tag = english_postagger.tag(keyword)
	for i in range(len(key_tag)):
		key_tag[i] = key_tag[i][1]
	print key_tag

	t_count =0 
	shuffle(grammar_template)
	for template in grammar_template:
		print "template", t_count
		t_count +=1 
		key_index_low = key_index_high = 0
		found_flag = 0
		if len(key_tag) == 1:
			if key_tag[0] in template:
				key_index_low = key_index_high = template.index(key_tag[0])
			else:
				continue
		else:
			for i in range(len(template)-2):
				if key_tag[0] == template[i] and key_tag[2] == template[i+2]:
					found_flag = 1
					key_index_low = i
					key_index_high = i+2
					break
			if not found_flag:
				continue

		print key_index_low, key_index_high
		
		prev_words = search_prev_words(keyword[0], solr, template[0:key_index_low], english_postagger)
		# if(prev_words == "NILL"):
		# 	continue
		next_words = search_next_words(keyword[-1], solr, template[key_index_high+1:len(template)], english_postagger)
		# if(next_words == "NILL"):
		# 	continue
		# print prev_words + " " + " ".join(keyword) + " " + next_words
		# break
		if prev_words == "NILL" and next_words == "NILL":
			continue
		if prev_words == "NILL":
			prev_words = ''
		if next_words == "NILL":
			next_words = ''
		print prev_words + " " + " ".join(keyword) + " " + next_words
		generated_sentence_list.append(prev_words + " " + " ".join(keyword) + " " + next_words)
	t_count =0
	for template in grammar_template:
		print "template", t_count
		t_count +=1
		key_index_low = key_index_high = 0
		if len(key_tag) == 1:
			break;
		else:
			if key_tag[0] in template:
				key_index_low = template.index(key_tag[0])
				if key_tag[-1] in template[key_index_low+1:]:
					key_index_high = template[key_index_low+1:].index(key_tag[-1])
				else:
					continue
			else:
				continue
			prev_words = search_prev_words(keyword[0], solr, template[0:key_index_low], english_postagger)
			
			middel_words = search_middel_words(keyword[0], keyword[-1], solr, template[key_index_low+1: key_index_high], english_postagger)
			if(middel_words == "NILL"):
				middel_words = keyword[1];
			next_words = search_next_words(keyword[-1], solr, template[key_index_high+1:len(template)], english_postagger)
			if(prev_words == "NILL" and next_words == "NILL" and middel_words == keyword[1]):
				continue
			if prev_words == "NILL" and next_words == "NILL":
				continue
			if prev_words == "NILL":
				prev_words = ''
			if next_words == "NILL":
				next_words = ''
			print prev_words + " " + middel_words + " " + next_words
			generated_sentence_list.append(prev_words + " " + middel_words + " " +next_words)	

	for sentence in generated_sentence_list:
		print sentence

if __name__ == '__main__':
	main()