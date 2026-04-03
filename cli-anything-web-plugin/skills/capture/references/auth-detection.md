# 认证检测指南

本文档描述 cli-anything-web 插件中认证检测的逻辑，用于识别 Web 应用使用的认证方式。

## 1. 检测逻辑

对于每个捕获的 API 请求，分析其认证方式。系统支持两种认证模式：
- **Cookie 模式**：使用浏览器 Cookie 进行认证
- **Token 模式**：使用 localStorage 中的 token，通过自定义 Header 传递

### 1.1 Token 模式检测

检查请求头中是否包含认证 token：

| 检测条件 | 说明 |
|---------|------|
| `Access-Token` 存在 | 检查请求头中是否有自定义的 `Access-Token` 字段 |
| `Authorization: Bearer *` 存在 | 检查是否有标准 Bearer Token 认证头 |
| `X-Auth-Token` 存在 | 检查是否有自定义认证头 |

检测优先级：
1. 首先检查 `Authorization` 头（最常见的标准）
2. 然后检查 `Access-Token` 头
3. 最后检查 `X-Auth-Token` 等自定义头

**示例**：
```http
# Bearer Token 格式
GET /api/user HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 自定义 Token 头
GET /api/user HTTP/1.1
Access-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.2 Cookie 模式检测

检查请求的 Cookie 中是否包含认证相关的 Cookie：

| Cookie 名称 | 常见应用场景 |
|------------|-------------|
| `sid` | 会话 ID |
| `session` | 会话标识 |
| `token` | 认证令牌 |
| `JSESSIONID` | Java Web 应用会话 |
| `PHPSESSID` | PHP 会话 |
| `ASP.NET_SessionId` | ASP.NET 会话 |
| `connect.sid` | Connect 会话 |
| `auth_token` | 认证令牌 |
| `access_token` | 访问令牌 |

**检测规则**：
- 只要 Cookie 中包含上述任意一个认证相关名称，即判定为 Cookie 模式
- Cookie 名称匹配不区分大小写

**示例**：
```http
# 发送的 Cookie
Cookie: sid=abc123; user_id=1001; theme=dark
```

## 2. 检测结果判定

基于以上检测逻辑，按照以下规则判定认证模式：

| Token 检测 | Cookie 检测 | 判定结果 |
|-----------|------------|---------|
| 有 | 无 | `auth_mode = "token"` |
| 无 | 有 | `auth_mode = "cookie"` |
| 有 | 有 | 需要用户选择 |
| 无 | 无 | 需要用户选择 |

### 判定流程

```
开始分析请求
    │
    ▼
检测 Token 模式 ──→ 有 Token? ──是──→ 标记 token_detected = true
    │                │
    │                否
    │                │
    ▼                ▼
检测 Cookie 模式 ──→ 有 Cookie? ──是──→ 标记 cookie_detected = true
    │                │
    │                否
    │                │
    ▼                ▼
综合判定
    │
    ├── token_detected=true, cookie_detected=false ──→ auth_mode="token"
    ├── token_detected=false, cookie_detected=true ──→ auth_mode="cookie"
    ├── token_detected=true, cookie_detected=true ──→ 需要用户选择
    └── token_detected=false, cookie_detected=false ──→ 需要用户选择
```

## 3. 输出格式

### 3.1 traffic-analysis.json

检测结果写入 `traffic-analysis.json`，包含以下字段：

```json
{
  "auth_mode": "token",
  "auth_header_name": "Authorization",
  "auth_header_value_prefix": "Bearer",
  "auth_storage_key": "auth_token",
  "detected_auth_cookies": [],
  "detected_auth_headers": ["Authorization"],
  "confidence": "high",
  "requests_analyzed": 50,
  "requests_with_auth": 45
}
```

字段说明：
- `auth_mode`: 认证模式 (`token` | `cookie` | `unknown`)
- `auth_header_name`: 认证头名称（如 `Authorization`、`Access-Token`）
- `auth_header_value_prefix`: 认证头值前缀（如 `Bearer`）
- `auth_storage_key`: localStorage 中的 key 名称
- `detected_auth_cookies`: 检测到的认证相关 Cookie 列表
- `detected_auth_headers`: 检测到的认证相关 Header 列表
- `confidence`: 检测置信度 (`high` | `medium` | `low`)
- `requests_analyzed`: 分析的请求总数
- `requests_with_auth`: 包含认证信息的请求数

### 3.2 assessment.md

在 `assessment.md` 中添加认证模式标记：

```markdown
## 认证模式

