from django.shortcuts import render,reverse,redirect
from django.http.response import HttpResponse
from django.views.generic import CreateView
#引入kind无效时的显示信息
from constants import INVALID_KIND
#引入继承后的表单类
from user.forms import StuLoginForm,TeaLoginForm
from user.cbvs import CreateStudentView,CreateTeacherView,UpdateStudentView,UpdateTeacherView
#引入模型
from user.models import Student, Teacher



def home(request):
    return render(request,"user/login_home.html")


def login(request, *args, **kwargs):
    #判断kind变量的内容是否是规定的student和teacher
    # if not kwargs or kwargs.get("kind","") not in ["student","teacher"]:
    #     return HttpResponse(INVALID_KIND)
    if not kwargs or "kind" not in kwargs or kwargs["kind"] not in ["teacher", "student"]:
        return HttpResponse(INVALID_KIND)

    kind = kwargs["kind"]
    #context = {"kind":kind}
    if kind not in ["teacher", "student"]:
        return HttpResponse(INVALID_KIND)


    if request.method == 'POST':
        #传递用户提交的信息
        if kind == "teacher":
            form = TeaLoginForm(data=request.POST)
        else:
            form = StuLoginForm(data=request.POST)

        #对表单进行数据检查
        if form.is_valid():
            # 表单内数据合法
            # 取出表单内的数据（用户名）并显示hello+用户名
            uid = form.cleaned_data["uid"]
            if len(uid) != 10:
                # 如果账户数据的长度不合法
                form.add_error("uid", "账号长度必须为10")

            #temp_res = "hello,%s" % uid
            #return HttpResponse(temp_res)
            else:
                # 如果账户数据的长度合法
                if kind == "teacher":
                    department_no = uid[:3]
                    number = uid[3:]
                    object_set = Teacher.objects.filter(department_no=department_no, number=number)
                else:
                    grade = uid[:4]
                    number = uid[4:]
                    object_set = Student.objects.filter(grade=grade, number=number)
                # 检查是否已经注册
                if object_set.count() == 0: #没有注册
                    form.add_error("uid", "该账号不存在.")
                else: #已经注册
                    user = object_set[0]
                    # 检查密码是否匹配
                    if form.cleaned_data["password"] != user.password:
                        form.add_error("password", "密码不正确.")
                    else:
                        request.session['kind'] = kind
                        request.session['user'] = uid
                        request.session['id'] = user.id

                        return redirect("course", kind=kind)
            # 登录成功，跳转到个人主页，通过cookie保存登录信息
            return render(request, 'user/login_detail.html', {'form': form, 'kind': kind})

    else:
        context = {'kind': kind}
        if request.GET.get('uid'):
            uid = request.GET.get('uid')
            context['uid'] = uid
            if kind == "teacher":
                form = TeaLoginForm({"uid": uid, 'password': '12345678'})
            else:
                form = StuLoginForm({"uid": uid, 'password': '12345678'})
        else:
            if kind == "teacher":
                form = TeaLoginForm()
            else:
                form = StuLoginForm()
        context['form'] = form
        if request.GET.get('from_url'):
            context['from_url'] = request.GET.get('from_url')

        return render(request, 'user/login_detail.html', context)


# 实现注册视图的方法
def register(request, kind):
    func = None
    if kind == "student":
        func = CreateStudentView.as_view()
    elif kind == "teacher":
        func = CreateTeacherView.as_view()

    if func:
        return func(request)
    else:
        return HttpResponse(INVALID_KIND)


# 实现退出登录
def logout(request):
    if request.session.get("kind", ""):
        del request.session["kind"]
    if request.session.get("user", ""):
        del request.session["user"]
    if request.session.get("id", ""):
        del request.session["id"]
    return redirect(reverse("login"))

#实现修改信息的功能
def update(request, kind):
    func = None
    # 根据kind的类型，确定生成不同的实例
    if kind == "student":
        func = UpdateStudentView.as_view()
    elif kind == "teacher":
        func = UpdateTeacherView.as_view()
    else:
        return HttpResponse(INVALID_KIND)

    pk = request.session.get("id")
    if pk:
        context = {
            "name": request.session.get("name", ""),
            "kind": request.session.get("kind", "")
        }
        return func(request, pk=pk, context=context)

    return redirect("login")


