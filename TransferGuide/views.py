import json

from django.db.models.functions import Length, Substr
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth import logout, get_user_model
from django.template import loader
from django.views import generic
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .tasks import sisBackground
from .models import Course, requestForm, Emails, AutoReplyEmail
from django.shortcuts import redirect
import requests

from django.db.models import Q

subjectList = []


class index(generic.ListView):
    model = requestForm
    template_name = 'TransferGuide/newLogin.html'
    context_object_name = 'requestForm_list'


def logoutt(request):
    logout(request)

    response = redirect('https://transfer-credit-guide.herokuapp.com/')
    return response


def displayUpdate(request, semester, page, subjectNum):
    template = loader.get_template('TransferGuide/newUpdate.html')
    param = str(semester) + '/' + str(page) + '/' + str(subjectNum) + '/'
    num = (int(semester) * 202 + int(subjectNum)) * 100
    percent = int(num / 808)
    context = {
        'param': param,
        'percent': percent,
    }
    return HttpResponse(template.render(context, request))


def sisUpdate(request, semester, page, subjectNum):
    semesters = ['1231', '1232', '1236', '1238']
    semester = int(semester)
    subjectNum = int(subjectNum)
    page = int(page)
    if subjectList == []:
        info = requests.get(
            'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1232')
        data = info.json()
        a = data['subjects']

        gettingSubjects = True
        x = 0
        while gettingSubjects:
            try:
                subjects = a[x]
                subject = subjects['subject']
                subjectList.append(subject)
            except IndexError:
                print('done!')
                print(subjectList)
                gettingSubjects = False
                break

            x = x + 1

    test = sisBackground(semesters[semester], subjectList[subjectNum], page)

    if (test):
        subjectNum = subjectNum + 1
        page = 1
    else:
        page = page + 1

    if (subjectNum == len(subjectList)):
        subjectNum = 0
        page = 1
        semester = semester + 1

    if (semester == 4):
        return render(request, 'TransferGuide/newCourseInfo.html')

    response = redirect('/displayUpdate/' + str(semester) + '/' + str(page) + '/' + str(subjectNum) + '/')
    return response


class CoursesViewAll(generic.ListView):
    template_name = 'TransferGuide/newAllCourses.html'
    context_object_name = 'all_courses_list'

    def get_queryset(self):
        all_subjects_queryset = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
        all_subjects_queryset = all_subjects_queryset.values_list()
        subjects = []
        for item in all_subjects_queryset:
            if item[3] not in subjects:
                subjects.append(item[3])
        json_subjects = json.dumps(subjects)
        return {
            "courses": Course.objects.all().order_by('courseSubject', 'courseNumber'),
            "subjects": Course.objects.all().values('courseSubject').order_by('courseSubject').distinct(),
            "jsonSubjects": json_subjects
        }


