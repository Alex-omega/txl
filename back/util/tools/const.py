API_ROOT = "/api/v1"

PING = "/ping"
LOGIN = "/login"
REGISTER = "/register"

POST = ["POST"]

"""
+-----------+-------------+------+-----+---------+----------------+
| Field     | Type        | Null | Key | Default | Extra          |
+-----------+-------------+------+-----+---------+----------------+
| userid    | int         | NO   | PRI | NULL    | auto_increment |
| username  | varchar(64) | NO   | UNI | NULL    |                |
| e_passwd  | varchar(64) | NO   |     | NULL    |                |
| e_salt    | varchar(32) | NO   |     | NULL    |                |
| schoolid  | varchar(7)  | NO   | UNI | NULL    |                |
| confirmed | tinyint(1)  | YES  |     | 0       |                |
| vip_level | int         | YES  |     | 0       |                |
| sent_txl  | tinyint(1)  | YES  |     | 0       |                |
+-----------+-------------+------+-----+---------+----------------+
"""

GET_SALT = "SELECT e_salt FROM user_basic_info WHERE username = %s AND schoolid = %s"

IF_EXISTS = "SELECT e_salt FROM user_basic_info WHERE username = %s OR schoolid = %s"

GET_PASSWD_ID = "SELECT e_passwd, userid, confirmed FROM user_basic_info WHERE username = %s"

GET_ID = "SELECT userid FROM user_basic_info WHERE username = %s"

UPDATE_TOKEN = "UPDATE user_token SET token = %s WHERE userid = %s"

INSERT_USER = "INSERT INTO user_basic_info (username, e_passwd, e_salt, schoolid) VALUES (%s, %s, %s, %s)"
# 用于检查管理员权限
CHECK_ADMIN = "SELECT vip_level FROM user_basic_info WHERE userid = %s AND vip_level = 5"

# 用于验证用户
VERIFY_USER = "UPDATE user_basic_info SET confirmed = 1 WHERE userid = %s AND schoolid = %s"

# 用于检查目标用户存在性和当前验证状态
CHECK_USER_EXISTS = "SELECT confirmed FROM user_basic_info WHERE userid = %s AND schoolid = %s"
GET_USER_BY_TOKEN = """
    SELECT u.userid, u.username, u.vip_level 
    FROM user_basic_info u
    JOIN user_token t ON u.userid = t.userid
    WHERE t.token = %s
"""