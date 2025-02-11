from django import forms
from .models import Course, Schedule, StudentCourse


# 创建课程的表单
class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        exclude = ['status', 'teacher']


#创建时刻表的表单
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ["course"]

#创建打分的表单
class ScoreForm(forms.ModelForm):
    class Meta:
        model = StudentCourse
        fields = ["student", "course", "scores", "comments"]

    student = forms.CharField(label="学生", disabled=True)
    # course = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    course = forms.CharField(label="课程", disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['student'] = self.instance.student
        self.initial['course'] = self.instance.course

    def clean_student(self):
        return self.initial['student']

    def clean_course(self):
        return self.initial['course']


#学生对老师评价的表单
class RateForm(forms.ModelForm):
    class Meta:
        model = StudentCourse
        fields = ["course", "scores", "comments", "rating", "assessment"]

    course = forms.CharField(label="课程", disabled=True)
    scores = forms.IntegerField(label="成绩", disabled=True)
    comments = forms.CharField(label="老师评价", disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['course'] = self.instance.course
        self.initial['scores'] = self.instance.scores
        self.initial['comments'] = self.instance.comments

    def clean_course(self):
        return self.initial['course']

    def clean_scores(self):
        return self.initial['scores']

    def clean_comments(self):
        return self.initial['comments']