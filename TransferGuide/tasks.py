import requests
from .models import Course
from django.core.exceptions import ObjectDoesNotExist 
from django.core.exceptions import MultipleObjectsReturned
from django.db import models



def sisBackground(semester, subject, pageNum):
    semester = str(semester)
    subject = str(subject)
    pageNum = str(pageNum)
    url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term='+semester+'&page='+pageNum+'&subject='+subject
    page = requests.get(url)
    data = page.json()

    for i in range(0,99):#goes through every course in a page
        inDB = True
        try: #if an exception happens then all the courses have been added
            course = data[i]
            catalogNum = course['catalog_nbr']
            name = course['descr']

            
            
            try:#an excpetion is thrown if the object is not in the database yet, so that we don't get repeats
                Course.objects.get(models.Q(courseNumber=catalogNum), models.Q(courseSubject=subject), models.Q(universityShort__iexact="UVA") | models.Q(universityLong__iexact="University Of Virginia")) 
                inDB = True
            except ObjectDoesNotExist:
                inDB = False
            except MultipleObjectsReturned:
                inDB = True


            if inDB == False:#create new course if it does not exist
                Course.objects.create(courseNumber=catalogNum, courseSubject=subject, courseName=name)


        except IndexError:
            return 1
            break
    return 0


    '''OLD METHOD
    #library info found from https://requests.readthedocs.io/en/latest/user/quickstart/
    semesters = ['1231','1232','1236','1238'] #list of semesters

    for sem in semesters:# goes through every semester in this year
        pageNotEmpty = True
        x=1

        while(pageNotEmpty): #goes through every page in a semester
            url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term='+sem+'&page='+ str(x)
            page = requests.get(url)
            data = page.json()
            
            for i in range(0,99):#goes through every course in a page
                inDB = True
                try: #if an exception happens then all the courses have been added
                    course = data[i]
                    catalogNum = course['catalog_nbr']
                    subject = course['subject']
                    name = course['descr']
                    prevCatalogNum = catalogNum

                    
                    
                    try:#an excpetion is thrown if the object is not in the database yet, so that we don't get repeats
                        Course.objects.get(courseNumber=catalogNum, courseSubject=subject) 
                        inDB = True
                    except ObjectDoesNotExist:
                        inDB = False
                    except MultipleObjectsReturned:
                        inDB = True


                    if inDB == False:#create new course if it does not exist
                        Course.objects.create(courseNumber=catalogNum, courseSubject=subject, courseName=name, equivalentCourse='N/A')


                except IndexError:
                    pageNotEmpty = False
                    break

            x = x+1'''