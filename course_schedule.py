	# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime
def check(i,j):
	print(i.day,j.day)
	ifrom_time = datetime.strptime(i.from_time, '%H:%M:%S').time()
	ito_time = datetime.strptime(i.to_time, '%H:%M:%S').time()
	jfrom_time = datetime.strptime(j.from_time, '%H:%M:%S').time()
	jto_time = datetime.strptime(j.to_time, '%H:%M:%S').time()
	if i.day==j.day  and ( (ifrom_time >=jfrom_time and ifrom_time<jto_time) or (ito_time > jfrom_time and ito_time<jto_time) or (ifrom_time <jfrom_time and ito_time>jfrom_time) ) :
		return True
	return False 
class OverlapError(frappe.ValidationError): pass
class CourseSchedule(Document):
	def validate(self):
		self.instructor_name = frappe.db.get_value("Instructor", self.instructor, "instructor_name")
		self.set_title()
		self.validate_course()
		#self.validate_date()
		#self.validate_overlap()
		self.validate_selfoverlap()
		self.validate_group()
		self.validate_instructor()
		self.validate_room()
	def set_title(self):
		"""Set document Title"""
		self.title = self.course + " by " + (self.instructor_name if self.instructor_name else self.instructor) +" group "+ self.student_group
	
	def validate_course(self):
		group_based_on, course = frappe.db.get_value("Student Group", self.student_group, ["group_based_on", "course"])
		if group_based_on == "Course":
			self.course = course

	
	
	
	def validate_selfoverlap(self):
		for i in self.emploi :
			for j in self.emploi:
				if i.name!=j.name and check(i,j):
					frappe.throw(_("Chevauchement d'emploi le {} entre {} et {}  ").format(i.day,i.from_time,i.to_time), OverlapError)
					
	
	
	def validate_date(self):
		"""Validates if from_time is greater than to_time"""
		if self.from_time > self.to_time:
			frappe.throw(_("From Time cannot be greater than To Time."))
	
	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""
		
		from erpnext.education.utils import validate_overlap_for

		#Validate overlapping course schedules.
		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "student_group")
		
		validate_overlap_for(self, "Course Schedule", "instructor")
		validate_overlap_for(self, "Course Schedule", "room")

		#validate overlapping assessment schedules.
		if self.student_group:
			validate_overlap_for(self, "Assessment Plan", "student_group")
		
		validate_overlap_for(self, "Assessment Plan", "room")
		validate_overlap_for(self, "Assessment Plan", "supervisor", self.instructor)
		
	def validate_group(self):
		for i in self.emploi:
			existing = frappe.db.sql("""select emp.name, from_time, to_time from `tabEmploi` as emp, `tabCourse Schedule` as sc
		where emp.parent = sc.name and  `student_group`=%(val)s and emp.day = %(day)s and
		(
			(from_time >= %(from_time)s and from_time < %(to_time)s) or
			(to_time > %(from_time)s and to_time < %(to_time)s) or
			(%(from_time)s > from_time and %(from_time)s < to_time) or
			(%(from_time)s = from_time and %(to_time)s = to_time))
		and emp.name!=%(name)s """,
		{
			"day": i.day,
			"val": self.student_group,
			"from_time": i.from_time,
			"to_time": i.to_time,
			"name": i.name or "No Name"
		}, as_dict=True)
			if existing:
				frappe.throw(_("Groupe {} est occupé {} entre {} et {} ").format(self.student_group,i.day,i.from_time,i.to_time), OverlapError)
	def validate_instructor(self):
		for i in self.emploi:
			existing = frappe.db.sql("""select emp.name, from_time, to_time from `tabEmploi` as emp, `tabCourse Schedule` as sc
		where emp.parent = sc.name and  `instructor`=%(val)s and emp.day = %(day)s and
		(
			(from_time >= %(from_time)s and from_time < %(to_time)s) or
			(to_time > %(from_time)s and to_time < %(to_time)s) or
			(%(from_time)s > from_time and %(from_time)s < to_time) or
			(%(from_time)s = from_time and %(to_time)s = to_time))
		and emp.name!=%(name)s """,
		{
			"day": i.day,
			"val": self.instructor,
			"from_time": i.from_time,
			"to_time": i.to_time,
			"name": i.name or "No Name"
		}, as_dict=True)
			if existing:
				frappe.throw(_("Instructeur {} est occupé {} entre {} et {} ").format(self.instructor,i.day,i.from_time,i.to_time), OverlapError)
	def validate_room(self):
		for i in self.emploi:
			existing = frappe.db.sql("""select emp.name, from_time, to_time from `tabEmploi` as emp, `tabCourse Schedule` as sc
		where emp.parent = sc.name and  `classe`=%(val)s and emp.day = %(day)s and
		(
			(from_time >= %(from_time)s and from_time < %(to_time)s) or
			(to_time > %(from_time)s and to_time < %(to_time)s) or
			(%(from_time)s > from_time and %(from_time)s < to_time) or
			(%(from_time)s = from_time and %(to_time)s = to_time))
		and emp.name!=%(name)s """,
		{
			"day": i.day,
			"val": i.classe,
			"from_time": i.from_time,
			"to_time": i.to_time,
			"name": i.name or "No Name"
		}, as_dict=True)
			if existing:
				frappe.throw(_("Classe {} est occupé {} entre {} et {} ").format(i.classe,i.day,i.from_time,i.to_time), OverlapError)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
