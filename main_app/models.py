from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from django.utils.html import format_html


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = (('1', "Administrator"), ('2', "Staff"), ('3', "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=2)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + self.first_name


class VulnSwitch(models.Model):
    MODE = [(1, "Vulnerable"), (2, "Optimized"), (3, "Disabled")]
    id = models.AutoField(primary_key=True)
    module = models.CharField(max_length=255)
    mode = models.IntegerField(choices=MODE)
    page_url = models.CharField(max_length=127)
    action_url = models.CharField(max_length=127)
    description = models.CharField(max_length=255)
    auth = models.ForeignKey(CustomUser, to_field='email', on_delete=models.CASCADE, )

    def search_page_url(self):
        return format_html('<a href="/admin/main_app/oplogs/?q={path}&_popup=1">{path}</a>', path=self.page_url)

    search_page_url.short_description = 'page url'

    def search_action_url(self):
        return format_html('<a href="/admin/main_app/oplogs/?q={path}&_popup=1">{path}</a>', path=self.action_url)

    search_action_url.short_description = 'action url'

    def colored_mode(self):
        if self.mode == 1:
            color_code = '#8B0000'
        elif self.mode == 2:
            color_code = '#B5A642'
        elif self.mode == 3:
            color_code = '#778899'
        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            self.MODE[self.mode-1][1],
        )

    colored_mode.short_description = 'mode'

    class Meta:
        db_table = 'vuln_switch'


class OpLogs(models.Model):
    """操作日志表"""
    id = models.AutoField(primary_key=True)
    re_time = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')
    re_user = models.ForeignKey(CustomUser, blank=True, to_field='email', on_delete=models.CASCADE, max_length=32,
                                verbose_name='操作人')
    re_ip = models.CharField(max_length=32, verbose_name='请求IP')
    re_url = models.CharField(max_length=255, verbose_name='请求url')
    re_method = models.CharField(max_length=11, verbose_name='请求方法')
    re_content = models.TextField(null=True, verbose_name='请求参数')
    rp_content = models.TextField(null=True, verbose_name='响应参数')
    access_time = models.IntegerField(verbose_name='响应耗时/ms')
    rp_status_code = models.CharField(max_length=32, blank=True, verbose_name='HTTP状态码')
    re_ua = models.CharField(max_length=255, verbose_name='User-Agent')

    def colored_rp_status_code(self):
        try:
            if self.rp_status_code[0] == '1' or self.rp_status_code[0] == '2':
                color_code = 'green'
            elif self.rp_status_code[0] == '3':
                color_code = '#FFC133'
            else:
                color_code = 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color_code,
                self.rp_status_code,
            )
        except IndexError:
            print('IndexError'+self.rp_status_code)
            return self.rp_status_code

    colored_rp_status_code.short_description = 'HTTP状态码'

    # 判断指定字段长度,超出部分用省略号代替
    def update_re_content(self):
        if len(str(self.re_content)) > 35:
            return '{}...'.format(str(self.re_content)[0:35])
        else:
            return self.re_content

    update_re_content.short_description = '请求参数'

    def update_rp_content(self):
        if len(str(self.rp_content)) > 35:
            return '{}...'.format(str(self.rp_content)[0:35])
        else:
            return self.rp_content

    update_rp_content.short_description = '响应参数'

    # def update_url(self):
    #     if len(str(self.re_url)) > 35:
    #         return '{}...'.format(str(self.re_url)[0:35])
    #     else:
    #         return self.re_url

    class Meta:
        db_table = 'op_logs'


class AccessTimeOutLogs(models.Model):
    """超时操作日志表"""

    id = models.AutoField(primary_key=True)
    re_time = models.DateTimeField(auto_now_add=True, verbose_name='请求时间')
    re_user = models.ForeignKey(CustomUser, blank=True, to_field='email', on_delete=models.CASCADE, max_length=32,
                                verbose_name='操作人')
    re_ip = models.CharField(max_length=32, verbose_name='请求IP')
    re_url = models.CharField(max_length=255, verbose_name='请求url')
    re_method = models.CharField(max_length=11, verbose_name='请求方法')
    re_content = models.TextField(null=True, verbose_name='请求参数')
    rp_content = models.TextField(null=True, verbose_name='响应参数')
    access_time = models.IntegerField(verbose_name='响应耗时/ms')
    rp_status_code = models.CharField(max_length=32, blank=True, verbose_name='HTTP状态码')
    re_ua = models.CharField(max_length=255, verbose_name='User-Agent')

    def colored_rp_status_code(self):
        try:
            if self.rp_status_code[0] == '1' or self.rp_status_code[0] == '2':
                color_code = 'green'
            elif self.rp_status_code[0] == '3':
                color_code = '#FFC133'
            else:
                color_code = 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color_code,
                self.rp_status_code,
            )
        except IndexError:
            print('IndexError'+self.rp_status_code)
            return self.rp_status_code

    colored_rp_status_code.short_description = 'HTTP状态码'

    def colored_access_time(self):
        color_code = 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            self.access_time,
        )

    colored_access_time.short_description = '响应耗时/ms'

    # 判断指定字段长度,超出部分用省略号代替
    def update_re_content(self):
        if len(str(self.re_content)) > 35:
            return '{}...'.format(str(self.re_content)[0:35])
        else:
            return self.re_content

    update_re_content.short_description = '响应参数'

    def update_rp_content(self):
        if len(str(self.rp_content)) > 35:
            return '{}...'.format(str(self.rp_content)[0:35])
        else:
            return self.rp_content

    update_rp_content.short_description = '请求参数'

    class Meta:
        db_table = 'access_timeout_logs'


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OnlineTeachingPlatformURL(models.Model):
    platform = models.CharField(max_length=20)
    # url = models.URLField(max_length=200)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.platform + "," + self.url


class StuSerialization(models.Model):
    GENDER = [("M", "Male"), ("F", "Female")]
    isFullDataChoice = [("True", "True"), ("False", "False")]
    StuId = models.CharField(verbose_name='学号', max_length=8, default='08190000')
    name = models.CharField(verbose_name='姓名', max_length=100)
    age = models.PositiveIntegerField(verbose_name='年龄', default=19,
                                      validators=[MinValueValidator(1), MaxValueValidator(100)])
    gender = models.CharField(verbose_name='性别', max_length=1, choices=GENDER, default='M')
    # isFullData = models.CharField(max_length=10, choices=isFullDataChoice)
    isFullData = models.BooleanField(verbose_name='请选择是否显示全部解析数据', default=1)

    def __str__(self):
        return self.name


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Award(models.Model):
    winner = models.ForeignKey(CustomUser, verbose_name='获奖者', on_delete=models.CASCADE)
    bonus = models.DecimalField(verbose_name='奖金', max_digits=8, decimal_places=2)
    winningDate = models.DateField(verbose_name='获奖日期')
    awardName = models.CharField(max_length=120, verbose_name='奖项名称')


class StuExamNumber(models.Model):
    EXAM_TYPE = (('00', "期末考试"), ('01', "期中考试"), ('10', "课程测试"), ('11', '特种考试'))
    examMode = models.CharField(verbose_name='考试种类', max_length=2, choices=EXAM_TYPE)
    StuId = models.CharField(verbose_name='学号', max_length=8, default='08190000')
    examNum = models.CharField(default='00000000000000', max_length=20)


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NewGroupPhoto(models.Model):
    title = models.CharField(max_length=48)
    groupImg = models.ImageField(upload_to='groupImg')
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
