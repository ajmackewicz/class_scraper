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


'''
Fill list of self.class_schedules
'''
class Scraper:
	def __init__(self, term, courseID, semester, subject, number):
		self.class_schedules = []

		self.subject = subject
		self.number = number
		self.id = self.subject + self.number
		
		self.url = "https://apps.lbcc.edu/schedule/scheduleDetail.cfm?term=" + term + "&courseID=" + courseID + "&semester=" + semester + "&subject=" + subject + "&catalog_nbr=" + number
		self.session = HTMLSession()
		self.response = self.session.get(self.url)

		self.entries = [entry.text
			for entry in self.response.html.find("td.scheduletext")] # Entries
		self.class_numbers = [number.text
			for number in self.response.html.find("a[href*='javascript:void(0);']")] # Class Numbers

	def get_id(self):
		return self.id
	'''
	Permit discarding the row if
	- the previous entry was a class number and current entry is 'WEB';
	- the current entry is 'CLOSED'.
	Do not allow discarding if there is a WEB component to a class.
	'''
	def to_discard_row(self, i):
		return (
			self.entries[i - 1] in self.class_numbers and self.entries[i] == 'WEB'
			) or (
			self.entries[i] == 'CLOSED'
			)

	'''
	Permit discarding entry if
	- the entry is blank; 
	- the entry is 'CLOSED'.
	'''
	def to_discard_entry(self, entry):
		return (entry == '') or (entry == 'CLOSED')

	'''
	Order entries into sections and
	Add sections of classes to list of classes.
	'''
	def process(self):
		class_sched = [] # Sublist to add each class by class number
		i = 0 # Index for entry

		while i < len(self.entries): # All table entries
			entry = self.entries[i] # Iterator for entries

			if not self.to_discard_row(i):
				if not self.to_discard_entry(entry):
					class_sched.append(entry)
					print(" Appending to class_sched: " + entry)
			else: # if to_discard_row == true
				print(" Deleting row.")
				class_sched.clear() # Clear all entries from sublist, all entries from class number

				# Find next entry that is a class number and restart the list
				while (entry not in self.class_numbers) and (i < len(self.entries)):
					i = i + 1
					if i < len(self.entries):
						entry = self.entries[i]
				continue

			try:
				if self.entries[i + 1] in self.class_numbers:
					self.class_schedules.append(class_sched.copy())

					print("Class sched: ")
					print(class_sched)
					print("Class schedules: ")
					print(self.class_schedules)

					class_sched.clear() # Start with fresh sublist
			except IndexError:
				self.class_schedules.append(class_sched.copy())
				break;

			i = i + 1

	def get_class_schedules(self):
		return self.class_schedules


"""
Count
	Online vs. in-person classes
	Late-starting vs. full-semester classes

Order by time frame
	1. M W || M
	2. T || T Th
	3. W
	4. Th
	5. F
	6. S

Order then by times of day

Create list of coalesced, ordered times

Create list of combinations of schedules
"""


'''
Precondition: A dictionary with keys the class subject + class number
		and values lists of the class's sections
Postcondition: A dictionary with sorted sections by start time
		(and perhaps a list with sorted classes by start time)
'''
class Processor:
	def __init__(self, class_dict):
		# Variables for the non-conflicting class combinations
		self.numb_online = 0
		self.numb_inperson = 0
		self.class_dict = class_dict
		self.class_keys = list(class_dict.keys())
		self.class_combos = []

	'''
	def count_numb_online(self, key):
		for class_listing in self.class_dict[key]:
	'''
	def get_numb_online(self):
		return self.numb_online
	
	def get_numb_inperson(self):
		return self.numb_inperson

	def get_class_combos(self):
		return self.class_combos

	def get_times(self, string):
		string = string.replace(" ", "")
		string = string.replace(":", "")
		str_times = string.split("-")
		
		times = []
		for str_time in str_times:
			if str_time[:2] == "12":
				print("str_time begins with 12")
				if str_time[-2:] == "AM":
					times.append(int(str_time.replace("AM", "")) - 1200)
				elif str_time[-2:] == "PM":
					times.append(int(str_time.replace("PM", "")))
			elif (str_time[-2:] == "AM"):
				times.append(int(str_time.replace("AM", "")))
			elif str_time[-2:] == "PM":
				times.append(int(str_time.replace("PM", "")) + 1200)
		return times 
	
	def minimum(self, int_list):
		min_i = 0
		minimum = int_list[0]
	
		for i in range(1, len(int_list)):
			if int_list[i] < minimum:
				minimum = int_list[i]
				min_i = i
		return minimum, min_i
	
	"""
	Order sections of a class list by times
	"""
	def order_sections(self, sections):
		sections_ordered = []
		sections_times = [self.get_times(section[2])[0] for section in sections]
	
		i = 0
		while i < len(sections):
			print(sections)
			print(sections_times)
			print()

			min_time, min_i = self.minimum(sections_times[i:])
			min_i = min_i + i
			min_section = sections[min_i]
			print("Assigned min_time, min_i: " + str(min_time) + ", " + str(min_i))
			# Reorder sections_times
			sections_times[min_i] = sections_times[i]
			sections_times[i] = min_time
			# Reorder sections
			sections[min_i] = sections[i]
			sections[i] = min_section

			sections_ordered.append(sections[i])
			i = i + 1

		return sections_ordered

	def order_classes(self):
		for key in self.class_keys:
			self.class_dict[key] = self.order_sections(self.class_dict[key])

	# def merge_classes(self):	
		'''
		Find smaller list in dict.
		Use the smaller list to be merged with the larger into another list
			- Group the sections in one subject list into equivalent times
				- if the start times of sections from larger_list
					are within the times of two start times of smaller_list
				- then append the sandwich to a merged_list

		'''
	# def calc_class_combos(self):

		

# MAIN
class Initializer:
	def __init__(self):
		print("Enter the term number, course ID, semester (spring/fall), subject, and class number.")
		self.term = input("term number: ")
		self.courseID = input("course ID: ")
		self.semester = input("semester (spring/fall): ")
		self.subject = input("subject: ")
		self.number = input("number: ")

	def initial(self):
		return Scraper(self.term, self.courseID, self.semester.upper(), self.subject.upper(), self.number.upper())


# ACCTG 1A
s1 = Scraper("1695", "002181", "SPRING", "ACCTG", "1A")

# CS 11
# s2 = Scraper("1695", "002669", "SPRING", "CS", "11")

# ENGL 1
s2 = Scraper("1695", "000643", "SPRING", "ENGL", "1")

scrapers = [s1, s2]
class_dict = {} # dictionary to be passed to Processor object
for scraper in scrapers:
	scraper.process()
	class_dict[scraper.get_id()] = scraper.get_class_schedules()

for key in class_dict.keys():
	print(key)
	print(class_dict[key])

processor = Processor(class_dict)
processor.order_classes()

print(class_dict)