def make_query(subject_query, number_query, name_query, university_query):
    all_subjects_queryset = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
    all_universities_queryset = Course.objects.all().values('universityLong').order_by('universityLong').distinct()
    all_universities_short_queryset = Course.objects.all().values('universityShort').order_by(
        'universityShort').distinct()
    all_numbers_queryset = Course.objects.all().values("courseNumber").order_by("courseNumber").distinct()
    all_names_queryset = Course.objects.all().values("courseName").order_by("courseName").distinct()

    all_subjects_queryset = all_subjects_queryset.values_list()
    all_universities_queryset = all_universities_queryset.values_list()
    all_universities_short_queryset = all_universities_short_queryset.values_list()
    all_numbers_queryset = all_numbers_queryset.values_list()
    all_names_queryset = all_names_queryset.values_list()
    subjects = []
    universities = []
    universities_short = []
    numbers = []
    names = []

    for item in all_subjects_queryset:
        if item[3] not in subjects:
            subjects.append(item[3])
    for item in all_universities_queryset:
        if item[5] not in universities:
            universities.append(item[5])
    for item in all_numbers_queryset:
        if item[2] not in numbers:
            numbers.append(item[2])
    for item in all_names_queryset:
        if item[1] not in names:
            if "\"" in item[1]:
                names.append(item[1].replace("\"", ''))
            else:
                names.append(item[1])
    for item in all_universities_short_queryset:
        if item[3] not in universities_short:
            universities_short.append(item[3])

    json_subjects = json.dumps(subjects)
    json_universities = json.dumps(universities)
    json_universities_short = json.dumps(universities_short)
    json_numbers = json.dumps(numbers)
    json_names = json.dumps(names)

    if (subject_query == '') & ((number_query == -1) | (number_query == '')) & (name_query == '') & (
            university_query == ''):
        return {"json": json_subjects, "universitiesJSON": json_universities,
                "universitiesShortJSON": json_universities_short, "numbersJSON": json_numbers,
                "namesJSON": json_names}

    courses = Course.objects.annotate(
        course_number_length=Length('courseNumber'),
        starting_digit=Substr('courseNumber', 1, 1),
    ).order_by('courseSubject', 'starting_digit', 'course_number_length', 'courseNumber')
    subjects = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()

    criteria = [subject_query, number_query, name_query, university_query]

    for i in range(len(criteria)):
        filter_criteria = criteria[i]
        if (filter_criteria is not None) & (filter_criteria != '') & (filter_criteria != -1):
            if filter_criteria == subject_query:
                exact_match = Q(courseSubject__iexact=filter_criteria)
                partial_match = Q(courseSubject__icontains=filter_criteria) & ~exact_match
                courses = courses.filter(exact_match | partial_match)
                # courses = courses.filter(Q(courseSubject__icontains=filter_criteria))
                exact_match = Q(courseSubject__iexact=filter_criteria)
                partial_match = Q(courseSubject__icontains=filter_criteria) & ~exact_match
                subjects = subjects.filter(exact_match | partial_match)
                # subjects = subjects.filter(Q(courseSubject__icontains=filter_criteria))
            elif filter_criteria == number_query:
                courses &= courses.filter(Q(courseNumber=number_query))
                subjects &= subjects.filter(Q(courseNumber=number_query))
            elif filter_criteria == name_query:
                courses = courses.filter(Q(courseName__icontains=name_query))
                subjects = subjects.filter(Q(courseName__icontains=name_query))
            elif filter_criteria == university_query:
                courses = courses.filter(Q(universityLong__icontains=university_query))
                subjects = subjects.filter(Q(universityLong__icontains=university_query))

    return {"courses": courses, "subjects": subjects, "json": json_subjects, "universitiesJSON": json_universities,
            "universitiesShortJSON": json_universities_short, "numbersJSON": json_numbers, "namesJSON": json_names}


class SearchResultsView(generic.ListView):
    model = Course
    template_name = 'TransferGuide/newSearch.html'
    context_object_name = 'all_courses_list'

    # Need to add search based on university once that is set up
    def get_queryset(self):
        subject_query = self.request.GET.get("subject")
        number_query = self.request.GET.get("number")
        name_query = self.request.GET.get("name")
        university_query = self.request.GET.get("university")
        if subject_query is None:
            subject_query = ''
        if subject_query is not None:
            subject_query = subject_query.upper()
        if name_query is None:
            name_query = ''
        if number_query is None:
            number_query = -1
        if university_query is None:
            university_query = ''

        return make_query(subject_query, number_query, name_query, university_query)


class CourseInfo(generic.ListView):
    model = Course
    template_name = 'TransferGuide/newCourseInfo.html'
    context_object_name = 'course_info'

    def get_queryset(self):
        subject_query = self.request.GET.get("subject")
        number_query = self.request.GET.get("number")
        university_query = self.request.GET.get("university")

        if (subject_query is None) & (number_query is None) & (university_query is None):
            queryset = []
        else:
            queryset = Course.objects.filter(courseNumber=number_query, courseSubject=subject_query,
                                             universityShort__icontains=university_query)
        return queryset


def make_number_query(numbers):
    new_numbers = []
    for i in range(len(numbers)):
        num = numbers[i]
        tens = num * 10
        tens_upper = (num + 1) * 10 - 1
        hundreds = num * 100
        hundreds_upper = (num + 1) * 100 - 1
        thousands = num * 1000
        thousands_upper = (num + 1) * 1000 - 1
        numbers_to_compute = [tens, tens_upper, hundreds, hundreds_upper, thousands, thousands_upper]
        index = 0
        while index < len(numbers_to_compute):
            lower = numbers_to_compute[index]
            index += 1
            upper = numbers_to_compute[index]
            index += 1
            for j in range(lower, upper + 1):
                new_numbers.append(j)
    return new_numbers


