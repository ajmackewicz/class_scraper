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
from collections import defaultdict


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

		self.process()

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
			else: # if to_discard_row == true
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

					class_sched.clear() # Start with fresh sublist
			except IndexError:
				self.class_schedules.append(class_sched.copy())
				break;

			i = i + 1

	def get_class_schedules(self):
		return self.class_schedules


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
		self.subjects = list(class_dict.keys())
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

	def get_times(self, section):
		string = section[2]

		string = string.replace(" ", "")
		string = string.replace(":", "")
		str_times = string.split("-")
		
		times = []
		for str_time in str_times:
			if str_time[:2] == "12":
				if str_time[-2:] == "AM":
					times.append(int(str_time.replace("AM", "")) - 1200)
				elif str_time[-2:] == "PM":
					times.append(int(str_time.replace("PM", "")))
			elif (str_time[-2:] == "AM"):
				times.append(int(str_time.replace("AM", "")))
			elif str_time[-2:] == "PM":
				times.append(int(str_time.replace("PM", "")) + 1200)
		return times 

	def get_start_time(self, section):
		return self.get_times(section)[0]
	
	def get_end_time(self, section):
		return self.get_times(section)[1]
	
	def minimum_and_index(self, int_list):
		min_i = 0
		minimum = int_list[0]
	
		for i in range(1, len(int_list)):
			if int_list[i] < minimum:
				minimum = int_list[i]
				min_i = i
		return minimum, min_i
	
	"""
	Precondition:
		A list of a class's sections
	Postcondition:
		Return a dictionary of sections whose keys are the day of week
	"""
	def order_by_day(self, sections):
		sections_by_day = defaultdict(list)
		# Order sections for the list of sections
		# Append the sections to the dictionary where the key is section[1] for section in sections
		for section in sections:
 			# Account for multi-line class days, separated by "AND"
			if len(section) > 8 and section[9] != "WEB":
				days = section[1].replace(" ", "") + " " + section[9].replace(" ", "")
			else:
				days = section[1]
			sections_by_day[days].append(section)
		
		return sections_by_day
		
	"""
	Precondition:
		A list of a class's sections
	Postcondition:
		Return a list of sections ordered by time
	"""
	def order_by_time(self, sections):
		sections_ordered = []
		sections_times = [self.get_start_time(section) for section in sections]
	
		for i in range(len(sections)):
			min_time, min_i = self.minimum_and_index(sections_times[i:])
			min_i = min_i + i
			min_section = sections[min_i]
			# Reorder sections_times
			sections_times[min_i] = sections_times[i]
			sections_times[i] = min_time
			# Reorder sections
			sections[min_i] = sections[i]
			sections[i] = min_section

			sections_ordered.append(sections[i])

		return sections_ordered

	"""
	Precondition:
		A dictionary of lists
			dictionary has keys subjects 
			lists contain lists of sections
	Postcondition:
		A dictionary of dictionaries
			parent dictionary has keys subjects and values dictionaries 
			child dictionary has keys days of class and values sections ordered by start and end times
	"""
	def order_classes(self):
		for subject in self.subjects:
			self.class_dict[subject] = self.order_by_day(self.class_dict[subject])
			for days in self.class_dict[subject].keys():
				self.class_dict[subject][days] = self.order_by_time(self.class_dict[subject][days])

	"""
	Return true if any part in item (part being one separated by a space)
	is in any part in to_list
	"""
	def days_overlap_list(self, days, days_list):
		days_overlap = False
		f_days = days.split()
		for f_day in f_days:
			for t_days in days_list:
				t_days_list = t_days.split()
				for t_day in t_days_list:
					if f_day == t_day:
						days_overlap = True
		return days_overlap
	
	def days_overlap_dict(self, item, to_dict):
		days_overlap = False
		for keys in to_dict.keys():
			if self.days_overlap_list(item, to_dict[keys]):
				days_overlap = True
		return days_overlap
			
	def get_class_days(self, c_dict):
		class_days = defaultdict(dict) # dictionary of class days
		# From a dictionary containing classes and their sections' information,
		# add to a new dict under each subject a list containing all the days
		# its sections are held
		for subj in c_dict.keys():
			class_days[subj] = [days for days in c_dict[subj].keys()]
		return class_days

	def times_overlap(self, times1, times2):
		times_overlap = False
	
		start1, end1 = times1[0], times1[1]
		start2, end2 = times2[0], times2[1]
	
		if (start2 <= start1 and start1 <= end2) or (start2 <= end1 and end1 <= end2):
			times_overlap = True
		elif (start1 <= start2 and start2 <= end1) or (start2 <= end1 and end1 <= end2):
			times_overlap = True
	
		return times_overlap

	def merge_outliers(self, c_dict):
		c_dict_new = defaultdict(dict)
		class_days = self.get_class_days(c_dict) # dictionary of class days

		print("class_days:")
		print(class_days)

		# for subj in class_days.keys():
		for i in range(len(self.subjects)):
			days_list = class_days[self.subjects[i]]  
			del class_days[self.subjects[i]] # Delete the list of days for this subject so that its days are not compared to itself
			for days in days_list: # for each day in the subject
				# Check if it does not overlap the entire dict
				if not self.days_overlap_dict(days, class_days):
					# Append sections whose days do not overlap with other sections to c_dict_new
					c_dict_new[self.subjects[i]][days] = c_dict[self.subjects[i]][days].copy()
			class_days[self.subjects[i]] = days_list # Re-add the list of days
		return c_dict_new
		
	"""
	Delete all entries in t_dd under the keys of f_dd, where both are dicts of dicts.
	"""
	def delete_overlap_dd(self, f_dd, t_dd):
		for subj in f_dd.keys():
			for days in f_dd[subj].keys():
				del t_dd[subj][days]
		return t_dd
		
	'''
	Find smaller list in dict.
	Use the smaller list to be merged with the larger into another list
		- Group the sections in one subject list into equivalent times
			- if the start times of sections from larger_list
				are within the times of two start times of smaller_list
			- then append the sandwich to a merged_list
	'''
	def merge_classes(self):	
		class_dict_new = defaultdict(dict)
		class_dict_copy = self.class_dict.copy()

		class_dict_new = self.merge_outliers(class_dict_copy)

		# Update class_dict_copy to reflect the subjects and days left in it
		class_dict_copy = self.delete_overlap_dd(class_dict_new, class_dict_copy)

		# Now we have in class_dict_copy the subjects whose sections are contained in the same day.
		# We can compare the sections by day.
		# Take the first subject's first section, compare it to the next subject's sections that lie on the same day. If the first section's times overlap the another section's times, discard both sections from class_dict_copy and do not append to class_dict_new, meaning to not count them as valid combinations.
		
		print("class_dict_new: ")
		print_class_dict(class_dict_new)

		print("class_dict_copy: ")
		print_class_dict(class_dict_copy)

		'''
		class_days = self.get_class_days(class_dict_copy)
		for i in range(len(self.subjects)): # for each subject
			for day in class_dict_copy[self.subjects[i]].keys():
				for section in class_dict_copy[self.subjects[i]][day]:
					if self.times_overlap():
						del class_dict_copy[self.subjects
					
			
			
		'''
	# def calc_class_combos(self):

		

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


def print_class_dict(c_dict):
	for subject in c_dict.keys():
		print(subject)
		for day in c_dict[subject]:
			print(day)
			for section in c_dict[subject][day]:
				print(section)
		print()
		
# MAIN******************
# ACCTG 1A
print("Scraping data...")
s1 = Scraper("1695", "002181", "SPRING", "ACCTG", "1A")

# CS 11
# s2 = Scraper("1695", "002669", "SPRING", "CS", "11")

# ENGL 1
s2 = Scraper("1695", "000643", "SPRING", "ENGL", "1")
print("Done scraping data.")

scrapers = [s1, s2]
class_dict = {} # dictionary to be passed to Processor object
for scraper in scrapers:
	class_dict[scraper.get_id()] = scraper.get_class_schedules() # class_dict has keys ``subject + number'' and
									# values the list of the subject's sections

for key in class_dict.keys():
	print(key)
	print(class_dict[key])

processor = Processor(class_dict)
print("Processing data...")
processor.order_classes()
print("Done processing data.")

print_class_dict(class_dict)

print("Merging classes...")
processor.merge_classes()
