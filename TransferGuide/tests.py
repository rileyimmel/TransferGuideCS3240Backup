from django.test import RequestFactory, TestCase
from .models import Course, requestForm, acronym, Emails, AutoReplyEmail
from .views import SearchResultsView
from django.contrib.auth.models import User


class URLTests(TestCase):
    def test_home(self):
        response = self.client.get('', secure=True)
        self.assertTrue(response.status_code == 200)

    # def test_ClassInfos(self): # no longer exists
    #     response = self.client.get('/ClassInfos/')
    #     self.assertTrue(response.status_code == 200)

    #def test_accounts_logout(self):
     #   response = self.client.get('/accounts/logout')
      #  self.assertTrue(response.status_code == 200)

    def test_All_Courses(self):
        response = self.client.get('/allCourses', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_Search(self):
        response = self.client.get('/search/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_info(self):
        response = self.client.get('/info/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_filter(self):
        response = self.client.get('/filter/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_addEquivalentCourse(self):
        response = self.client.get('/addEquivalentCourse/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_PendingRequests(self):
        response = self.client.get('/pendingRequests/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_requestForm(self):
        response = self.client.get('/requestForm/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_pendingRequests(self):
        response = self.client.get('/pendingRequests/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_mailbox(self):
        response = self.client.get('/mailBox/', secure=True)
        self.assertTrue(response.status_code == 200)

    def test_sendmail(self):
        response = self.client.get('/sendMail/', secure=True)
        self.assertTrue(response.status_code == 200)

    # def test_autoDatabase(self): # no longer exists
    #     response = self.client.get('/autoDatabase')
    #     self.assertTrue(response.status_code == 200)


class CourseDisplay(TestCase):
    def test_display(self):
        course = Course(courseName="name", courseNumber='1', courseSubject='BRUH')
        name = course.courseName
        number = course.courseNumber
        subject = course.courseSubject
        self.assertEqual(subject + number + name, "BRUH" + "1" + "name")

    def test_display2(self):
        course = Course(courseName="name", courseNumber='123456', courseSubject='BRUH')
        name = course.courseName
        number = course.courseNumber
        subject = course.courseSubject
        self.assertEqual(subject + number + name, "BRUH" + "123456" + "name")


class Requests(TestCase):
    def test_request_creation(self):
        request = requestForm()
        name = request.courseName
        number = request.courseNumber
        subject = request.courseSubject
        self.assertEqual(name + number + subject, request.courseName + request.courseNumber + request.courseSubject)

    def test_request_creation2(self):
        request = requestForm(courseName="name", courseNumber="101", courseSubject="lol")
        name = request.courseName
        number = request.courseNumber
        subject = request.courseSubject
        self.assertEqual(name + number + subject, "name" + "101" + "lol")


class AcronymDisplay(TestCase):
    # acronym = acronym(encoder=None, decoder=None, default=dict, null=True, blank=True)

    def test_acronym(self):
        self.assertEqual("", "")


class EmailsDisplay(TestCase):
    def test_emails(self):
        email = Emails(title="title", content="content", studentName=User(), studentEmail="email", status="unread")
        title = email.title
        content = email.content
        studentEmail = email.studentEmail
        status = email.status
        self.assertEqual(title + content + studentEmail + status, "title" + "content" + "email" + "unread")


class AutoReplyEmailDisplay(TestCase):
    ARE = AutoReplyEmail(title="title", content="content", studentEmail="email", status="unread")
    title = ARE.title
    content = ARE.content
    studentEmail = ARE.studentEmail
    status = ARE.status

    def test_AutoReplyEmailDisplay(self):
        self.assertEqual(self.title + self.content + self.studentEmail + self.status,
                         "title" + "content" + "email" + "unread")

    def test_AutoReplyEmailString(self):
        ARE = AutoReplyEmail(title="title", content="content", studentEmail="email", status="unread")
        self.assertEqual(ARE.__str__(), "title " + "content " + "email, " + "unread ")
