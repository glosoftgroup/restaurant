from __future__ import unicode_literals
from django.utils.timezone import now
from django.db import models

class Contacts(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	mobile = models.CharField(max_length=100, null=True, blank=True)
	relation = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return str(self.name)

class Bank(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class BankBranch(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    bank =  models.ForeignKey(Bank, related_name='branch', max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class Department(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class UserRole(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)

# Create your models here.
class Employee(models.Model):
	'''dsadad'''
	added_on = models.DateTimeField(default=now, editable=False)
	name = models.CharField(max_length=100, null=True, blank=True)
	dob = models.CharField(max_length=100, null=True, blank=True)
	doj = models.CharField(max_length=100, null=True, blank=True)
	email = models.CharField(max_length=100, null=True, blank=True)
	mpbile = models.CharField(max_length=100, null=True, blank=True)
	nid = models.CharField(max_length=100, null=True, blank=True)
	gender = models.CharField(max_length=100, null=True, blank=True)
	department = models.CharField(max_length=100, null=True, blank=True)
	role = models.CharField(max_length=100, null=True, blank=True)
	marital_status = models.CharField(max_length=100, null=True, blank=True)
	employement_type = models.CharField(max_length=100, null=True, blank=True)
	'''education details'''
	qualification = models.CharField(max_length=100, null=True, blank=True)
	school = models.CharField(max_length=100, null=True, blank=True)
	graduation_year = models.CharField(max_length=100, null=True, blank=True)
	'''contacts details'''
	contacts = models.ForeignKey(
        Contacts, related_name='contacts', blank=True, null=True, default='')
	phone = models.CharField(max_length=100, null=True, blank=True)
	'''statutory details'''
	amount = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
	'''Job History details'''

	def __str__(self):
		return str(self.name)
