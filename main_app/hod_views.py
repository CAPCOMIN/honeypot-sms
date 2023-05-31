import json
import sqlite3
import platform

import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.generic import UpdateView

from xml.dom.minidom import parse
from lxml import etree
import xml.dom.minidom
import pickle
import subprocess
# https://www.cnblogs.com/wjrblogs/p/14057784.html 反序列化漏洞介绍

import main_app.admin
from .forms import *
from .models import *

import sys
import logging

from .pystrich.code128 import Code128Encoder

import logging
from django.shortcuts import render
import csv


# 配置logging
# logging.FileHandler(filename='access.log', encoding='utf-8')
# logging.basicConfig(
#     filename="access.log",
#     filemode="w",
#     encoding='utf-8',
#     format="%(asctime)s-[%(funcName)s:%(lineno)d]-%(levelname)s-%(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.CRITICAL,
# )

class LogInfoFilter(logging.Filter):
    def filter(self, record):
        if record.funcName.find('log_message') == -1:
            return True
        return False


logger = logging.getLogger()
fh = logging.FileHandler("access.log", encoding="utf-8", mode="a")
formatter = logging.Formatter("%(asctime)s-[%(funcName)s:%(lineno)d]-%(levelname)s-%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.CRITICAL)
logger.addFilter(LogInfoFilter())


def page_not_found(request, exception):
    switch = VulnSwitch.objects.get(module='page_not_found').mode
    # print(switch)
    if switch == 1:
        current_url = request.get_raw_uri()
        context = {
            'url': current_url
        }
        return render(request, 'admin/fake404.html', context, status=404)
    else:
        return render(request, 'admin/404.html', status=404)


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)
    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list

    }
    logger.critical("request_user:" + str(request.user))
    return render(request, 'hod_template/home_content.html', context)


def convenient_calc(request):
    switch = VulnSwitch.objects.get(module='calculated').mode
    # print(switch)
    if switch == 3:
        return render(request, 'hod_template/denied.html')
    else:
        test = {'page_title': '便捷计算器'}
        logger.critical("request_user:" + str(request.user))
        return render(request, 'hod_template/calculator.html', test)


def calculated(request):
    # print(request.user)
    # formula = request.GET['formula']
    formula = request.POST
    formula = formula['formula']
    # print(formula)
    # funcName = sys._getframe().f_code.co_name
    # print(sys._getframe().f_code.co_name)
    switch = VulnSwitch.objects.get(module='calculated').mode
    if switch == 1:
        print('1111111111111111111111111111111111111111111111')
        try:
            # result=eval(formula,{},{})
            # result=ast.literal_eval(formula)
            result = eval(formula)  # 命令注入
        except:
            result = '无效公式'
        l = {'page_title': '便捷计算器'}
        print(result)
        l['res'] = result
        return render(request, 'hod_template/calculator.html', l)
    elif switch == 2:
        try:
            result = eval(formula, {'__builtins__': None, 'abs': abs}, {'__builtins__': None, 'abs': abs})
            # result=ast.literal_eval(formula)
            # result = eval(formula)  # 命令注入
        except:
            result = '无效公式'
        l = {'page_title': '便捷计算器'}
        print(result)
        l['res'] = result
        logger.critical("request_user:" + str(request.user) + ", formula:" + str(formula) + ", result:" + str(result))
        return render(request, 'hod_template/calculator.html', l)
    elif switch == 3:
        l = {'page_title': 'Access Denied',
             'res': '-'}
        return render(request, 'hod_template/calculator.html', l)


def search(request):
    switch = VulnSwitch.objects.get(module='search').mode
    # print(switch)
    if switch == 3:
        return render(request, 'hod_template/denied.html')
    elif switch == 1:
        title = {'page_title': '数据查询'}
        logger.critical("request_user:" + str(request.user))
        return render(request, 'hod_template/search_vuln.html', title)
    elif switch == 2:
        title = {'page_title': '数据查询'}
        logger.critical("request_user:" + str(request.user))
        return render(request, 'hod_template/search_repaired.html', title)


