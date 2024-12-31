import pymysql
from util.tools import functions
from util.tools.const import *
from util.passwd import *

connection = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = mysql_passwd,
    database = "hy_txl",
    )
cursor = connection.cursor()

class LoginUser:
    def __init__(self, username: str, m_passwd: str, schoolid: str, device_hash: str):
        self.username = username
        self.m_passwd = m_passwd
        self.schoolid = schoolid

    def _login(self):
        # 获取用户的盐值
        cursor.execute(GET_SALT, (self.username, self.schoolid,))
        result = cursor.fetchone()
        if not result:
            return 801, ()  # 用户名或学号错误

        salt = result[0]

        # 加密用户输入的密码
        n_e_passwd = functions.encrypt(self.m_passwd + salt)

        # 获取数据库中存储的加密密码和用户ID
        cursor.execute(GET_PASSWD_ID, (self.username,))
        user_info = cursor.fetchone()
        if not user_info:
            return 801, ()  # 用户名或学号错误

        e_passwd, userid, confirmed = user_info  # 获取确认状态

        # 验证密码
        if e_passwd != n_e_passwd:
            return 802, ()  # 密码错误

        # 检查是否已验证
        if not confirmed:
            return 804, ()  # 用户未验证

        # 生成新令牌并更新数据库
        new_token = functions.random_str(64)
        cursor.execute(UPDATE_TOKEN, (new_token, userid))
        connection.commit()

        return 700, (userid, new_token,)
            
            
class RegisterUser:
    def __init__(self, username: str, m_passwd: str, schoolid: str, device_hash: str):
        self.username = username
        self.m_passwd = m_passwd
        self.schoolid = schoolid
        # self.security = {}
        # self.security["device"] = device_hash
        
    def _register(self):
        cursor.execute(IF_EXISTS, (self.username, self.schoolid, ))
        result = cursor.fetchone()
        if result:
            return 803, ()
        salt = functions.random_str(32)
        e_passwd = functions.encrypt(self.m_passwd + salt)
        cursor.execute(INSERT_USER, (self.username, e_passwd, salt, self.schoolid, ))
        connection.commit()
        cursor.execute(GET_ID, (self.username, ))
        userid = cursor.fetchone()[0]
        new_token = functions.random_str(64)
        cursor.execute(UPDATE_TOKEN, (new_token, userid))
        connection.commit()
        return 700, (userid, new_token, )
    
        
class VerifyUser:
    """
    处理用户验证的逻辑。
    仅允许会员等级为 5 的管理员完成操作。
    """

    def __init__(self, admin_userid: int, target_userid: int, schoolid: str):
        self.admin_userid = admin_userid  # 当前管理员的 ID
        self.target_userid = target_userid  # 目标用户的 ID
        self.schoolid = schoolid  # 目标用户的学号

    def _is_admin(self) -> bool:
        """
        检查当前用户是否为管理员。
        :return: 如果是管理员，返回 True；否则返回 False。
        """
        cursor.execute(CHECK_ADMIN, (self.admin_userid,))
        return cursor.fetchone() is not None

    def _user_exists(self) -> tuple:
        """
        检查目标用户是否存在以及验证状态。
        :return: (status, data)
        """
        cursor.execute(CHECK_USER_EXISTS, (self.target_userid, self.schoolid))
        result = cursor.fetchone()
        if result:
            self.confirmed = result[0]  # 获取验证状态
            return 700, ()
        return 801, ()

    def verify(self) -> tuple:
        """
        执行用户验证操作。
        :return: (status, data)
        """
        # 检查管理员权限
        if not self._is_admin():
            return 903, ()

        # 检查目标用户是否存在
        status, _ = self._user_exists()
        if status != 700:
            return status, ()

        # 检查用户是否已验证
        if self.confirmed:
            return 901, ()

        # 验证目标用户
        cursor.execute(VERIFY_USER, (self.target_userid, self.schoolid))
        connection.commit()
        return 700, (self.target_userid,)



def get_user_from_token(token: str):
    """
    根据提供的 token 获取用户信息。
    :param token: 要验证的 token
    :return: 如果 token 有效且对应的用户存在，返回用户信息字典；否则返回 None。
    """
    try:
        # 执行 SQL 查询
        cursor.execute(GET_USER_BY_TOKEN, (token,))
        user = cursor.fetchone()

        if user:
            # 返回用户信息
            return {
                "userid": user[0],
                "username": user[1],
                "vip_level": user[2]
            }
        return None
    except Exception as e:
        # 处理任何异常，返回 None
        print(f"Error fetching user from token: {e}")
        return None