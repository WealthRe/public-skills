---
name: aliyun-sms-verifier
description: 阿里云短信验证服务，支持发送和核验验证码。安全设计：无硬编码AccessKey/手机号，内置系统赠送的签名和模板供用户选择。
metadata:
  display_name: 阿里云短信验证 (安全版)
  category: Messaging
  keywords: ["阿里云", "短信", "验证码", "SMS", "验证"]
  version: "1.2.0"
  icon: "📱"
  security_notes: "此技能不包含任何硬编码的敏感信息（AccessKey、手机号），内置系统赠送的签名和模板供用户选择"
  prerequisites: ["aliyun-python-sdk-core"]
---

# 阿里云短信验证 Skill (安全版)

基于阿里云**号码认证服务 PNVS** API 2017-05-25 的短信验证实现。安全设计，无硬编码敏感信息，内置系统赠送的签名和模板。

## 📚 官方参考文档

- **新手教程**: https://help.aliyun.com/zh/pnvs/getting-started/sms-authentication-service-novice-guide
- **短信认证参数配置**: https://dypns.console.aliyun.com/smsCertParamsConfig/sign
- **SendSmsVerifyCode API**: https://help.aliyun.com/zh/pnvs/developer-reference/api-dypnsapi-2017-05-25-sendsmsverifycode
- **CheckSmsVerifyCode API**: https://help.aliyun.com/zh/pnvs/developer-reference/api-dypnsapi-2017-05-25-checksmsverifycode

## 🔒 安全声明

**此技能不包含任何硬编码的：**
- AccessKey ID / AccessKey Secret
- 手机号

**此技能内置系统赠送的固定配置（非敏感信息）：**
- ✓ 系统赠送的短信签名列表（5个）
- ✓ 系统赠送的短信模板列表（5个）

**使用前必须由用户提供：**
1. AccessKey ID
2. AccessKey Secret
3. 目标手机号
4. 从内置列表中选择签名
5. 从内置列表中选择模板

## 📋 前置要求

### 安装依赖

```bash
pip install aliyun-python-sdk-core
```

### 阿里云控制台准备

使用前请确保已在阿里云控制台完成：
1. 开通**号码认证服务 PNVS**

参考教程：https://help.aliyun.com/zh/pnvs/getting-started/sms-authentication-service-novice-guide

参考配置页面：https://dypns.console.aliyun.com/smsCertParamsConfig/sign

## 📦 内置配置

### 系统赠送的短信签名

| 序号 | 签名名称 | 状态 |
|------|---------|------|
| 1 | 云渚科技验证平台 | ✓ 通过 |
| 2 | 云渚科技验证服务 | ✓ 通过 |
| 3 | 速通互联验证码 | ✓ 通过 |
| 4 | 速通互联验证平台 | ✓ 通过 |
| 5 | 速通互联验证服务 | ✓ 通过 |

### 系统赠送的短信模板

| 序号 | 模板CODE | 模板名称 | 模板内容 |
|------|----------|---------|---------|
| 1 | 100001 | 登录/注册模板 | 您的验证码为${code}。尊敬的客户，以上验证码${min}分钟内有效，请注意保密，切勿告知他人。 |
| 2 | 100002 | 修改绑定手机号模板 | 尊敬的客户，您正在进行修改手机号操作，您的验证码为${code}。以上验证码${min}分钟内有效，请注意保密，切勿告知他人。 |
| 3 | 100003 | 重置密码模板 | 尊敬的客户，您正在进行重置密码操作，您的验证码为${code}。以上验证码${min}分钟内有效，请注意保密，切勿告知他人。 |
| 4 | 100004 | 绑定新手机号模板 | 尊敬的客户，您正在进行绑定手机号操作，您的验证码为${code}。以上验证码${min}分钟内有效，请注意保密，切勿告知他人。 |
| 5 | 100005 | 验证绑定手机号模板 | 尊敬的客户，您正在验证绑定手机号操作，您的验证码为${code}。以上验证码${min}分钟内有效，请注意保密，切勿告知他人。 |

## 🎯 核心功能

### 1. 发送短信验证码

向指定手机号发送验证码，支持配置：
- 验证码长度（4-8位）
- 有效期（秒）
- 发送间隔（秒）
- 验证码类型（纯数字/纯字母/混合）

