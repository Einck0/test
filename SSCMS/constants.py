# constants.py中存放项目中用到的一系列常量
# 声明这是不支持的kind的文本
INVALID_KIND = "Invalid kind.kind should be student or teacher"
# 对非法的课程请求出现时，给出的声明内容
INVALID_REQUEST_METHOD = "Invalid request method."
# 学生选课撤课时，如果网页发送非法请求，给出声明内容
ILLEGAL_KIND = "Illegal kind for you."

COURSE_STATUS = {
    1: "未开始选课",
    2: "开始选课",
    3: "结束选课",
    4: "结课",
    5: "打分完成",
}

COURSE_OPERATION = {
    1: "开始选课",
    2: "结束选课",
    3: "结课",
    4: "给分",
    5: "查看详情"
}
