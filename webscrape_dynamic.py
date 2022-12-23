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

class Scraper:
	def __init__(self, term, courseID, semester, subject, number):
		self.url = "https://apps.lbcc.edu/schedule/scheduleDetail.cfm?term=" + term + "&courseID=" + courseID + "&semester=" + semester + "&subject=" + subject + "&catalog_nbr=" + number

	# self.url = "https://apps.lbcc.edu/schedule/scheduleDetail.cfm?term=1695&courseID=002181&semester=SPRING&subject=ACCTG&catalog_nbr=1A"

	def tester(self):
		print(self.url)

	def process(self):
		session = HTMLSession()
		response = session.get(self.url)
		class_times = response.html.find("td") # Actually returns the class id, prof, time, whatnot. However, it prints other unnecessary info. Find how to delete them. My idea is to find the parent element and then .find() again.

		for class_time in class_times:
			print(class_time.text)
	# Print class times
	# """
	# def print(self):
	# """
	# print(class_times.text)

s = Scraper("1695", "002181", "SPRING", "ACCTG", "1A")
s.tester()
s.process()
s.print()
