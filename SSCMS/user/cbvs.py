from django.shortcuts import reverse,redirect
# 引入原有的CreateView方法
from django.views.generic import  CreateView,UpdateView
# 引入已经创建的注册表单项
from user.forms import StuRegisterForm,TeaRegisterForm,StuUpdateForm
# 引入已经创建的model模型
from user.models import Student,Teacher

#引入数据更新需要的库和类
from django.views.generic import UpdateView
from user.forms import StuUpdateForm

import random

#创建继承自CreateView的视图类
class CreateStudentView(CreateView):
    model = Student
    form_class = StuRegisterForm
    template_name = "user/register.html"
    #成功后跳转的页面
    success_url = "login"

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateStudentView, self).get_context_data(**kwargs)
        context["kind"]="student"
        return context

    # form_valid的功能：生成学号=年级号+子学号
    def form_valid(self, form):
        #学生注册时选定年级自动生成学号
        #通过表单的cleaned_data属性获取学号
        grade = form.cleaned_data["grade"]
        #order_by默认升序排列，number前的负号表示降序排列
        #对现有的学生数据进行排序
        student_set = Student.objects.filter(grade=grade).order_by("-number")
        # 生成学生的编号
        if student_set.count() >0 :
            #如果不是第一个学生，则先排序
            #最后一个学生位于第一个位置
            last_student = student_set[0]
            new_number = str(int(last_student.number)+1)

            for i in range(6 - len(new_number)):
                new_number = "0" + new_number
        else:
            #如果是第一个学生
            new_number = "000001"
        #新建学生实例(不保存)
        new_student = form.save(commit=False)
        #添加学生信息（将新生成的序号加到学生数据的对应位置上
        new_student.number = new_number
        #保存学生实例
        new_student.save()
        #保存多项学生信息
        #many-to-many data
        form.save_m2m()

        self.object = new_student
        #生成学生的学号
        uid = grade + new_number
        from_url = "register"
        base_url = reverse(self.get_success_url(),kwargs={'kind':'student'})
        #完成后会返回一个HttpResponseRedirect对象
        #注册成功后，会返回到注册详情页
        return redirect(base_url + '?uid=%s&from_url=%s' % (uid, from_url))

#继承CreateView创建教师的view类
class CreateTeacherView(CreateView):
    model = Teacher
    form_class = TeaRegisterForm
    template_name = "user/register.html"
    success_url = "login"

    def post(self, request, *args,**kwargs):
        form = self.get_form()
        #判断表单的内容是否合法
        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateTeacherView,self).get_context_data(**kwargs)
        context["kind"] = "teacher"
        return  context

    def form_valid(self, form):
        #老师注册时随机生成院系号，院系号的范围为[0,300)
        department_no = random.randint(0,300)
        #把非三位数的院系号转为以0填充的字符串(比如1转为001)
        department_no = "{:0>3}".format(department_no)
        #对现有的老师进行排序
        teacher_set = Teacher.objects.filter(department_no = department_no).order_by("-number")
        if teacher_set.count()>0:
            last_teacher = teacher_set[0]
            new_number = int(last_teacher.number) + 1
            new_number = '{:0>7}'.format(new_number)
        else:
            new_number = "0000001"

        #实例化老师对象，但是不保存
        new_teacher = form.save(commit=False)
        #添加老师的信息
        new_teacher.department_no = department_no
        new_teacher.number = new_number
        #保存老师实例
        new_teacher.save()
        # 保存多项学生信息
        # many-to-many data
        form.save_m2m()

        self.object = new_teacher

        uid = department_no + new_number
        from_url = "register"
        base_url = reverse(self.get_success_url(),kwargs={'kind':'teacher'})
        return redirect(base_url + '?uid=%s&from_url=%s' % (uid,from_url))

# 修改个人信息的视图，继承自UpdateView类
class UpdateStudentView(UpdateView):
    model = Student
    form_class = StuUpdateForm
    template_name = "user/update.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateStudentView, self).get_context_data(**kwargs)
        # 用传递进来的参数的内容对某个实例的信息进行更新
        context.update(kwargs)
        # 添加类别
        context["kind"] = "student"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"kind": "student"})


class UpdateTeacherView(UpdateView):
    model = Teacher
    form_class = TeaRegisterForm
    template_name = "user/update.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateTeacherView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["kind"] = "teacher"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"kind": "teacher"})

