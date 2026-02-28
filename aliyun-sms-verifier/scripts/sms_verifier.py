#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阿里云短信验证核心脚本（安全版）

安全设计：
- 无硬编码 AccessKey、手机号
- 内置系统赠送的签名和模板供用户选择
"""

import json
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    ALIYUN_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_SDK_AVAILABLE = False
    logger.warning("阿里云 SDK 未安装，请运行: pip install aliyun-python-sdk-core")


# 系统赠送的固定配置（非敏感信息）
SIGN_NAMES = [
    '云渚科技验证平台',
    '云渚科技验证服务',
    '速通互联验证码',
    '速通互联验证平台',
    '速通互联验证服务'
]

TEMPLATE_CODES = [
    '100001',
    '100002',
    '100003',
    '100004',
    '100005'
]

TEMPLATE_NAMES = [
    '登录/注册模板',
    '修改绑定手机号模板',
    '重置密码模板',
    '绑定新手机号模板',
    '验证绑定手机号模板'
]


class AliyunSmsVerifier:
    """
    阿里云短信验证器（安全版）

    - 无硬编码 AccessKey、手机号
    - 内置系统赠送的签名和模板供选择
    """

    DEFAULT_REGION = "cn-hangzhou"
    DEFAULT_DOMAIN = "dypnsapi.aliyuncs.com"
    DEFAULT_API_VERSION = "2017-05-25"

    # 内置配置
    SIGN_NAMES = SIGN_NAMES
    TEMPLATE_CODES = TEMPLATE_CODES
    TEMPLATE_NAMES = TEMPLATE_NAMES

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        region_id: str = DEFAULT_REGION,
        sign_name: Optional[str] = None,
        template_code: Optional[str] = None
    ):
        """
        初始化短信验证器

        Args:
            access_key_id: 阿里云 AccessKey ID（必须由用户提供）
            access_key_secret: 阿里云 AccessKey Secret（必须由用户提供）
            region_id: 地域，默认 cn-hangzhou
            sign_name: 短信签名名称（建议从内置列表选择）
            template_code: 短信模板 CODE（建议从内置列表选择）
        """
        if not ALIYUN_SDK_AVAILABLE:
            raise RuntimeError("阿里云 SDK 未安装，请运行: pip install aliyun-python-sdk-core")

        if not access_key_id:
            raise ValueError("access_key_id 不能为空，必须由用户提供")
        if not access_key_secret:
            raise ValueError("access_key_secret 不能为空，必须由用户提供")

        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        self.sign_name = sign_name
        self.template_code = template_code

        self.client = AcsClient(access_key_id, access_key_secret, region_id)

    @classmethod
    def list_sign_names(cls):
        """获取可用的签名列表"""
        return cls.SIGN_NAMES

    @classmethod
    def list_templates(cls):
        """获取可用的模板列表（返回 CODE 和名称）"""
        return list(zip(cls.TEMPLATE_CODES, cls.TEMPLATE_NAMES))

    @classmethod
    def get_sign_name_by_index(cls, index: int):
        """通过序号获取签名（1-5）"""
        if 1 <= index <= len(cls.SIGN_NAMES):
            return cls.SIGN_NAMES[index - 1]
        raise ValueError(f"签名序号必须在 1-{len(cls.SIGN_NAMES)} 之间")

    @classmethod
    def get_template_by_index(cls, index: int):
        """通过序号获取模板（1-5）"""
        if 1 <= index <= len(cls.TEMPLATE_CODES):
            return cls.TEMPLATE_CODES[index - 1]
        raise ValueError(f"模板序号必须在 1-{len(cls.TEMPLATE_CODES)} 之间")

    def _create_request(self, action_name: str) -> CommonRequest:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.DEFAULT_DOMAIN)
        request.set_method('POST')
        request.set_version(self.DEFAULT_API_VERSION)
        request.set_action_name(action_name)
        return request

    def send_verify_code(
        self,
        phone_number: str,
        sign_name: Optional[str] = None,
        template_code: Optional[str] = None,
        template_param: str = '{"code":"##code##","min":"5"}',
        scheme_name: str = "默认方案",
        code_length: int = 6,
        valid_time: int = 300,
        interval: int = 60,
        code_type: int = 1,
        return_verify_code: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送短信验证码

        Args:
            phone_number: 手机号（必须由用户提供）
            sign_name: 短信签名名称（未提供则使用初始化值）
            template_code: 短信模板 CODE（未提供则使用初始化值）
            template_param: 模板参数，默认 '{"code":"##code##","min":"5"}'
            scheme_name: 方案名称
            code_length: 验证码长度 (4-8)
            valid_time: 有效期(秒)
            interval: 发送间隔(秒)
            code_type: 验证码类型 (1纯数字, 2纯大写, 3纯小写, 4混合)
            return_verify_code: 是否返回验证码

        Returns:
            API 响应结果
        """
        if not phone_number:
            raise ValueError("phone_number 不能为空，必须由用户提供")

        sign_name = sign_name or self.sign_name
        template_code = template_code or self.template_code

        if not sign_name:
            raise ValueError("sign_name 不能为空，请选择或提供短信签名名称")
        if not template_code:
            raise ValueError("template_code 不能为空，请选择或提供短信模板 CODE")

        request = self._create_request('SendSmsVerifyCode')

        request.add_query_param('PhoneNumber', phone_number)
        request.add_query_param('SignName', sign_name)
        request.add_query_param('TemplateCode', template_code)
        request.add_query_param('TemplateParam', template_param)
        request.add_query_param('SchemeName', scheme_name)
        request.add_query_param('CodeLength', code_length)
        request.add_query_param('ValidTime', valid_time)
        request.add_query_param('Interval', interval)
        request.add_query_param('CodeType', code_type)
        request.add_query_param('ReturnVerifyCode', return_verify_code)

        for key, value in kwargs.items():
            if value is not None:
                request.add_query_param(key, value)

        try:
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))
            logger.info(f"发送验证码成功")
            return result
        except Exception as e:
            logger.error(f"发送验证码失败: {str(e)}")
            return {
                "Success": False,
                "Message": str(e),
                "Code": "Error"
            }

    def check_verify_code(
        self,
        phone_number: str,
        verify_code: str,
        scheme_name: str = "默认方案"
    ) -> Dict[str, Any]:
        """
        核验短信验证码

        Args:
            phone_number: 手机号（必须由用户提供）
            verify_code: 验证码（必须由用户提供）
            scheme_name: 方案名称

        Returns:
            API 响应结果，Model.VerifyResult 为 "PASS" 表示通过
        """
        if not phone_number:
            raise ValueError("phone_number 不能为空")
        if not verify_code:
            raise ValueError("verify_code 不能为空")

        request = self._create_request('CheckSmsVerifyCode')

        request.add_query_param('PhoneNumber', phone_number)
        request.add_query_param('VerifyCode', verify_code)
        request.add_query_param('SchemeName', scheme_name)

        try:
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))

            verify_result = result.get('Model', {}).get('VerifyResult', 'UNKNOWN')
            if verify_result == 'PASS':
                logger.info("验证码核验通过")
            else:
                logger.warning(f"验证码核验失败: {verify_result}")

            return result
        except Exception as e:
            logger.error(f"核验验证码失败: {str(e)}")
            return {
                "Success": False,
                "Message": str(e),
                "Code": "Error"
            }