# maybe add approved/disapproved courses filter alter
class CourseFilter(generic.ListView):
    model = Course
    template_name = 'TransferGuide/newFilter.html'
    context_object_name = 'filtered_courses'

    def get_queryset(self):
        subject_query = self.request.GET.get("subject")
        number_query = self.request.GET.get("number")
        university_query = self.request.GET.getlist("universities")

        if (subject_query == '') & (number_query == '') & (university_query == ['']):
            all_subjects_queryset = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
            all_universities_queryset = Course.objects.all().values('universityLong').order_by(
                'universityLong').distinct()

            all_subjects_queryset = all_subjects_queryset.values_list()
            all_universities_queryset = all_universities_queryset.values_list()
            subjects = []
            universities = []
            for item in all_subjects_queryset:
                if item[3] not in subjects:
                    subjects.append(item[3])
            for item in all_universities_queryset:
                if item[5] not in universities:
                    universities.append(item[5])
            json_subjects = json.dumps(subjects)
            json_universities = json.dumps(universities)

            courses = []
            return_set = {
                "json": json_subjects,
                "courses": courses,
                "filteredSubjects": subjects,
                "allSubjects": Course.objects.all().values('courseSubject').order_by('courseSubject').distinct(),
                "universitiesJSON": json_universities
            }
            return return_set

        if university_query == ['']:
            university_query = None
        number_query_list = []
        subject_query = [subject_query]
        if not isinstance(number_query, int):
            if number_query is not None:
                number_query = list(number_query)
                count = number_query.count(',')
                for i in range(count):
                    number_query.remove(',')
                for i in range(len(number_query)):
                    if number_query[i] != '':
                        number_query[i] = eval(number_query[i])
                if len(number_query) > 0:
                    number_query_list = make_number_query(number_query)
        if subject_query == ' ':
            subject_query = None
        if university_query is not None:
            if len(university_query) > 0:
                university_query = university_query[0].split(',')
        if university_query == '':
            university_query = None
        if subject_query == ['']:
            subject_query = None
        if subject_query == [None]:
            subject_query = None
        if university_query == []:
            university_query = None

        all_subjects_queryset = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
        all_universities_queryset = Course.objects.all().values('universityLong').order_by('universityLong').distinct()

        all_subjects_queryset = all_subjects_queryset.values_list()
        all_universities_queryset = all_universities_queryset.values_list()
        subjects = []
        universities = []
        for item in all_subjects_queryset:
            if item[3] not in subjects:
                subjects.append(item[3])
        for item in all_universities_queryset:
            if item[5] not in universities:
                universities.append(item[5])
        json_subjects = json.dumps(subjects)
        json_universities = json.dumps(universities)

        if subject_query is not None:
            subject_query = subject_query[0]
            subject_query = subject_query.split(',')

        filters = Q()
        if (subject_query != '') and (subject_query is not None):
            filters &= Q(courseSubject__in=subject_query)
        if len(number_query_list) > 0:
            filters &= Q(courseNumber__in=number_query_list)
        if university_query is not None:
            filters &= Q(universityLong__in=university_query)

        if len(filters) < 1:
            courses = []
        else:
            courses = Course.objects.filter(
                Q(filters)).order_by('courseNumber')

        subjects = Course.objects.filter(Q(
            filters)).values('courseSubject').order_by(
            'courseSubject').distinct()

        if number_query is not None:
            courses = courses.annotate(
                course_number_length=Length('courseNumber'),
                starting_digit=Substr('courseNumber', 1, 1),
            ).order_by('courseSubject', 'starting_digit', 'course_number_length', 'courseNumber')

        return_set = {
            "json": json_subjects,
            "courses": courses,
            "filteredSubjects": subjects,
            "allSubjects": Course.objects.all().values('courseSubject').order_by('courseSubject').distinct(),
            "universitiesJSON": json_universities
        }
        return return_set


