# 阿里云短信验证 API 使用指南

## API 端点

- **域名**: `dypnsapi.aliyuncs.com`
- **版本**: `2017-05-25`
- **地域**: `cn-hangzhou`

## API 列表

### 1. SendSmsVerifyCode - 发送短信验证码

**Action**: `SendSmsVerifyCode`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| PhoneNumber | String | 是 | 手机号，如 13000000000 |
| SignName | String | 是 | 短信签名名称 |
| TemplateCode | String | 是 | 短信模板 CODE |
| TemplateParam | String | 是 | 模板参数，JSON 格式，如 `{"code":"##code##","min":"5"}` |
| SchemeName | String | 否 | 方案名称，默认 "默认方案" |
| CodeLength | Integer | 否 | 验证码长度，4-8位，默认4 |
| ValidTime | Integer | 否 | 有效期(秒)，默认300 |
| Interval | Integer | 否 | 发送间隔(秒)，默认60 |
| CodeType | Integer | 否 | 验证码类型，1纯数字，2纯大写，3纯小写，4混合 |
| ReturnVerifyCode | Boolean | 否 | 是否返回验证码，默认true |

**返回参数**:

```json
{
  "Message": "OK",
  "RequestId": "...",
  "Code": "OK",
  "Success": true,
  "Model": {
    "VerifyCode": "123456",
    "BizId": "...",
    "RequestId": "..."
  }
}
```

### 2. CheckSmsVerifyCode - 核验短信验证码

**Action**: `CheckSmsVerifyCode`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| PhoneNumber | String | 是 | 手机号 |
| VerifyCode | String | 是 | 验证码 |
| SchemeName | String | 否 | 方案名称，默认 "默认方案" |

**返回参数**:

```json
{
  "Message": "OK",
  "RequestId": "...",
  "Code": "OK",
  "Success": true,
  "Model": {
    "VerifyResult": "PASS"
  }
}
```

**VerifyResult 取值**:
- `PASS`: 验证通过
- `FAIL`: 验证失败
- `UNKNOWN`: 未找到记录

## 使用示例

### Python SDK 示例

```python
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json

# 初始化
client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')

# 发送验证码
request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dypnsapi.aliyuncs.com')
request.set_method('POST')
request.set_version('2017-05-25')
request.set_action_name('SendSmsVerifyCode')

request.add_query_param('PhoneNumber', '15919313229')
request.add_query_param('SignName', '速通互联验证码')
request.add_query_param('TemplateCode', '100001')
request.add_query_param('TemplateParam', '{"code":"##code##","min":"5"}')
request.add_query_param('ReturnVerifyCode', True)

response = client.do_action_with_exception(request)
result = json.loads(response.decode('utf-8'))
verify_code = result['Model']['VerifyCode']
```

## 常见错误码

| 错误码 | 说明 |
|--------|------|
| OK | 成功 |
| isv.SMS_SIGNATURE_ILLEGAL | 签名不合法 |
| isv.SMS_TEMPLATE_ILLEGAL | 模板不合法 |
| isv.MOBILE_NUMBER_ILLEGAL | 手机号不合法 |
| Forbidden.NoPermission | 无权限 |