### 2. 核验短信验证码

核验手机号和验证码是否匹配且在有效期内。

## 📝 使用方法

### 第一步：询问用户配置

使用前必须询问用户以下信息：

```javascript
// 使用前询问用户
const config = await askUser([
  {
    key: 'access_key_id',
    question: '请输入阿里云 AccessKey ID',
    required: true
  },
  {
    key: 'access_key_secret',
    question: '请输入阿里云 AccessKey Secret',
    required: true,
    secret: true
  },
  {
    key: 'phone_number',
    question: '请输入目标手机号',
    required: true
  },
  {
    key: 'sign_name',
    question: '请选择短信签名（1-5）：\n1. 云渚科技验证平台\n2. 云渚科技验证服务\n3. 速通互联验证码\n4. 速通互联验证平台\n5. 速通互联验证服务',
    required: true,
    default: '3'
  },
  {
    key: 'template_code',
    question: '请选择短信模板（1-5）：\n1. 登录/注册模板 (100001)\n2. 修改绑定手机号模板 (100002)\n3. 重置密码模板 (100003)\n4. 绑定新手机号模板 (100004)\n5. 验证绑定手机号模板 (100005)',
    required: true,
    default: '1'
  }
]);

// 将选择转换为实际值
const SIGN_NAMES = [
  '云渚科技验证平台',
  '云渚科技验证服务',
  '速通互联验证码',
  '速通互联验证平台',
  '速通互联验证服务'
];
const TEMPLATE_CODES = ['100001', '100002', '100003', '100004', '100005'];

const selectedSignName = SIGN_NAMES[parseInt(config.sign_name) - 1];
const selectedTemplateCode = TEMPLATE_CODES[parseInt(config.template_code) - 1];
```

### 第二步：发送验证码

```python
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json

# 内置配置
SIGN_NAMES = [
    '云渚科技验证平台',
    '云渚科技验证服务',
    '速通互联验证码',
    '速通互联验证平台',
    '速通互联验证服务'
]
TEMPLATE_CODES = ['100001', '100002', '100003', '100004', '100005']

# 初始化客户端（使用用户提供的配置）
client = AcsClient(
    config['access_key_id'],
    config['access_key_secret'],
    'cn-hangzhou'
)

# 构建请求
request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dypnsapi.aliyuncs.com')
request.set_method('POST')
request.set_version('2017-05-25')
request.set_action_name('SendSmsVerifyCode')

# 设置参数
request.add_query_param('PhoneNumber', config['phone_number'])
request.add_query_param('SignName', selectedSignName)
request.add_query_param('TemplateCode', selectedTemplateCode)
request.add_query_param('TemplateParam', '{"code":"##code##","min":"5"}')
request.add_query_param('SchemeName', '默认方案')
request.add_query_param('CodeLength', 6)
request.add_query_param('ValidTime', 300)
request.add_query_param('ReturnVerifyCode', True)

# 发送请求
response = client.do_action_with_exception(request)
result = json.loads(response.decode('utf-8'))

if result.get('Success'):
    verify_code = result.get('Model', {}).get('VerifyCode')
    print(f'发送成功，验证码: {verify_code}')
```

### 第三步：核验验证码

```python
# 构建核验请求
request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dypnsapi.aliyuncs.com')
request.set_method('POST')
request.set_version('2017-05-25')
request.set_action_name('CheckSmsVerifyCode')

# 设置参数
request.add_query_param('PhoneNumber', config['phone_number'])
request.add_query_param('VerifyCode', user_input_code)
request.add_query_param('SchemeName', '默认方案')

# 发送核验请求
response = client.do_action_with_exception(request)
result = json.loads(response.decode('utf-8'))

verify_result = result.get('Model', {}).get('VerifyResult')
if verify_result == 'PASS':
    print('验证通过！')
```

## ⚙️ 参数说明

### 连接参数（必须用户提供）

| 参数 | 说明 | 示例 |
|------|------|------|
| access_key_id | 阿里云 AccessKey ID | LTAI5t... |
| access_key_secret | 阿里云 AccessKey Secret | **** |
| phone_number | 目标手机号 | 15919313229 |

### 选择参数（从内置列表选择）