class AddEquivalency(generic.ListView):
    model = Course
    template_name = 'TransferGuide/newAddEquivCourse.html'
    context_object_name = 'all_courses_list'

    @staticmethod
    def post(request):
        print("before if")
        print(request.method)
        if request.method == 'POST':
            form = request.POST

            existingCourseSet = Course.objects.filter(Q(universityLong__iexact=form.get('outsideUniversity'))).filter(
                courseSubject=form.get('outsideSubject')).filter(courseNumber=form.get('outsideNumber'))

            if len(existingCourseSet) <= 0:
                # queryset is empty

                oCourse = Course()
                oCourse.courseName = form.get('outsideName')
                oCourse.courseNumber = form.get('outsideNumber')
                oCourse.courseSubject = form.get('outsideSubject')
                oCourse.universityShort = form.get('outsideAcronym')
                oCourse.universityLong = form.get('outsideUniversity')

                uvaInfo = form.get('uvaSubject').split(' ')
                uvaSubject = uvaInfo[0]
                uvaNumber = uvaInfo[1]
                uvaName = ''
                for i in range(2, len(uvaInfo)):
                    uvaName += uvaInfo[i]
                    if i != len(uvaInfo) - 1:
                        uvaName += ' '

                equivCourseDict = {
                    "universityShort": "UVA",
                    "universityLong": "University of Virginia",
                    "subject": uvaSubject,
                    "number": uvaNumber,
                    "name": uvaName
                }
                equivCourseList = list()
                equivCourseList.append(equivCourseDict)
                oCourse.equivalentCourse = equivCourseList

                oCourse.save()


                uvaUniversityLong = "University of Virginia"
                uvaUniversityShort = "UVA"

                uvaCourse = Course.objects.all().filter(Q(courseSubject__iexact=uvaSubject) & Q(courseNumber__iexact=
                                                                                                uvaNumber) & Q(
                    courseName__iexact=uvaName) & Q(universityLong__iexact=uvaUniversityLong) &
                                                        Q(universityShort__iexact=uvaUniversityShort))

                oldEquivList = uvaCourse[0].equivalentCourse
                UVAEquivCourseDict = {
                    "universityShort": form.get('outsideAcronym'),
                    "universityLong": form.get('outsideUniversity'),
                    "subject": form.get('outsideSubject'),
                    "number": form.get('outsideNumber'),
                    "name": form.get('outsideName')
                }
                if (len(oldEquivList) == 0):
                    oldEquivList = list()

                oldEquivList.append(UVAEquivCourseDict)
                if type(uvaCourse[0].equivalentCourse) is dict:
                    uvaCourse[0].equivalentCourse.update(UVAEquivCourseDict)
                else:
                    uvaCourse[0].equivalentCourse.append(UVAEquivCourseDict)
                UVACourse = uvaCourse[0]
                UVACourse.equivalentCourse = oldEquivList

                UVACourse.save(force_update=True)
                messages.add_message(request, messages.SUCCESS, "Course Equivalency Added")
                return redirect('addEquivCoursePage')
            else:
                messages.error(request, 'Class Equivalency Already Exists in Database')
                return redirect('addEquivCoursePage')

    def get_queryset(self):
        all_subjects_queryset = Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
        all_numbers_queryset = Course.objects.all().values("courseNumber").order_by("courseNumber").distinct()
        all_names_queryset = Course.objects.all().values("courseName").order_by("courseName").distinct()

        all_subjects_queryset = all_subjects_queryset.values_list()
        all_numbers_queryset = all_numbers_queryset.values_list()
        all_names_queryset = all_names_queryset.values_list()
        subjects = []
        numbers = []
        names = []

        all_together = []
        all_together_query = Course.objects.all().values().distinct().order_by('courseSubject', 'courseNumber')
        # print(all_together_query)
        for course in all_together_query:
            if course.get('universityShort') == 'UVA':
                to_add = ''
                to_add += course.get('courseSubject')  # subject
                to_add += ' ' + course.get('courseNumber')  # number
                courseName = course.get('courseName')
                if "\"" in courseName:
                    to_add += ' ' + courseName.replace("\"", '')  # name
                else:
                    to_add += ' ' + course.get('courseName')  # name
                all_together.append(to_add)

        all_together_json = json.dumps(all_together)

        for item in all_subjects_queryset:
            if item[4] == 'UVA':
                if item[3] not in subjects:
                    subjects.append(item[3])
        for item in all_numbers_queryset:
            if item[4] == 'UVA':
                if item[2] not in numbers:
                    numbers.append(item[2])
        for item in all_names_queryset:
            if item[4] == 'UVA':
                if item[1] not in names:
                    if "\"" in item[1]:
                        names.append(item[1].replace("\"", ''))
                    else:
                        names.append(item[1])

        json_subjects = json.dumps(subjects)
        json_numbers = json.dumps(numbers)
        json_names = json.dumps(names)
        return {"json": json_subjects, "numbersJSON": json_numbers, "namesJSON": json_names,
                "courses": all_subjects_queryset, "all_together": all_together_json}


class Test(generic.ListView):
    template_name = 'TransferGuide/changeUserPriv.html'
    context_object_name = 'all_courses_list'

    def get_queryset(self):
        return {
            "courses": Course.objects.all().order_by('courseSubject', 'courseNumber'),
            "subjects": Course.objects.all().values('courseSubject').order_by('courseSubject').distinct()
        }


class RequestForms(generic.ListView):
    model = requestForm
    template_name = 'TransferGuide/newRequests.html'


def requests_database(request):
    if request.method == "POST":
        requestForm1 = requestForm.objects.create(courseName=request.POST['courseName'],
                                                  courseNumber=request.POST['courseNumber'],
                                                  courseSubject=request.POST['courseSubject'],
                                                  university=request.POST['university'],
                                                  universityShort=request.POST['universityShort'],
                                                  url=request.POST['url'],
                                                  studentName=request.user,
                                                  studentEmail=request.user.email)
        messages.add_message(request, messages.SUCCESS, "Request submitted")
    return redirect('index')


