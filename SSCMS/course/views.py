from django.shortcuts import render
from django.http.response import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.db.models import Q
from django.utils import timezone

from user.models import Student, Teacher
from constants import INVALID_KIND,INVALID_REQUEST_METHOD,ILLEGAL_KIND

from course.models import Course, Schedule, StudentCourse
from course.forms import CourseForm,ScheduleForm


# 获取用户的基本信息
def get_user(request, kind):
    """

    :param request:
    :param kind: teacher or student
    :return: return Teacher instance or Student instance
    """
    if request.session.get('kind', '') != kind or kind not in ["student", "teacher"]:
        return None

    if len(request.session.get('user', '')) != 10:
        return None

    uid = request.session.get('user')
    if kind == "student":
        # 找到对应学生
        grade = uid[:4]
        number = uid[4:]
        student_set = Student.objects.filter(grade=grade, number=number)
        if student_set.count() == 0:
            return None
        return student_set[0]
    else:
        # 找到对应老师
        department_no = uid[:3]
        number = uid[3:]
        teacher_set = Teacher.objects.filter(department_no=department_no, number=number)
        if teacher_set.count() == 0:
            return None
        return teacher_set[0]


# Create your views here.
# 执行跳转前的基本主页（充当选择器的功能），根据不同的kind确定不同的跳转方向
def home(request, kind):
    if kind == "teacher":
        return teacher_home(request)
    elif kind == "student":
        return student_home(request)
    return HttpResponse(INVALID_KIND)



# 实现教师端的功能逻辑（包括显示课程、查看课程列表）
def teacher_home(request):
    # 功能逻辑实现前的预处理
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    info = {
        "name": user.name,
        "kind": "teacher",
    }
    # 搜索相关的设置
    is_search = False
    search_key = ""
    if request.method == "POST":
        # 获取搜索的时候用到的关键字
        search_key = request.POST.get("search")
        if search_key:
            is_search = True

    context = {"info": info}
    q = Q(teacher=user)
    # 如果当前正在搜索
    if is_search:
        q = q & Q(name__icontains=search_key)
        context["search_key"] = search_key
    # 其他情况下直接显示课程列表
    context["course_list"] = Course.objects.filter(q).order_by('status')
    return render(request, 'course/teacher/home.html', context)



def student_home(request):
    kind = "student"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind = kind)

    info = {
        "name": user.name,
        "kind": kind
    }

    context = {
        "info": info
    }

    #return render(request, 'course/nav.html', context)
    return redirect(reverse("view_course", kwargs={"view_kind": "current"}))


# 创建课程
def create_course(request):
    # 创建课程界面的预处理
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    info = {
        "name": user.name,
        "kind": "teacher",
    }

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = 1
            obj.teacher = user
            obj.save()
            return redirect(reverse("course", kwargs={"kind": "teacher"}))
    elif request.method == 'GET':
        form = CourseForm()
    else:
        return HttpResponse(INVALID_REQUEST_METHOD)

    return render(request, 'course/teacher/create_course.html', {'info': info, 'form': form})


# 实现添加课程时刻表功能
def create_schedule(request, course_id):
    #添加时刻表前的预处理
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    info = {
        "name": user.name,
        "kind": "teacher",
    }

    course = Course.objects.get(pk=course_id)

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.save()
            return redirect(reverse("view_detail", kwargs={"course_id": course_id}))
    elif request.method == 'GET':
        form = ScheduleForm()
    else:
        return HttpResponse(INVALID_REQUEST_METHOD)
    return render(request, 'course/teacher/create_schedule.html', {'info': info, 'form': form, "course": course})


# 实现删除课程时刻表功能
def delete_schedule(request, schedule_id):
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    schedule = Schedule.objects.get(pk=schedule_id)

    course_id = request.GET.get("course_id") or schedule.course.id

    schedule.delete()

    return redirect(reverse("view_detail", kwargs={"course_id": course_id}))

