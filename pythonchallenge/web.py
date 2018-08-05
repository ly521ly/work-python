from enum import Enum, unique
from datetime import datetime
import sys
import hashlib
import pymysql
from flask import Flask, request, render_template


# 第一步，设计数据表
# 数据表中应该有的信息字段：姓名，编号，性别，出生年月日，民族，政治面貌，班级职务，角色（学生，教师，管理员），用户名，密码
# user(name, id, gender, birthday, nationality, politics_status, job, role, username, password)


def executeSql(sql, params=None, isQuery=False):
    """
    负责打开和关闭数据库的操作，这也包括游标。
    负责执行SQL语句
    \n
    :param sql: 符合MySQL标准的SQL语句
    :param params: SQL语句中的参数值
    :param isQuery: 声明当前这条被执行的SQL语句是否为查询
    :return: 只有当isQuery为True时，返回查询后的结果列表，否则返回空列表
    """
    results = []
    # 打开一个数据库连接
    db_conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="test")
    db_conn.set_charset("utf8")
    with db_conn.cursor() as cursor:
        cursor.execute(sql, params)
        if isQuery:
            results = cursor.fetchall()
        db_conn.commit()
    # 关闭数据库连接
    db_conn.close()
    return results


# 如果已经存在user表，则先删除掉
# executeSql(r"DROP TABLE IF EXISTS user")
executeSql("SET NAMES utf8;")
executeSql("SET CHARACTER SET utf8;")
executeSql("SET character_set_connection=utf8;")
# 创建数据表，如果不存在的情况下
executeSql(r"CREATE TABLE IF NOT EXISTS user(id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(30),"
           r"gender VARCHAR(10), birthday DOUBLE, nationality VARCHAR(20), politics_status VARCHAR(20),"
           r"job VARCHAR(20), role VARCHAR(10) NOT NULL, username VARCHAR(30), password VARCHAR(100));")


# 新增一个注册用户
def insertUser(user):
    if isinstance(user, User):
        # 由于数据表中的ID为自增长，因此永久性传入0值
        sql = "INSERT INTO user VALUES(0, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (user.name, user.gender, user.birthday, user.nationality, user.politics_status, user.job,
                  user.role, user.username, user.password)
        # 目前这种SQL语句总感觉有点勉强，因为有很多个占位符，参数必须要严格按照先后顺序插入
        executeSql(sql, params)
        print("execute insert success. -> %s" % str(user))
    else:
        raise TypeError("存入用户失败了，当前参数对象并非一个合法的用户对象：%s" % type(user))


def pack(values):
    """
    将数据源组装成为目标对象
    \n
    :param values: 被组装的数据源，必须是一个元组
    :return: 返回被组装后的数据对象
    """
    u = User()
    u.id = values[0]
    u.name = values[1]
    # Gender[[k for k, v in Gender.__members__.items() if v.value == res[2]][0]] 根据value得到Gender
    u.gender = Gender[values[2]]
    u.birthday = datetime.fromtimestamp(values[3]).strftime("%Y-%m-%d")
    u.nationality = values[4]
    u.politics_status = values[5]
    u.job = values[6]
    u.role = Role[values[7]]
    u.username = values[8]
    u.password = values[9]
    return u


def queryUsers():
    """
    查询表中的所有数据
    :return: 返回所有的用户数据
    """

    sql = "SELECT * FROM user;"
    values = executeSql(sql=sql, isQuery=True)
    users = []
    for value in values:
        users.append(pack(value))
    return users


def queryUsersByRole(role):
    """
    根据用户角色查询对应的所有用户信息
    :param role: 要查询的用户角色
    :return: 返回查询到的用户集合，若角色不存在则返回空的集合
    """

    users = []
    if role in Role:
        sql = "SELECT * FROM user WHERE role = %s"
        params = (role.name,)
        values = executeSql(sql, params, True)
        for value in values:
            users.append(pack(value))
    return users


def queryStudents():
    """
    查询表中所有的学生信息
    :return: 返回查到的所有学生信息
    """
    return queryUsersByRole(Role.STUDENT)


def queryTeachers():
    """
    查询表中所有的教师信息
    :return: 返回查到的所有教师信息
    """
    return queryUsersByRole(Role.TEACHER)


def queryAdmins():
    """
    查询表中所有的管理员信息
    :return: 返回查到的所有管理员信息
    """
    return queryUsersByRole(Role.ADMIN)


