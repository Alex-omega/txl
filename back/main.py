from flask import *

from util.tools.const import *
from util.UserModels import *
from util.ResponseModels import *
from util.i18n import cn, en


app = Flask(__name__)
api = Blueprint('api', __name__, url_prefix=API_ROOT)


@api.route(PING)
def ping():
    return SuccessResponse("pong")


# Helper function to get the appropriate smsg dictionary
def get_smsg(lang):
    if lang == "en_US":
        return en.smsg
    return cn.smsg

# Example: Applying i18n in login route
@api.route(LOGIN, methods=POST)
def login():
    """
    用户登录接口，处理 POST 请求。
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return IResponse(status=601, msg="missing_parameters", smsg=get_smsg(None)["missing_parameters"])

        lang = request_data.get("lang", "zh_CN")
        smsg = get_smsg(lang)

        username = request_data.get("username")
        password = request_data.get("password")
        schoolid = request_data.get("schoolid")

        if not all([username, password, schoolid]):
            return IResponse(status=601, msg="missing_parameters", smsg=smsg["missing_parameters"])

        login_user = LoginUser(username=username, m_passwd=password, schoolid=schoolid)
        status_code, response_data = login_user._login()

        if status_code == 700:
            userid, token = response_data
            return SuccessResponse(smsg=smsg["login_success"], data={"userid": userid, "token": token})
        elif status_code == 801:
            return IResponse(status=801, msg="user_not_found", smsg=smsg["user_not_found"])
        elif status_code == 802:
            return IResponse(status=802, msg="invalid_password", smsg=smsg["invalid_password"])
        elif status_code == 804:
            return IResponse(status=804, msg="user_not_verified", smsg=smsg["user_not_verified"])
        else:
            return IResponse(status=500, msg="unknown_error", smsg=smsg["unknown_error"])

    except Exception:
        return IResponse(status=500, msg="internal_server_error", smsg=get_smsg(None)["internal_server_error"])


@api.route(REGISTER, methods=POST)
def register():
    """
    用户注册接口，处理 POST 请求。
    """
    # try:
    if True:
        # 从请求体中解析 JSON 数据
        request_data = request.get_json()
        if not request_data:
            return IResponse(status=601, msg="missing_parameters", smsg=get_smsg(None)["missing_parameters"])

        # 获取语言参数
        lang = request_data.get("lang", "zh_CN")
        smsg = get_smsg(lang)

        # 从请求数据中提取参数
        username = request_data.get("username")
        password = request_data.get("password")
        schoolid = request_data.get("schoolid")

        # 检查必要参数是否存在
        if not all([username, password, schoolid]):
            return IResponse(status=601, msg="missing_parameters", smsg=smsg["missing_parameters"])

        # 调用 RegisterUser 类进行注册
        register_user = RegisterUser(username=username, m_passwd=password, schoolid=schoolid)
        status_code, response_data = register_user._register()

        if status_code == 700:  # 注册成功
            userid = response_data[0]
            return SuccessResponse(
                smsg=smsg["registration_success"],
                data={"userid": userid}
            )
        elif status_code == 803:  # 用户已存在
            return IResponse(status=803, msg="user_already_exists", smsg=smsg["user_already_exists"])
        else:  # 未知错误
            return IResponse(status=500, msg="unknown_error", smsg=smsg["unknown_error"])

    # except Exception as e:
    #     # 捕获异常并返回错误响应
    #     print(e)
    return IResponse(status=500, msg="internal_server_error", smsg=get_smsg(None)["internal_server_error"])


@api.route(VERIFY, methods=['POST'])
def verify():
    """
    用户验证接口，仅允许已登录的管理员完成操作。
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return IResponse(status=601, msg="missing_parameters", smsg=get_smsg(None)["missing_parameters"])

        lang = request_data.get("lang", "zh_CN")
        smsg = get_smsg(lang)

        token = request.headers.get("Authorization")  # 从请求头获取登录令牌
        admin_user = get_user_from_token(token)

        if not admin_user:
            return IResponse(status=908, msg="admin_user_not_found", smsg=smsg["admin_user_not_found"])

        admin_userid = admin_user["userid"]
        target_userid = request_data.get("userid")
        schoolid = request_data.get("schoolid")

        if not all([target_userid, schoolid]):
            return IResponse(status=601, msg="missing_parameters", smsg=smsg["missing_parameters"])

        # 创建 VerifyUser 实例
        verifier = VerifyUser(admin_userid, target_userid, schoolid)
        status, data = verifier.verify()

        if status == 700:
            return SuccessResponse(smsg=smsg["verify_success"], data={"userid": data[0]})
        elif status == 903:
            return IResponse(status=903, msg="permission_denied", smsg=smsg["permission_denied"])
        elif status == 801:
            return IResponse(status=801, msg="user_not_found", smsg=smsg["user_not_found"])
        elif status == 901:
            return IResponse(status=901, msg="user_already_verified", smsg=smsg["user_already_verified"])

    except Exception as e:
        print(f"Error during verification: {e}")
        return IResponse(status=500, msg="internal_server_error", smsg=get_smsg(None)["internal_server_error"])