def pending_requests(request):
    requests = requestForm.objects.all()

    form_id = request.GET.get("request_id")
    status = request.GET.get("status")

    if form_id is not None:
        form = requestForm.objects.all().filter(id=form_id)[0]
        time = timezone.localtime()
        content1 = "You request form for: " + request.GET.get("request_courseSubject") + " " + request.GET.get(
            "request_courseNumber") + " " + request.GET.get("request_courseName") + " at " + request.GET.get(
            "request_University") + " has had its status changed from " + form.status + " to " + request.GET.get(
            "status") + " at " + time.strftime("%Y-%m-%d %H:%M:%S")
        autoReply = AutoReplyEmail.objects.create(content=content1,
                                                  studentEmail=request.GET.get("request.studentEmail"))
        form.status = status
        form.save()

    return render(request, "TransferGuide/newPendingRequests.html", context={"requests": requests})


def update_email_status(request, email_id, auto_reply, for_admins):
    if request.method == 'POST':
        if auto_reply == 1:
            email = AutoReplyEmail.objects.get(id=email_id)
        else:
            email = Emails.objects.get(id=email_id)
        email.status = request.POST.get('status')
        email.save()
        return redirect('mailBox')
    else:
        return HttpResponseNotAllowed(['POST'])


def send_reply(request, email_id, auto_reply, for_admins):
    if request.method == 'POST':
        if auto_reply == 1:
            email = AutoReplyEmail.objects.get(id=email_id)
        else:
            email = Emails.objects.get(id=email_id)
        if for_admins == 1:
            for_admins_value = 'True'
        else:
            for_admins_value = 'False'
        emailS1 = Emails.objects.create(title="Re: " + email.title, content=request.POST['reply_content'],
                                        studentName=email.studentName,
                                        studentEmail=email.studentEmail, studentName_id=email.studentName_id,
                                        reply='True', for_admins=for_admins_value, send_time=timezone.now())
        email.status = 'Read'
        email.save()
        messages.add_message(request, messages.SUCCESS, "Email sent")
        return redirect('mailBox')
    else:
        return HttpResponseNotAllowed(['POST'])


def mail_box(request):
    emails = Emails.objects.all().order_by('pk').reverse()
    AutoReplys = AutoReplyEmail.objects.all().order_by('pk').reverse()

    return render(request, "TransferGuide/newMailBox.html", context={"requests": emails, "Autos": AutoReplys})


def send_email(request):
    return render(request, "TransferGuide/newSendBox.html")


def email_database(request):
    if request.method == "POST":
        emailS1 = Emails.objects.create(title=request.POST['title'], content=request.POST['content'],
                                        studentName=request.user,
                                        studentEmail=request.user.email, reply='False', for_admins='True', send_time=timezone.now())
        messages.add_message(request, messages.SUCCESS, "Email sent")
    return redirect('index')


class ChangePriv(generic.ListView):
    template_name = 'TransferGuide/changeUserPriv.html'
    model = get_user_model()
    context_object_name = 'users_list'

    @staticmethod
    def post(request):
        if request.method == 'POST':
            body = str(request.body)

            id_start_index = body.find("&userInfo=")
            id_end_index = body.find("&userStatus=")

            user_id = body[id_start_index:id_end_index].replace("&userInfo=", '').replace('+', ' ')
            user_id = user_id[0:user_id.find(' ')]
            superuser_status = body[id_end_index:].replace("&userStatus=", '').replace('\'', '').replace('+', ' ')
            User = get_user_model()
            usersAll = User.objects.all()
            user = ''
            for i in range(len(usersAll)):
                if usersAll[i].id == int(user_id):
                    user = usersAll[i]
            if user == '':
                messages.add_message(request, messages.SUCCESS, "User not found")
                return redirect('change_user_status')
            else:
                if superuser_status == 'Make Admin':
                    user.is_superuser = True
                elif superuser_status == 'Remove Admin':
                    user.is_superuser = False

                user.save()
                messages.add_message(request, messages.SUCCESS, "Successfully changed user status")
                return redirect('change_user_status')

    def get_queryset(self):
        User = get_user_model()
        IDS = User.objects.all().values('username', 'id').order_by('id')
        IDS_list = []
        for i in range(len(IDS)):
            IDS_list.append(str(IDS[i].get('id')) + ' ' + IDS[i].get('username'))
        jsonIDS = json.dumps(IDS_list)

        users_list = {"user_ids": User.objects.all().order_by('id'), "user_pks": User.objects.all().values("id"), "jsonIDS": jsonIDS}
        return users_list
