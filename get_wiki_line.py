#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Attempt to retrieve wikipedia article based on command line argument (topic) passed to this script using requests module. 
If found, return the first line of the article with markup and any reference numbers removed. 
Remove parenthetical notes (e.g., translations) and replace with ellipses, and include parenthesized reference at the end. 
Detect whether a 'disambiguation page' is reached, or no result is found. 
Print result to screen and copy to clipboard. 

Usage:
	
	python get_wiki_line.py black
	
	Print and copy to clipboard: 
	Black is the darkest color, resulting from the absence or complete absorption of light ( https://en.wikipedia.org/wiki/black ).
			
'''
import requests
import sys
import html_parser as hp
import re
import subprocess as sp

def main():

	if len(sys.argv) < 2:
		print 'need file to look up'
		sys.exit()
		
	wiki_file = sys.argv[1]
	url = 'https://en.wikipedia.org/wiki/%s'%wiki_file

	r=requests.get(url=url)
	doc = r.text

	tree = hp.parse(doc)
	
	def rm_markup(text):
		return re.sub('<.*?>','',text)
	
	if 'may refer to' in tree.node_dict['p'][0].content:
		print 'Got disambiguation page: %s' %url
		sys.exit()
	
	if 'Other reasons this message may be displayed:' in tree.node_dict['p'][0].content:
		print 'No page was found for url: %s' %url
		sys.exit()
	
	for i in tree.node_dict['p']:	#iterate through 'p' tags until finding first formal paragraph of article
		check_p = rm_markup(i.content)
		if wiki_file.lower() in check_p[:len(wiki_file)+10].lower():
			markup_removed = check_p 
			break
	
	after_wiki_file = markup_removed[re.search(wiki_file.lower(),markup_removed.lower()).pos+len(wiki_file):]
	
	if '(' in after_wiki_file[:3]:	#pseudo stack to find total enclosing parentheses (if present, possibly nested) in first line; remove and replace with '...'
		parentheses_present = False
		count = 0
		start_pos = None
		for i in xrange(len(markup_removed)):
			if markup_removed[i] == '(':
				count+=1
				if parentheses_present == False:
					start_pos = i
					parentheses_present = True
			if markup_removed[i] == ')':
				count -=1
			if count == 0 and parentheses_present == True:
				end_pos = i
				break
				
		parentheses_removed = re.sub('\ \ +',' ',markup_removed[:start_pos-1]+'... '+markup_removed[end_pos+1:])
		markup_removed = parentheses_removed
	
	markup_removed = re.sub('\[.+?\]','',markup_removed.replace('&#160;',' '))	#replace "non-breaking spaces" and bracketed reference numbers
	
	first_sentence = re.search('.*?\w\.[^\.]',markup_removed).group().strip()[:-1]	#extract first sentence by single period (omit ellipses)

	first_sentence_w_ref = first_sentence + ' ( %s ).' %url
	
	print first_sentence_w_ref
	
	cmd = 'echo \'%s\' | pbcopy' %first_sentence_w_ref
	sp.Popen(cmd,shell=True)
	
	
if __name__ == '__main__':
	main()