#实现教师端在课程主页面常规修改课程状态的逻辑
#功能包括：开始选课、结束选课、结课
def handle_course(request, course_id, handle_kind):
    """
    :param request:
    :param course_id:
    :param handle_kind:
            1: "开始选课",
            2: "结束选课",
            3: "结课",
            4: "给分完成"
    :return:
    """
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    info = {
        "name": user.name,
        "kind": "teacher",
    }

    course = Course.objects.get(pk=course_id)
    if course.status == handle_kind and course.status < 5:
        if course.status == 4:
            scs = StudentCourse.objects.filter(course=course)
            all_given = True
            res = ""
            for sc in scs:
                if sc.scores is None:
                    all_given = False
                    res += "<div>%s 未打分</div>" % sc.student

            if all_given:
                course.status += 1
                course.save()
                return redirect(reverse("view_detail", kwargs={"course_id": course.id}))
            else:
                return HttpResponse(res)
        else:
            course.status += 1
            course.save()

    course_list = Course.objects.filter(teacher=user)
    return render(request, 'course/teacher/home.html', {'info': info, 'course_list': course_list})


def view_detail(request, course_id):
    user = get_user(request, "teacher")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "teacher"}))

    info = {
        "name": user.name,
        "kind": "teacher",
    }

    course = Course.objects.get(pk=course_id)
    c_stu_list = StudentCourse.objects.filter(course=course)
    sche_list = Schedule.objects.filter(course=course)

    context = {
        "info": info,
        "course": course,
        "course_students": c_stu_list,
        "schedules": sche_list
    }

    if course.status == 5:
        sorted_cs_list = sorted(c_stu_list, key=lambda cs: cs.scores)
        context["sorted_course_students"] = sorted_cs_list

    return render(request, "course/teacher/course.html", context)

# 添加学生对课程的操作：查看课程
def view_course(request, view_kind):
    """
    :param view_kind:
        current: 查看当前课程
        is_end: 查看结课课程
        select: 选课
        withdraw: 撤课
    """
    user = get_user(request, "student")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "student"}))

    is_search = False
    search_key = ""
    if request.method == "POST":
        search_key = request.POST.get("search")
        if search_key:
            is_search = True

    info = {
        "name": user.name,
        "kind": "student",
    }

    course_list = []
    # 查看不同状态的课程
    if view_kind in ["select", "current", "withdraw", "is_end"]:
        if view_kind == "select":
            q = Q(status=2)
            if is_search:
                q = q & (Q(name__icontains=search_key) | Q(teacher__name__icontains=search_key))

            course_list = Course.objects.filter(q)

            my_course = StudentCourse.objects.filter(Q(student=user) & Q(with_draw=False))
            my_cids = [c.course.id for c in my_course]
            course_list = [c for c in course_list if c.id not in my_cids]
        else:
            q = Q(student=user) & Q(with_draw=False)
            if is_search:
                q = q & (Q(name__icontains=search_key) | Q(teacher__name__icontains=search_key))
            my_course = StudentCourse.objects.filter(q)
            if view_kind == "current":
                course_list = [c.course for c in my_course if c.course.status < 4]
            elif view_kind == "withdraw":
                course_list = [c.course for c in my_course if c.course.status == 2]
            elif view_kind == "is_end":
                course_list = [c for c in my_course if c.course.status >= 4]

    else:
        return HttpResponse(INVALID_REQUEST_METHOD)

    context = {
        'info': info,
        'view_kind': view_kind,
        'course_list': course_list
    }
    if is_search:
        context["search_key"] = search_key

    return render(request, 'course/student/home.html', context)

# 学生选课撤课的功能实现
def operate_course(request, operate_kind, course_id):
    """
    :param operate_kind:
        select: 选课
        withdraw: 撤课
    """
    # 操作前的预处理
    user = get_user(request, "student")
    if not user:
        return redirect(reverse("login", kwargs={"kind": "student"}))
    # 进行选课或者撤课的操作
    if operate_kind not in ["select", "withdraw"]:
        return HttpResponse(ILLEGAL_KIND)
    # 如果执行的是选课操作
    elif operate_kind == "select":
        course = Course.objects.filter(pk=course_id).get()
        new_course = StudentCourse(student=user, course=course)
        new_course.save()
    # 如果执行的是撤课操作
    elif operate_kind == "withdraw":
        q = Q(course__id=course_id) & Q(student=user) & Q(with_draw=False)
        course = StudentCourse.objects.filter(q).get()
        course.with_draw = True
        course.with_draw_time = timezone.now()
        course.save()
    return redirect(reverse("view_course", kwargs={"view_kind": operate_kind}))