def searchResult(request):
    switch = VulnSwitch.objects.get(module='search').mode
    if switch == 1:
        result1 = []
        con = sqlite3.connect('db.sqlite3')
        firstName = request.GET['f']
        print(firstName)
        db = con.cursor()
        print("Connected database successfully.")
        dbResult = db.execute(
            "select last_name,first_name,email,gender from main_app_customuser where first_name = '" + firstName + "'")
        for row in dbResult:
            print(row)
            result1.append(row)
        con.close()
        print(result1)
        m1 = {'m': result1,
              'page_title': '数据查询'
              # 'ln':result[0]
              }
        print(m1)
        return render(request, 'hod_template/search_vuln.html', m1)
    elif switch == 2:
        firstName = request.GET['f']
        try:
            result = CustomUser.objects.filter(Q(last_name__in=firstName) | Q(first_name__contains=firstName)
                                               | Q(last_name__contains=firstName[0],
                                                   first_name__contains=firstName[1:]))
        except Exception as e:
            messages.error(request, "搜索无效, " + str(e))
            result = ''
        print(result)
        m = {'m': result,
             'page_title': '数据查询'}
        print(m)
        logger.critical("request_user:" + str(request.user) + ", f:" + str(firstName) + ", f:" + str(result))
        return render(request, 'hod_template/search_repaired.html', m)


def upload_and_show_group_photo(request):
    form = GroupImgForm(request.POST or None, request.FILES or None)
    # content = {
    #     'form': form,
    #     'page_title': '合影与回忆'
    # }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "图片 " + str(form.cleaned_data.get('title')) + " 上传成功！")
                logger.critical(
                    "request_user:" + str(request.user) + ", imgTitle:" + str(form.cleaned_data.get('title')))
            except Exception as e:
                messages.error(request, "图片上传失败, " + str(e))
        else:
            messages.error(request, "表单无效！")
    all_img = NewGroupPhoto.objects.all()
    content = {'page_title': '合影与回忆',
               'form': form,
               'all_img': all_img}
    for u in all_img:
        print(u.groupImg.url)
        # print(u.)
    logger.critical("request_user:" + str(request.user))
    return render(request, 'hod_template/group_photo.html', content)


def add_online_teaching_url(request):
    form = OnlineTeachingURLForm(request.POST or None)
    context = {
        'form': form,
        'page_title': '在线教学平台地址添加'
    }
    if request.method == 'POST':
        if form.is_valid():
            p = form.cleaned_data.get('platform')
            u = form.cleaned_data.get('url')
            switch = VulnSwitch.objects.get(module='manage_online_teaching_url').mode
            if switch == 2:
                try:
                    URLValidator()(u)
                except ValidationError as e:
                    messages.error(request, '错误的 URL 格式！')
            elif switch == 3:
                messages.error(request, '此功能已被禁用！')
            elif switch == 1:
                try:
                    new_url = OnlineTeachingPlatformURL()
                    new_url.platform = p
                    new_url.url = u
                    new_url.save()
                    messages.success(request, p + "平台的在线教学链接已成功添加！")
                except Exception as e:
                    messages.error(request, "链接添加失败, " + str(e))
        else:
            messages.error(request, "表单无效或错误")
    logger.critical("request_user:" + str(request.user) + ", form:" + str(form))
    return render(request, 'hod_template/add_online_teaching_url.html', context)


def manage_online_teaching_url(request):
    switch = VulnSwitch.objects.get(module='manage_online_teaching_url').mode
    if switch == 1:
        all_urls = OnlineTeachingPlatformURL.objects.all()
        context = {
            'urls': all_urls,
            'page_title': '在线教学平台地址维护'
        }
        logger.critical("request_user:" + str(request.user))
        return render(request, "hod_template/manage_online_teaching_url_xss.html", context)
    elif switch == 2:
        all_urls = OnlineTeachingPlatformURL.objects.all()
        context = {
            'urls': all_urls,
            'page_title': '在线教学平台地址维护'
        }
        logger.critical("request_user:" + str(request.user))
        return render(request, "hod_template/manage_online_teaching_url.html", context)
    elif switch == 3:
        return render(request, 'hod_template/denied.html')


