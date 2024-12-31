import pymysql
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
        device_hash = request_data.get("device_hash")

        if not all([username, password, schoolid, device_hash]):
            return IResponse(status=601, msg="missing_parameters", smsg=smsg["missing_parameters"])

        login_user = LoginUser(username=username, m_passwd=password, schoolid=schoolid, device_hash=device_hash)
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
    try:
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
        device_hash = request_data.get("device_hash")

        # 检查必要参数是否存在
        if not all([username, password, schoolid, device_hash]):
            return IResponse(status=601, msg="missing_parameters", smsg=smsg["missing_parameters"])

        # 调用 RegisterUser 类进行注册
        register_user = RegisterUser(username=username, m_passwd=password, schoolid=schoolid, device_hash=device_hash)
        status_code, response_data = register_user._register()

        if status_code == 700:  # 注册成功
            userid, token = response_data
            return SuccessResponse(
                smsg=smsg["registration_success"],
                data={"userid": userid, "token": token}
            )
        elif status_code == 803:  # 用户已存在
            return IResponse(status=803, msg="user_already_exists", smsg=smsg["user_already_exists"])
        else:  # 未知错误
            return IResponse(status=500, msg="unknown_error", smsg=smsg["unknown_error"])

    except Exception as e:
        # 捕获异常并返回错误响应
        return IResponse(status=500, msg="internal_server_error", smsg=get_smsg(None)["internal_server_error"])


@api.route("/verify", methods=['POST'])
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
            return IResponse(status=801, msg="user_not_found", smsg=smsg["user_not_found"])

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


app.register_blueprint(api)
