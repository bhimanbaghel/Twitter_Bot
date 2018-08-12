import random
import subprocess
import nltk
from nltk.tag.stanford import StanfordPOSTagger as POSTagger
from nltk.internals import find_file, find_jar, config_java, java, _java_options
config_java(options='-xmx1G')

def main():
	data_file = open("../data/good_data.txt","r")
	out_file = open("../data/good_lines_tags_1.txt", "w")
	lines = data_file.readlines();
	data_file.close();
	line_count = 0
	english_postagger = POSTagger('../postagger/models/english-bidirectional-distsim.tagger', '../postagger/stanford-postagger.jar')
	for line in lines:
		tag_list = []
		for t in english_postagger.tag(line.split('\n')[0].split(' ')):
			tag_list.append(t[1])
		out_file.write(" ".join(tag_list))
		out_file.write("\n")
		print "completed line" + str(line_count)
		line_count +=1
	out_file.close();

if __name__ == '__main__':
	main()