def delete_online_teaching_url(request, *args, **kwargs):
    de_url = get_object_or_404(OnlineTeachingPlatformURL, id=int(kwargs['id']))
    try:
        de_url.delete()
        messages.success(request, "删除成功！")
    except Exception as e:
        messages.error(request, "删除失败, " + str(e))
    logger.critical("request_user:" + str(request.user))
    return redirect(reverse('manage_online_teaching_url'))


def stu_data_parser(request):
    context = {
        'page_title': '学生XML数据解析',
        'filename_csv': 'stu.csv',
        'filename_xml': 'data.xml',
    }
    logger.critical("request_user:" + str(request.user))

    switch = VulnSwitch.objects.get(module='stu_data_parser').mode
    # print(switch)
    if switch == 3:
        return render(request, 'hod_template/denied.html')
    else:
        return render(request, "hod_template/stu_data_parser.html", context)


def stu_data_parser_result(request):
    switch = VulnSwitch.objects.get(module='stu_data_parser').mode
    if switch == 1:
        if request.method == 'POST':
            content = request.POST
            xml_data = list(content['data'].replace("\r", ""))
            # print(xml_data)
            try:
                f = open("./media/data.xml", "w", encoding='utf-8')
                for x in xml_data:
                    f.write(x)
                # f.write('\n')
                f.close()
            except IOError:
                messages.error(request, "文件读写错误, " + str(IOError))
            parser = etree.XMLParser(load_dtd=True, no_network=True)
            datalist = []
            root = {}
            all_data = ''
            try:
                tree = etree.parse("./media/data.xml", parser=parser)
                etree.dump(tree.getroot())
                root = tree.getroot()

                for i in root:
                    all_data = i.text
                for stu in root:
                    temp = [stu.attrib["id"], stu.attrib["name"], stu[0].text, stu[1].text, stu[2].text]
                    print("****")
                    print(stu)
                    # temp = ['1', '2', stu[0].text]
                    datalist.append(temp)
            except Exception as e:
                messages.warning(request, "警告：数据解析错误，您可能提交了包含错误格式的数据！\n" + repr(e))
                context = {
                    'page_title': '学生XML数据解析',
                    'filename_csv': 'stu.csv',
                    'filename_xml': 'data.xml',
                    'datalist': datalist,
                    'all_data': all_data,
                    'is_parsed': 'yes',
                }
                return render(request, "hod_template/stu_data_parser.html", context)
            try:
                f2 = open("./media/stu.csv", "w", encoding='utf-8')
                writer = csv.writer(f2)
                writer.writerows(datalist)
                f2.close()
            except IOError:
                messages.error(request, "csv文件写入错误, " + str(IOError))
            context = {
                'page_title': '学生XML数据解析',
                'datalist': datalist,
                'all_data': all_data,
                'filename_csv': 'stu.csv',
                'filename_xml': 'data.xml',
                'is_parsed': 'yes',
            }
            messages.success(request, "学生XML数据已被成功解析！")
            return render(request, "hod_template/stu_data_parser.html", context)
    elif switch == 2:
        if request.method == 'POST':
            content = request.POST
            xml_data = list(content['data'].replace("\r", ""))
            # print(xml_data)
            try:
                f = open("./media/data.xml", "w", encoding='utf-8')
                for x in xml_data:
                    f.write(x)
                # f.write('\n')
                f.close()
            except IOError:
                messages.error(request, "文件读写错误, " + str(IOError))
            parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
            datalist = []
            root = {}
            all_data = ''
            try:
                tree = etree.parse("./media/data.xml", parser=parser)
                etree.dump(tree.getroot())
                root = tree.getroot()

                for i in root:
                    all_data = i.text
                for stu in root:
                    temp = [stu.attrib["id"], stu.attrib["name"], stu[0].text, stu[1].text, stu[2].text]
                    print("****")
                    print(stu)
                    # temp = ['1', '2', stu[0].text]
                    datalist.append(temp)
            except Exception as e:
                messages.warning(request, "警告：数据解析错误，您可能提交了包含错误格式的数据！\n" + repr(e))
                context = {
                    'page_title': '学生XML数据解析',
                    'filename_csv': 'stu.csv',
                    'filename_xml': 'data.xml',
                    'datalist': datalist,
                    'all_data': all_data,
                    'is_parsed': 'yes',
                }
                return render(request, "hod_template/stu_data_parser.html", context)
            all_data = "✔ 已禁用外部实体，无相关数据"
            try:
                with open('./media/stu.csv', 'w', newline='') as f2:
                    # f2 = open("stu.csv", "w", encoding='utf-8')
                    writer = csv.writer(f2)
                    writer.writerows(datalist)
            except IOError:
                messages.error(request, "csv文件写入错误, " + str(IOError))
            context = {
                'page_title': '学生XML数据解析',
                'datalist': datalist,
                'all_data': all_data,
                'filename_csv': 'stu.csv',
                'filename_xml': 'data.xml',
                'is_parsed': 'yes'
            }
            messages.success(request, "学生XML数据已被成功解析！")
            logger.critical("request_user:" + str(request.user) + ', content:' + str(content))
            return render(request, "hod_template/stu_data_parser.html", context)


