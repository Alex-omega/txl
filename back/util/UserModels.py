import pymysql
import json
from util.tools import functions
from util.tools.const import *
from util.passwd import *

connection = pymysql.connect(
    host = "127.0.0.1",
    user = "root",
    password = MYSQL_PASSWD,
    database = "hy_txl",
    )
cursor = connection.cursor()

class LoginUser:
    def __init__(self, username: str, m_passwd: str, schoolid: str, device_hash=None):
        self.username = username
        self.m_passwd = m_passwd
        self.schoolid = schoolid

    def _login(self):
        # 获取用户的盐值
        connection.ping()
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
    def __init__(self, username: str, m_passwd: str, schoolid: str, device_hash=None):
        self.username = username
        self.m_passwd = m_passwd
        self.schoolid = schoolid
        # self.security = {}
        # self.security["device"] = device_hash
        
    def _register(self):
        connection.ping()
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
        cursor.execute(INSERT_TOOKEN)
        connection.commit()
        return 700, (userid, )
    
        
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
        connection.ping()
        cursor.execute(CHECK_ADMIN, (self.admin_userid,))
        return cursor.fetchone() is not None

    def _user_exists(self) -> tuple:
        """
        检查目标用户是否存在以及验证状态。
        :return: (status, data)
        """
        connection.ping()
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
        connection.ping()
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
        connection.ping()
        cursor.execute(GET_USER_FROM_TOKEN, (token,))
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
    
    
class User:
    @staticmethod
    def get_user_from_token(token: str):
        """
        根据 token 获取用户信息。
        """
        connection.ping()
        cursor.execute(GET_USER_BY_TOKEN, (token,))
        user = cursor.fetchone()
        if user:
            return {
                "userid": user[0],
                "username": user[1],
                "schoolid": user[2],
                "confirmed": user[3],
                "sent_txl": user[4],
            }
        return None

    @staticmethod
    def post_txl(userid: int, content: dict, is_anonymous: bool) -> tuple:
        """
        插入同学录信息，并更新用户的 `sent_txl` 字段。
        :param userid: 用户 ID
        :param content: 同学录内容（JSON 格式）
        :param is_anonymous: 是否匿名
        :return: (status, message)
        """
        try:
            # 插入同学录内容
            connection.ping()
            cursor.execute(
                "INSERT INTO txl_2025 (publisher_id, content, is_anonymous) VALUES (%s, %s, %s)",
                (userid, json.dumps(content), is_anonymous),
            )

            # 更新用户表中的 `sent_txl` 字段
            cursor.execute("UPDATE user_basic_info SET sent_txl = 1 WHERE userid = %s", (userid,))
            connection.commit()
            return 700, "TXL Posted Successfully"
        except pymysql.Error as e:
            connection.rollback()
            return 500, str(e)
        

class AdminAuth:
    @staticmethod
    def get_random_key() -> tuple:
        """
        获取当前有效的随机密码。
        :return: (status, random_key) 或 (status, None)
        """
        connection.ping()
        cursor.execute("SELECT random_key, expires_at FROM admin_auth WHERE id=1")
        result = cursor.fetchone()
        if not result:
            return 910, None  # 未找到随机密码
        
        random_key = result[0]
        return 700, random_key


def set_user_as_admin(userid: int) -> int:
    """
    将指定用户设置为管理员（会员等级提升到 5）。
    :param userid: 用户ID
    :return: status
    """
    try:
        connection.ping()
        cursor.execute("UPDATE user_basic_info SET vip_level = 5 WHERE userid = %s", (userid,))
        connection.commit()
        return 700
    except Exception:
        connection.rollback()
        return 500