def main():
    """
    交互演示（安全版）

    - 无硬编码敏感信息
    - 内置签名和模板供选择
    """
    import sys

    print("=" * 60)
    print("阿里云短信验证 - 交互式演示（安全版）")
    print("=" * 60)
    print()
    print("提示: 无硬编码敏感信息，AccessKey/手机号需您提供")
    print("      签名和模板已内置，请从列表选择")
    print()

    # 询问用户配置
    print("请输入配置信息：")
    print("-" * 40)

    try:
        access_key_id = input("AccessKey ID: ").strip()
        if not access_key_id:
            print("错误: AccessKey ID 不能为空")
            return

        access_key_secret = input("AccessKey Secret: ").strip()
        if not access_key_secret:
            print("错误: AccessKey Secret 不能为空")
            return

        phone_number = input("目标手机号: ").strip()
        if not phone_number:
            print("错误: 手机号不能为空")
            return

        print()
        print("请选择短信签名（1-5）:")
        for i, name in enumerate(SIGN_NAMES, 1):
            print(f"  {i}. {name}")

        sign_choice = input("请输入序号 [默认: 3]: ").strip()
        if not sign_choice:
            sign_choice = "3"

        try:
            sign_idx = int(sign_choice)
            sign_name = SIGN_NAMES[sign_idx - 1]
        except (ValueError, IndexError):
            print("错误: 无效的序号，使用默认值")
            sign_name = SIGN_NAMES[2]

        print()
        print("请选择短信模板（1-5）:")
        for i, (code, name) in enumerate(zip(TEMPLATE_CODES, TEMPLATE_NAMES), 1):
            print(f"  {i}. {name} ({code})")

        tpl_choice = input("请输入序号 [默认: 1]: ").strip()
        if not tpl_choice:
            tpl_choice = "1"

        try:
            tpl_idx = int(tpl_choice)
            template_code = TEMPLATE_CODES[tpl_idx - 1]
        except (ValueError, IndexError):
            print("错误: 无效的序号，使用默认值")
            template_code = TEMPLATE_CODES[0]

    except KeyboardInterrupt:
        print("\n\n取消")
        return

    print()
    print("-" * 40)
    print(f"使用签名: {sign_name}")
    print(f"使用模板: {template_code}")
    print("初始化验证器...")

    try:
        verifier = AliyunSmsVerifier(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            sign_name=sign_name,
            template_code=template_code
        )
    except Exception as e:
        print(f"错误: {e}")
        return

    print(f"向 {phone_number} 发送验证码...")
    result = verifier.send_verify_code(
        phone_number=phone_number,
        code_length=6,
        valid_time=300
    )

    if result.get('Success'):
        model = result.get('Model', {})
        verify_code = model.get('VerifyCode')
        print(f"✓ 发送成功")
        if verify_code:
            print(f"  验证码: {verify_code}")

        print()
        while True:
            try:
                user_input = input("请输入收到的验证码核验 (q 退出): ").strip()
            except KeyboardInterrupt:
                print("\n\n退出")
                break

            if user_input.lower() == 'q':
                break

            if not user_input:
                continue

            check = verifier.check_verify_code(phone_number, user_input)
            verify_result = check.get('Model', {}).get('VerifyResult', 'UNKNOWN')

            print(f"结果: {verify_result}")
            if verify_result == 'PASS':
                print("✓ 验证通过！")
                break
    else:
        print(f"✗ 发送失败: {result.get('Message')}")


if __name__ == '__main__':
    main()
