"""
Many modern web applications are designed to provide their
functionality in collaboration with the clients’ browsers.
Instead of sending HTML pages, these apps send JavaScript
code that instructs your browser to create the desired HTML.
Web apps deliver dynamic content in this way to offload work
from the server to the clients’ machines as well as to avoid
page reloads and improve the overall user experience.
"""

import requests_html
from requests_html import HTMLSession

class_schedules = []

class Scraper:
	# self.url = "https://apps.lbcc.edu/schedule/scheduleDetail.cfm?term=1695&courseID=002181&semester=SPRING&subject=ACCTG&catalog_nbr=1A"

	def __init__(self, term, courseID, semester, subject, number):
		self.url = "https://apps.lbcc.edu/schedule/scheduleDetail.cfm?term=" + term + "&courseID=" + courseID + "&semester=" + semester + "&subject=" + subject + "&catalog_nbr=" + number
		self.session = HTMLSession()
		self.response = self.session.get(self.url)
		self.class_elements = self.response.html.find("td.scheduletext") 

	def tester(self):
		print(self.url)

	def process(self):
		class_sched = []

		for class_element in self.class_elements: # for all text elements scraped, i.e., each table entry
			if class_element.text == "": # if it is an empty string
				continue; # go to next text element
			else:
				print(class_element.text)
				# Return or define the list of schedules, containing
				# 	class number,
				# 	class days,
				# 	class times, 
				# 	class professor
				# Ignore classes with days = WEB
				if not class_element.text.replace(" ", "").isnumeric(): # if it is not a number
					class_sched.append(class_element.text)
					print(" In appending to class_sched: " + class_element.text)
				else:
					print( "In appending to class_sched: ")
					class_sched.append(class_element.text) # Update sublist
					print("Class sched: ")
					print(class_sched)

					class_schedules.append(class_sched.copy())
					print("Class schedules: ")
					print(class_schedules)
					class_sched.clear() # Start with fresh sublist

# class Processor:
	# def __init__(self):

# MAIN
s = Scraper("1695", "002181", "SPRING", "ACCTG", "1A")
s.tester()
s.process()
print("Class schedule: ")
print(class_schedules)