- **认证方式**: Token 模式
- **认证头**: Authorization (Bearer)
- **存储键**: auth_token
- **置信度**: 高
```

## 4. 用户交互

### 4.1 需要用户选择的情况

以下情况需要提示用户选择认证模式：

1. **同时检测到两种认证方式**
   ```
   检测到同时存在 Token 和 Cookie 认证，请选择要使用的认证模式：

   [1] Token 模式
   [2] Cookie 模式
   [3] 两者都使用

   请输入选项编号：
   ```

2. **未检测到任何认证方式**
   ```
   未能自动检测到认证方式，请选择：

   [1] Token 模式（手动输入 Token）
   [2] Cookie 模式（使用浏览器 Cookie）
   [3] 无需认证（公开接口）

   请输入选项编号：
   ```

### 4.2 用户确认流程

当自动检测成功后，向用户展示检测结果并确认：

```
✓ 认证检测完成

检测结果：
- 认证模式: Token 模式
- 认证头: Authorization (Bearer)
- 存储键: auth_token
- 置信度: 高 (45/50 请求)

是否正确？[Y/n]
```

### 4.3 手动输入

如果用户选择手动输入认证信息：

**Token 模式手动输入**：
```
请输入 Token 值：________________
请输入 Token 存储的 localStorage key（默认：token）：________________
```

**Cookie 模式手动输入**：
```
请输入认证 Cookie 名称（多个用逗号分隔）：________________
示例：sid, token, JSESSIONID
```

## 5. 实际示例

### 5.1 示例 1：纯 Token 认证

捕获的请求：
```http
GET /api/profile HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

检测结果：
- Token 认证: ✓ 检测到 `Authorization: Bearer`
- Cookie 认证: ✗ 未检测到
- 判定: `auth_mode = "token"`

### 5.2 示例 2：纯 Cookie 认证

捕获的请求：
```http
GET /api/profile HTTP/1.1
Host: api.example.com
Cookie: sid=abc123xyz; user_id=1001
Content-Type: application/json
```

检测结果：
- Token 认证: ✗ 未检测到
- Cookie 认证: ✓ 检测到 `sid`
- 判定: `auth_mode = "cookie"`

### 5.3 示例 3：混合认证（需用户选择）

捕获的请求：
```http
GET /api/profile HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Cookie: theme=dark; language=zh-CN
```

检测结果：
- Token 认证: ✓ 检测到 `Authorization: Bearer`
- Cookie 认证: ✓ 检测到 Cookie（但非认证相关）
- 判定: 需要用户确认

注：此场景下 `theme` 和 `language` 是普通 Cookie，不是认证 Cookie，应该判定为 Token 模式。

## 6. 注意事项

1. **Cookie 过滤**：只有认证相关的 Cookie 才作为判定依据，普通偏好设置 Cookie（theme、language 等）应忽略
2. **多请求分析**：建议分析多个请求以提高检测准确性
3. **动态 Token**：注意 token 可能经常变化，分析时应取最新值
4. **安全存储**：Token 模式需要正确处理 localStorage 的读取

## 7. 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 无法读取 localStorage | 提示用户手动输入 token |
| 无法获取 Cookie | 提示用户确保浏览器已登录 |
| 检测结果不明确 | 引导用户手动选择 |