@api.route(POST_TXL, methods=['POST'])
def post_txl():
    """
    处理用户发送同学录的请求。
    """
    # 获取请求中的参数
    data = request.json
    token = data.get("token")
    content = data.get("content")
    is_anonymous = data.get("is_anonymous", 0)  # 默认为非匿名
    lang = data.get("lang", "zh_CN")

    # 设置语言
    i18n = get_smsg(lang)

    # 检查必要参数
    if not token or content is None:
        return IResponse(601, "missing_parameter", i18n["missing_parameters"])

    # 获取用户信息
    user = User.get_user_from_token(token)
    if not user:
        return IResponse(802, "invalid_token", i18n["invalid_token"])

    userid = user["userid"]
    schoolid = user["schoolid"]
    confirmed = user["confirmed"]
    sent_txl = user["sent_txl"]

    # 检查用户是否已确认
    if not confirmed:
        return IResponse(804, "unverified_user", i18n["user_not_verified"])

    # 检查学号是否以 '25' 开头
    if not schoolid.startswith("25"):
        return IResponse(902, "invalid_schoolid", i18n["invalid_schoolid_desc"])

    # 检查是否已发送过同学录
    if sent_txl:
        return IResponse(904, "already_posted", i18n["already_posted_desc"])

    # 插入同学录信息
    status, message = User.post_txl(userid, content, is_anonymous)
    if status == 700:
        return SuccessResponse(smsg=i18n["txl_posted_success"])
    else:
        return IResponse(500, "Server Error", message)


@api.route(MAKE_ADMIN, methods=['POST'])
def make_admin():
    """
    将特定用户更改为管理员。
    """
    try:
        # 获取 Headers
        super_admin_password = request.headers.get("X-Super-Admin-Password")
        random_password = request.headers.get("X-Random-Password")
        data = request.get_json()
        target_userid = data.get("userid")

        # 验证必要参数
        if not super_admin_password or not random_password or not target_userid:
            return IResponse(601, "Missing parameters", "必要参数缺失")

        # 验证超级管理员密码
        if super_admin_password != SUPER_ADMIN_PASSWD:
            return IResponse(909, "Invalid admin password", "超级管理员密码错误")

        # 验证随机密码
        status, valid_random_key = AdminAuth.get_random_key()
        if status != 700 or random_password != valid_random_key:
            return IResponse(910, "Invalid random password", "随机密码无效或已过期")

        # 更改用户为管理员
        status = set_user_as_admin(target_userid)
        if status != 700:
            return IResponse(500, "Make admin failed", "无法将目标用户设置为管理员，请稍后再试")

        return SuccessResponse("成功设置为管理员")

    except Exception as e:
        return IResponse(500, "Internal server error", f"服务器内部错误: {e}")




app.register_blueprint(api)
