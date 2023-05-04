from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Course(models.Model):
    courseName = models.CharField(max_length=200, default="N/A")  # name of course
    courseNumber = models.CharField(max_length=5, default="N/A")  # number of course
    courseSubject = models.CharField(max_length=20, default="N/A")  # department of course, i.e. CS
    universityShort = models.CharField(max_length=100, default="UVA")  #acronym, such as UVA
    universityLong = models.CharField(max_length=100, default="University Of Virginia")  # Full name so university of virginia
    equivalentCourse = models.JSONField(encoder=None, decoder=None, default=dict, null=True, blank=True)
    nonEquivalentCourse = models.JSONField(encoder=None, decoder=None, default=dict, null=True, blank=True)

    def __str__(self):
        return self.courseName


class requestForm(models.Model):
    courseName = models.CharField(max_length=200, default="N/A")  # name of course
    courseNumber = models.CharField(max_length=5, default="N/A")  # number of course
    courseSubject = models.CharField(max_length=20, default="N/A")  # department of course, i.e. CS
    university = models.CharField(max_length=100, default="N/A")  # Full name so University of Virginia
    universityShort = models.CharField(max_length=100, default="N/A") # acronym so UVA
    url = models.CharField(max_length=1000, default="N/A")  # url to class webpage
    studentName = models.ForeignKey(User, on_delete=models.CASCADE)
    studentEmail = models.CharField(max_length=1000, default="N/A")
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return '{} {} {}, {}, {}, {}, {}, {}'.format(self.courseSubject, self.courseNumber,
                                                     self.courseName, self.university,
                                                     self.url, self.studentName, self.studentEmail, self.status)


class user(models.Model):
    isAdmin = models.BooleanField(default=True)


class acronym(models.Model):
    nameAcronymTable = models.JSONField(encoder=None, decoder=None, default=dict, null=True, blank=True)


class Emails(models.Model):
    title = models.CharField(max_length=200, default="N/A")
    content = models.CharField(max_length=5000, default="N/A")
    studentName = models.ForeignKey(User, on_delete=models.CASCADE)
    studentEmail = models.CharField(max_length=1000, default="N/A")
    status = models.CharField(max_length=7, default="Unread")
    reply = models.CharField(max_length=5, default="False")
    for_admins = models.CharField(max_length=5, default="False")
    send_time = models.DateTimeField(default=timezone.now)


class AutoReplyEmail(models.Model):
    title = models.CharField(max_length=200, default="Auto-reply Status Changed")
    content = models.CharField(max_length=5000, default="N/A")
    studentEmail = models.CharField(max_length=1000, default="N/A")
    status = models.CharField(max_length=7, default="Unread")
    send_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} {} {}, {} '.format(self.title, self.content,
                                                     self.studentEmail, self.status)