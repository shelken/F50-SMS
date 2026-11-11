# 私有构建

本分支移除设备信息上报、个性化消息查询与已读回执，以及为这些功能生成的设备 UUID。网页不再自动查询上游更新，赞赏图片从 APK 内加载

短信转发保留。用户手动打开插件商店、检查上游更新或使用网络功能时，仍会访问对应服务。后续私有版本从本仓库的 CI 获取

## 构建

推送 `privacy/no-telemetry` 分支会运行 `.github/workflows/android-build.yml`。构建工具、依赖和缓存均位于 GitHub 托管运行器

仓库的 Actions Secrets 必须包含：

| 名称 | 内容 |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64` | PKCS12 签名密钥库的 Base64 内容，密钥别名为 `ufi-tools` |
| `ANDROID_KEYSTORE_PASSWORD` | 密钥库和私钥共用的密码 |

必须保留同一签名密钥。不得为每次构建重新生成密钥。密钥备份放在仓库忽略的 `.local/signing/` 中，不得提交到 Git

构建产物包含 APK、SHA-256 校验值、包信息和源码提交号。Actions 页面中的构建产物保留 7 天

```bash
python3 scripts/check-privacy.py
python3 scripts/check-privacy.py dist/UFI-TOOLS-private.apk
```

CI 检查源码、网页语法和 APK 内容，并验证 APK 签名。签名步骤只接收仓库 Secrets，构建步骤不接收签名密钥

## 安装

先比较现有应用与私有 APK 的签名。相同签名可以覆盖安装

```bash
adb install -r dist/UFI-TOOLS-private.apk
```

签名不同时，Android 会拒绝覆盖安装。必须先保存短信转发、登录口令和定时任务配置，再卸载原应用并安装私有 APK。卸载前必须确认备份可以恢复

应用包名保留不变。后续构建沿用固定签名，版本代码随 CI 运行编号递增