class StuFullData(object):
    ID = '08190000'
    name = '测试学生'
    gender = 'F'
    age = 19

    def __init__(self, ID, name, gender, age):
        self.name = name
        self.ID = ID
        self.gender = gender
        self.age = age

    def __reduce__(self):
        return subprocess.getoutput, (self.name,)


class StuData(object):
    ID = '08190000'
    name = '测试学生'
    gender = 'F'
    age = 19

    def __init__(self, ID, name, gender, age):
        self.name = name
        self.ID = ID
        self.gender = gender
        self.age = age


def serialize_stu_parser(request):
    switch = VulnSwitch.objects.get(module='serialize_stu_parser').mode
    if switch == 1:
        form = SerializeStuParserForm(request.POST or None)
        content = {'page_title': '序列化学生数据',
                   'form': form}
        if request.method == 'POST':
            getData = request.POST
            if 'isFullData' in getData:
                print('yes')
                stuObj = StuFullData(getData['StuId'], getData['name'], getData['gender'], getData['age'])
                serializedStu = pickle.dumps(stuObj)
                print(serializedStu)
                unSerializedStu = pickle.loads(serializedStu)
                print(unSerializedStu)
                content = {
                    'page_title': '序列化学生数据',
                    'form': form,
                    'serialization': serializedStu,
                    'Full': unSerializedStu,
                    'warning': '⚠ __reduce__() 函数已经启用，可能包含反序列化漏洞'
                }
            else:
                print('no')
                stuObj = StuData(getData['StuId'], getData['name'], getData['gender'], getData['age'])
                serializedStu = pickle.dumps(stuObj)
                print(serializedStu)
                content = {
                    'page_title': '序列化学生数据',
                    'form': form,
                    'serialization': serializedStu,
                    'warning': '✔ __reduce__() 函数未启用'
                }
        return render(request, 'hod_template/serialized_data_parser.html', content)
    elif switch == 2:
        form = SerializeStuParserForm(request.POST or None)
        content = {'page_title': '序列化学生数据',
                   'form': form}
        if request.method == 'POST':
            getData = request.POST
            stuObj = StuData(getData['StuId'], getData['name'], getData['gender'], getData['age'])
            serializedStu = pickle.dumps(stuObj)
            print(serializedStu)
            if 'isFullData' in getData:
                print('yes')
                unSerializedStu = pickle.loads(serializedStu)
                print(unSerializedStu)
                content = {
                    'page_title': '序列化学生数据',
                    'form': form,
                    'serialization': serializedStu,
                    'Full': unSerializedStu,
                    'warning': '✔ __reduce__() 函数未启用'
                }
            else:
                print('no')
                content = {
                    'page_title': '序列化学生数据',
                    'form': form,
                    'serialization': serializedStu,
                    'warning': '✔ __reduce__() 函数未启用'
                }
        logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
        return render(request, 'hod_template/serialized_data_parser.html', content)
    elif switch == 3:
        return render(request, 'hod_template/denied.html')