| 参数 | 选项 | 说明 |
|------|------|------|
| sign_name | 1-5 | 从5个系统赠送签名中选择 |
| template_code | 1-5 | 从5个系统赠送模板中选择 |

### 发送验证码可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| scheme_name | 方案名称 | "默认方案" |
| code_length | 验证码长度 (4-8) | 6 |
| valid_time | 有效期(秒) | 300 |
| interval | 发送间隔(秒) | 60 |
| code_type | 验证码类型 | 1(纯数字) |

**验证码类型 (code_type):**
- 1: 纯数字
- 2: 纯大写字母
- 3: 纯小写字母
- 4: 数字+字母混合

### 核验结果 (VerifyResult)

| 值 | 说明 |
|----|------|
| PASS | 验证通过 |
| FAIL | 验证码错误 |
| UNKNOWN | 未找到记录 |

## 📚 参考文档

### 官方文档

- 新手教程: https://help.aliyun.com/zh/pnvs/getting-started/sms-authentication-service-novice-guide
- 短信认证参数配置: https://dypns.console.aliyun.com/smsCertParamsConfig/sign
- SendSmsVerifyCode API: https://help.aliyun.com/zh/pnvs/developer-reference/api-dypnsapi-2017-05-25-sendsmsverifycode
- CheckSmsVerifyCode API: https://help.aliyun.com/zh/pnvs/developer-reference/api-dypnsapi-2017-05-25-checksmsverifycode

## 💡 成功经验总结

### 本次实现的成功经验：

1. **API 选择正确**
   - 使用 `dypnsapi.aliyuncs.com` (号码认证服务 PNVS)
   - 而不是 `dysmsapi.aliyuncs.com` (普通短信服务)
   - PNVS 免申请资质、签名和模板，直接使用系统赠送资源

2. **正确的参数配置**
   - `TemplateParam` 必须使用 `{"code":"##code##","min":"5"}` 格式
   - `SignName` 使用系统赠送的签名（如"速通互联验证码"）
   - `TemplateCode` 使用系统赠送的模板（如"100001"）

3. **内置固定配置**
   - 系统赠送的签名和模板是固定的，内置在 skill 中
   - 用户只需从列表中选择，无需手动输入
   - 这样更方便且不易出错

4. **安全设计原则**
   - 绝不硬编码敏感信息（AccessKey、手机号）
   - AccessKey Secret 标记为 secret 类型
   - 内置配置仅包含系统赠送的非敏感资源

5. **完整的双端验证**
   - 发送验证码后立即获取验证码值
   - 支持核验功能，验证 PASS/FAIL 状态

## 📁 文件结构

```
aliyun-sms-verifier/
├── SKILL.md (本文件 - 内置签名和模板列表)
├── references/
│   └── api_guide.md (API 使用指南)
└── scripts/
    └── sms_verifier.py (核心脚本 - 内置签名和模板)
```

## 🔐 安全最佳实践

1. **敏感信息询问用户** - AccessKey、手机号必须由用户提供
2. **固定配置内置** - 系统赠送的签名模板内置供选择
3. **敏感信息加密** - AccessKey Secret 不要记录日志
4. **配置验证** - 验证用户输入的格式正确性
5. **临时凭证** - 建议使用 RAM 子用户和临时 STS Token
6. **权限最小化** - RAM 账号只授予 PNVS 相关权限

## 更新日志

### 1.2.0 (2026-02-28)

- 📝 文档：官方参考链接移至顶部显眼位置
- 📝 文档：方便其他用户快速找到官方参考

### 1.1.0 (2026-02-28)

- ✨ 改进：内置系统赠送的5个签名供用户选择
- ✨ 改进：内置系统赠送的5个模板供用户选择
- ✨ 改进：用户只需选择序号，无需手动输入签名模板
- 📝 文档：更新安全声明，明确区分敏感信息和固定配置

### 1.0.0 (2026-02-28)

- 🔒 安全设计：无任何硬编码敏感信息
- ✨ 功能：发送验证码
- ✨ 功能：核验验证码
- 📝 文档：完整的安全声明和使用指南
- 💡 总结：成功经验总结

---

**重要提示**: 使用此技能前，请确保您有合法的阿里云账号权限，并遵守相关的使用政策和安全规定。