def queryUserByuname(uname):
    """
    根据用户名查询对应的用户在本地数据表中是否存在
    \n
    :param uname: 被查询的用户名
    :return: 若存在对应的用户则返回该用户的对象，否则返回None
    """

    if not uname is None:
        sql = "SELECT * FROM user WHERE username = %s"
        params = (uname,)
        values = executeSql(sql, params, True)
        if len(values) > 0:
            return pack(values[0])
        return None


# 定义性别
@unique
class Gender(Enum):
    BOYS = 1
    GIRLS = 0


# 定义角色
@unique
class Role(Enum):
    # 学生
    STUDENT = 1
    # 教师
    TEACHER = 2
    # 管理员
    ADMIN = 3


# 用户信息模型
class User(object):

    def __init__(self):
        self.__id = 0
        self.__name = None
        self.__role = Role.STUDENT.name
        self.__gender = Gender.GIRLS.name
        self.__birthday = None
        self.__nationality = None
        self.__politics_status = None
        self.__job = None
        # 缺省设置用户名和密码一样
        self.__username = "admin"
        md5 = hashlib.md5()
        md5.update(self.__username.encode("utf-8"))
        self.__password = md5.hexdigest()

    __slots__ = ("__id", "__name", "__role", "__gender", "__birthday", "__nationality",
                 "__politics_status", "__job", "__username", "__password")

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        if not isinstance(id, int):
            raise ValueError("ID必须为整型！当前是%s" % id)
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, role):
        if not isinstance(role, Role):
            raise ValueError("角色参数有误！")
        self.__role = role.name

    @property
    def gender(self):
        return self.__gender

    @gender.setter
    def gender(self, gender):
        if not isinstance(gender, Gender):
            raise ValueError("性别参数有误！")
        self.__gender = gender.name

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, birthday):
        self.__birthday = birthday

    @property
    def nationality(self):
        return self.__nationality

    @nationality.setter
    def nationality(self, nationality):
        self.__nationality = nationality

    @property
    def politics_status(self):
        return self.__politics_status

    @politics_status.setter
    def politics_status(self, politics_status):
        self.__politics_status = politics_status

    @property
    def job(self):
        return self.__job

    @job.setter
    def job(self, job):
        self.__job = job

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        self.__username = username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        if len(password) < 6:
            raise ValueError("密码长度不得小于6位")
        self.__password = password

    def __str__(self):
        return "Name:%s|Gender:%s|Role:%s|Birthday:%s|Nationality:%s|Politics Status:%s|Job:%s|Username:%s|Password:%s" \
               % (self.name, self.gender, self.role, datetime.fromtimestamp(self.birthday), self.nationality,
                  self.politics_status, self.job, self.username, self.password)

    __repr__ = __str__


webApp = Flask(__name__)


@webApp.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@webApp.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html", gender_boys=Gender.BOYS.name, gender_girls=Gender.GIRLS.name,
                           role_admin=Role.ADMIN.name, role_teacher=Role.TEACHER.name, role_student=Role.STUDENT.name)


@webApp.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    name = request.form["name"]
    gender = request.form["gender"]
    role = request.form["role"]
    birthday = request.form["birthday"]
    nationality = request.form["nationality"]
    politics_status = request.form["politics_status"]
    job = request.form["job"]
    try:
        u = User()
        u.role = Role[role]
        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        u.password = md5.hexdigest()
        u.username = username
        u.job = job
        u.politics_status = politics_status
        u.nationality = nationality
        u.birthday = datetime.strptime(birthday, "%Y-%m-%d").timestamp()
        u.gender = Gender[gender]
        u.name = name
        insertUser(u)
        return render_template("home.html")
    except (ValueError, TypeError, RuntimeError):
        return render_template("register.html", message="Unexpected error: %s" % sys.exc_info()[1], username=username,
                               name=name)


@webApp.route("/signin", methods=["POST"])
def signin():
    username = request.form["username"]
    password = request.form["password"]
    user = queryUserByuname(username)
    if user is None:
        return render_template("home.html", message="用户%s不存在，请检查用户名" % username)
    else:
        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        if user.password == md5.hexdigest():
            roles = {Role.ADMIN.name: "管理员", Role.TEACHER.name: "教师", Role.STUDENT.name: "学生"}
            users = []
            if Role[user.role] == Role.ADMIN:
                users = queryUsers()
            elif Role[user.role] == Role.TEACHER:
                users = queryStudents()
            elif Role[user.role] == Role.STUDENT:
                users.append(user)
            return render_template("signin-ok.html", username=user.username, role=roles[user.role], users=users)
        else:
            return render_template("home.html", message="密码错了")


if __name__ == "__main__":
    webApp.run()