def download(request, *args, **kwargs):
    from django.http import FileResponse
    switch = VulnSwitch.objects.get(module='download').mode
    if switch == 1:
        downloadFile = str(kwargs['filename'])
        if downloadFile == 'stu.csv' or downloadFile == 'data.xml':
            file = open('./media/' + downloadFile, 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
            response['Content-Disposition'] = 'attachment;filename=' + '"' + downloadFile + '"'
            return response
        else:
            file = open('./fake/' + downloadFile, 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
            response['Content-Disposition'] = 'attachment;filename=' + '"' + downloadFile + '"'
            return response
    elif switch == 2:
        downloadFile = str(kwargs['filename'])
        if downloadFile == 'stu.csv' or downloadFile == 'data.xml':
            file = open('./media/' + downloadFile, 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
            response['Content-Disposition'] = 'attachment;filename=' + '"' + downloadFile + '"'
            logger.critical("request_user:" + str(request.user) + ', downloadFile:' + str(kwargs['filename']))
            return response
        else:
            return HttpResponseNotFound("File not available.")
    elif switch == 3:
        response = HttpResponseForbidden()
        return response


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name,
                    profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    return render(request, 'hod_template/add_staff_template.html', context)


def isPasswordValid(passwd):
    number = 0
    lower_num = 0
    upper_num = 0
    specialChar = 0
    invalidChar = 0

    # 字数检查
    if len(passwd) > 20 or len(passwd) < 6:
        return "不符合密码安全策略：密码长度无效"
    # 包含字符数量统计
    for s in passwd:
        if s.isdigit():
            number += 1
        elif s.islower():
            lower_num += 1
        elif s.isupper():
            upper_num += 1
        elif s == "_" or s == "&" or s == "-" or s == "@":
            specialChar += 1
        else:
            invalidChar += 1

    # 英文字母检查
    if lower_num <= 0 and upper_num <= 0:
        return "不符合密码安全策略：未包含英文字母"
    # 数字检查
    if number < 2:
        return "不符合密码安全策略：数字少于两个"
    # 特殊文字检查
    if invalidChar > 0:
        return "不符合密码安全策略：包含无效字符"
    if specialChar <= 0:
        return "不符合密码安全策略：未包含特殊字符"
    else:
        return "OK"


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            passwdPolicy = isPasswordValid(password)
            print(passwdPolicy)
            if not passwdPolicy == 'OK':
                messages.error(request, "学生添加失败, " + passwdPolicy)
                return render(request, 'hod_template/add_student_template.html', context)
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name,
                    profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    logger.critical("request_user:" + str(request.user) + ', form:' + str(student_form))
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    return render(request, 'hod_template/add_subject_template.html', context)


# def stu_exam_num_generate(request):
#     context = {'page_title': '学生准考证号生成'}
#     return render(request, "hod_template/stu_exam_number.html", context)


def stu_exam_num_generate(request):
    import datetime
    from random import randint
    form = StuExamNumberForm(request.POST or None)
    context = {
        'form': form,
        'page_title': '学生准考证号生成'}
    if request.method == 'POST':
        if form.is_valid():
            examMode = str(form.cleaned_data.get('examMode'))
            stuId = str(form.cleaned_data.get('StuId'))
            print(examMode)
            print(stuId)
            stuId1 = stuId[0:2].replace('{', '')
            stuId2 = stuId[4:].replace('}', '')
            year = str(datetime.datetime.today().year)[2:]
            r = str(randint(1000, 9999))
            examNumber = year + stuId1 + examMode + stuId2 + r
            print(examNumber)
            try:
                stuExamNum = StuExamNumber()
                stuExamNum.examMode = examMode
                stuExamNum.examNum = examNumber
                stuExamNum.StuId = stuId
                stuExamNum.save()
                print('准考证号数据库保存成功')
                # messages.success(request, "奖项添加成功")
                # return redirect(reverse('add_award'))
            except Exception as e:
                messages.error(request, "添加准考证号失败, " + str(e))
            print(request.user)
            # if str(request.user) == 'zhangxiyuan':
            result = '你好 ' + str(request.user) + ', 学生' + stuId + '的准考证号为 ' + examNumber
            print(result)
            encoder = Code128Encoder(examNumber)
            encoder.save(examNumber + '.png', bar_width=5)
            context = {
                'form': form,
                'page_title': '学生准考证号生成',
                'result': result,
                'en': examNumber
            }
            messages.success(request, '学生 ' + stuId + ' 的准考证号已成功生成！')
            # else:
            #     context = {
            #         'form': form,
            #         'page_title': '学生准考证号生成',
            #         'result': '对不起，您无权访问该模块'
            #     }
        else:
            messages.error(request, "此表单无效！")
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    return render(request, "hod_template/stu_exam_number.html", context)


def manage_stu_exam_num(request):
    examNum = StuExamNumber.objects.all()
    context = {
        'page_title': '学生准考证号管理',
        'examNum': examNum
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, 'hod_template/manage_stu_exam_num.html', context)


def delete_en(request, *args, **kwargs):
    de_en = get_object_or_404(StuExamNumber, id=int(kwargs['id']))
    logger.critical("request_user:" + str(request.user) + ', de_en:' + str(de_en))
    try:
        de_en.delete()
        messages.success(request, "删除成功！")
    except Exception as e:
        messages.error(request, "删除失败, " + str(e))
    return redirect(reverse('manage_stu_exam_num'))


def add_award(request):
    form = AwardForm(request.POST or None)
    context = {
        'form': form,
        'page_title': '添加奖项'
    }
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    if request.method == 'POST':
        if form.is_valid():
            winner = form.cleaned_data.get('winner')
            bonus = form.cleaned_data.get('bonus')
            winningDate = form.cleaned_data.get('winningDate')
            awardName = form.cleaned_data.get('awardName')
            try:
                award = Award()
                award.winner = winner
                award.bonus = bonus
                award.winningDate = winningDate
                award.awardName = awardName
                award.save()
                messages.success(request, "奖项添加成功")
                return redirect(reverse('add_award'))
            except Exception as e:
                messages.error(request, "添加奖项失败, " + str(e))
        else:
            messages.error(request, "此奖项表单无效！")
    return render(request, 'hod_template/add_award.html', context)


def manage_award(request):
    awards = Award.objects.all()
    context = {
        'page_title': '管理奖项',
        'awards': awards
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, 'hod_template/manage_award.html', context)


def delete_award(request, *args, **kwargs):
    de_award = get_object_or_404(Award, id=int(kwargs['id']))
    logger.critical("request_user:" + str(request.user) + ', de_award:' + str(de_award))
    try:
        de_award.delete()
        messages.success(request, "删除成功！")
    except Exception as e:
        messages.error(request, "删除失败, " + str(e))
    return redirect(reverse('manage_award'))


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    print(students)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    logger.critical("request_user:" + str(request.user))
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    logger.critical("request_user:" + str(request.user))
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    logger.critical("request_user:" + str(request.user) + ', form:' + str(form))
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        logger.critical("request_user:" + str(request.user))
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    logger.critical("request_user:" + str(request.user))
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    logger.critical("request_user:" + str(request.user))
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    logger.critical("request_user:" + str(request.user))
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    logger.critical("request_user:" + str(request.user))
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status": str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    # admin = get(Admin, admin=request.user)
    try:
        admin = Admin.objects.get(admin=request.user)
    except:
        context = {
            'page_title': '管理员已禁用此模块'
        }
        return render(request, "hod_template/admin_view_profile.html", context)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    logger.critical("request_user:" + str(request.user))
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    logger.critical("request_user:" + str(request.user))
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    logger.critical("request_user:" + str(request.user))
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    logger.critical("request_user:" + str(request.user))
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                       'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    logger.critical("request_user:" + str(request.user))
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                       'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request,
            "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))
