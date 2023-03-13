from django.contrib.auth.models import AnonymousUser
from django.http import StreamingHttpResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
import time
import json
from main_app.models import OpLogs, AccessTimeOutLogs, CustomUser
from django.contrib import admin


def wrap_streaming_content(content):
    byte = 0
    for chunk in content:
        yield len(chunk)
        byte += len(chunk)
    return byte


class OpLogsMiddleWare(MiddlewareMixin):
    __exclude_urls = []  # 定义不需要记录日志的url名单

    def __init__(self, *args):
        super(OpLogsMiddleWare, self).__init__(*args)

        # super().__init__()
        self.start_time = None  # 开始时间
        self.end_time = None  # 响应时间
        self.data = {}  # dict数据

    def process_request(self, request):
        """
        请求进入
        :param request: 请求对象
        :return:
        """

        self.start_time = time.time()  # 开始时间
        # re_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 请求时间（北京）

        # 请求IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 如果有代理，获取真实IP
            re_ip = x_forwarded_for.split(",")[0]
        else:
            re_ip = request.META.get('REMOTE_ADDR')

        # 请求方法
        re_method = request.method
        re_ua = request.headers['User-Agent']

        # 请求参数
        re_content = request.GET if re_method == 'GET' else request.POST
        if re_content:
            # 筛选空参数
            re_content = json.dumps(re_content)
        else:
            re_content = None

        self.data.update(
            {
                # 're_time': re_time,  # 请求时间
                're_url': request.path,  # 请求url
                're_method': re_method,  # 请求方法
                're_ip': re_ip,  # 请求IP
                're_content': re_content,  # 请求参数
                # 're_user': request.user.username    # 操作人(需修改)，网站登录用户
                # 're_user': 'AnonymousUser'  # 匿名操作用户测试
                're_ua': re_ua,
            }
        )

        if str(request.user) != 'AnonymousUser':
            self.data['re_user'] = CustomUser.objects.get(email=request.user.email)
        else:
            self.data['re_user'] = CustomUser.objects.get(email='AnonymousUser@zxy.link')

    def process_response(self, request, response):
        """
        响应返回
        :param request: 请求对象
        :param response: 响应对象
        :return: response
        """
        # 请求url在 exclude_urls中，直接return，不保存操作日志记录
        global rp_content
        for url in self.__exclude_urls:
            if url in self.data.get('re_url'):
                return response

        # 获取响应数据字符串(多用于API, 返回JSON字符串)
        # print(response.status_code)
        # print(response.reason_phrase)
        if isinstance(response, HttpResponse):
            # print('HttpResponse')
            rp_content = response.content.decode()
        elif isinstance(response, StreamingHttpResponse):
            rp_content = str(response.streaming_content.__sizeof__()) + ' bytes of streaming content'
            # rp_content = 'streaming content'
            # todo streaming size
            print('StreamingHttpResponse')
            print(rp_content)

        self.data['rp_content'] = rp_content
        self.data['rp_status_code'] = str(response.status_code)

        # 耗时
        self.end_time = time.time()  # 响应时间
        access_time = self.end_time - self.start_time
        self.data['access_time'] = round(access_time * 1000)  # 耗时毫秒/ms

        # 耗时大于3s的请求,单独记录 (可将时间阈值设置在settings中,实现可配置化)
        if self.data.get('access_time') > 1.5 * 1000:
            AccessTimeOutLogs.objects.create(**self.data)  # 超时操作日志入库db

        OpLogs.objects.create(**self.data)  # 操作日志入库db

        return response


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Who is the current user ?
        if user.is_authenticated:
            if user.user_type == '1':
                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))
            elif user.user_type == '2':
                if modulename == 'main_app.student_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3':
                if modulename == 'main_app.hod_views' or modulename == 'main_app.staff_views':
                    return redirect(reverse('student_home'))
            else:  # None of the aforementioned ? Please take the user to login page
                return redirect(reverse('login_page'))
        else:
            print(request.path)
            if request.path == reverse(
                    'login_page') or modulename == 'django.contrib.auth.views' or request.path == reverse('user_login') \
                    or request.path == 'eM6y7uyZSX78aL9a8/':
                print('ok')
                # If the path is login or has anything to do with authentication, pass
                pass
            # else:
            #     return redirect(reverse('login_page'))
