import json
from flask import Response

class _IResponse:
    """
    统一的响应模型，直接返回符合 Flask 的 Response 对象。
    """

    def __init__(self, status, msg, smsg=None, data=None):
        """
        初始化响应对象。
        :param status: 自定义状态（例如 "success", "error"）。
        :param msg: 描述信息。
        :param smsg: 数据中的子消息，可以是字符串或 None。
        :param data: 可选的主要数据，默认为 None。
        """
        self.status = status
        self.msg = msg
        self.data = {"smsg": smsg}  # smsg 放在 data 主体之前
        if data:
            self.data.update(data)  # 将用户提供的其他数据追加到 smsg 后

    def __call__(self):
        """
        返回响应对象，方便直接调用实例。
        :return: Flask 的 Response 对象。
        """
        response_body = json.dumps({
            "status": self.status,
            "msg": self.msg,
            "data": self.data
        }, ensure_ascii=False)  # 确保中文字符不会被转义
        return Response(
            response=response_body,
            status=200,  # 固定 HTTP 状态码为 200
            mimetype="application/json"  # 设置响应类型为 JSON
        )

class _SuccessResponse(_IResponse):
    """
    继承自 IResponse，构建固定的成功响应。
    """

    def __init__(self, smsg=None, data=None):
        """
        初始化成功响应，固定 status 为 700，msg 为 "Success"。
        :param smsg: 数据中的子消息，可以是字符串或 None。
        :param data: 可选的主要数据，默认为 None。
        """
        super().__init__(status=700, msg="Success", smsg=smsg, data=data)
        
        
def SuccessResponse(smsg=None, data=None):
    return _SuccessResponse(smsg=smsg, data=data)()

def IResponse(status, msg, smsg=None, data=None):
    return _IResponse(status=status, msg=msg, smsg=smsg, data=data)()