from django import forms
from user.models import Student, Teacher

#实现登录功能的表单（学生）
# 继承forms.Form后，拓展学生表单项的内容
class StuLoginForm(forms.Form):
    uid = forms.CharField(label='学号', max_length=10)
    password = forms.CharField(label='密码',max_length=30, widget=forms.PasswordInput)

#实现登录功能的表单（老师）
#继承forms.Form后，拓展教师表单项的内容
class TeaLoginForm(forms.Form):
        uid = forms.CharField(label='教职工号',max_length=10)
        password = forms.CharField(label='密码',max_length=30,widget=forms.PasswordInput)

#通过CBVs方法实现定制化表单
#实现注册功能的表单（学生）
class StuRegisterForm(forms.ModelForm):
    #实现拓展的确认密码的功能
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="确认密码")
    class Meta:
        model = Student
        fields = ('grade',
                  'name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')
    # 判断两次输入的密码是否相同
    def clean(self):
        # cleaned_data 就是读取表单返回的值，返回类型为字典dict型
        cleaned_data = super(StuRegisterForm, self).clean()
        # 获取表单中首次输入的密码
        password = cleaned_data.get('password')

        # 获取表单中确认的密码
        confirm_password = cleaned_data.get('confirm_password')
        # 判断首次输入的密码与确认的密码是不是一个
        if confirm_password != password:
            self.add_error('confirm_password','Password does not match')
        return cleaned_data

#实现注册功能的表单（老师）
class TeaRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(),label="确认密码");

    class Meta:
        model = Teacher
        fields = ('name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')
    def clean(self):
        cleaned_data = super(TeaRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password','Password does not match')
        return cleaned_data

#实现修改功能的表单
#修改功能的表单继承自注册功能的表单
class StuUpdateForm(StuRegisterForm):
    class Meta:
        model = Student
        fields = ('name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')
