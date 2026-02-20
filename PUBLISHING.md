# 发布到 PyPI 指南

本项目支持两种发布方式：
- **自动发布**（推荐）：通过 GitHub Actions 自动发布
- **手动发布**：本地构建并上传

## 前置准备

### 1. 注册 PyPI 账号
- 正式环境：https://pypi.org/account/register/
- 测试环境：https://test.pypi.org/account/register/

### 2. 安装发布工具
```bash
pip install --upgrade pip setuptools wheel twine build
```

### 3. 配置 PyPI 凭证
创建 `~/.pypirc` 文件：
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-test-api-token-here
```

## 发布前检查清单

- [ ] 更新 `setup.py` 中的作者信息（author, author_email）
- [ ] 更新 `pyproject.toml` 中的作者信息
- [ ] 更新 `LICENSE` 文件中的版权信息
- [ ] 更新 `Block/__init__.py` 中的版本号
- [ ] 确认包名 `block-protocol` 在 PyPI 上可用（或修改为其他名称）
- [ ] 更新 GitHub 仓库地址（如果有）
- [ ] 确保 README.md 内容完整且格式正确
- [ ] 删除或排除敏感文件（密钥.yaml 等）

## 手动发布步骤

如果需要手动发布（不推荐，建议使用自动发布）：

### 1. 清理旧的构建文件
```bash
rm -rf build/ dist/ *.egg-info/
```

### 2. 构建分发包
```bash
python -m build
```
这会在 `dist/` 目录生成：
- `.tar.gz` 源码包
- `.whl` wheel 包

### 3. 检查包的完整性
```bash
twine check dist/*
```

### 4. 先发布到测试环境（推荐）
```bash
twine upload --repository testpypi dist/*
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ blocklink
```

### 5. 发布到正式 PyPI
确认测试环境没问题后：
```bash
twine upload dist/*
```

### 6. 验证发布
```bash
pip install blocklink
```

## 版本管理

### 更新版本号
修改以下文件中的版本号：
- `Block/__init__.py` 中的 `__version__`
- `setup.py` 中的 `version`

版本号规范（语义化版本）：
- `0.1.0` - 初始版本
- `0.1.1` - 补丁版本（bug 修复）
- `0.2.0` - 次版本（新功能）
- `1.0.0` - 主版本（重大变更）

### 发布新版本
```bash
# 1. 更新版本号
# 2. 提交代码
git add .
git commit -m "Release v0.1.1"
git tag v0.1.1
git push origin main --tags

# 3. 清理并重新构建
rm -rf build/ dist/ *.egg-info/
python -m build

# 4. 上传新版本
twine upload dist/*
```

## 常见问题

### 包名已被占用
如果 `blocklink` 已被占用，可以修改为：
- `blocklink-network`
- `blocklink-framework`
- `yourname-blocklink`
- 或其他唯一的名称

修改位置：
- `setup.py` 中的 `name`
- `pyproject.toml` 中的 `name`

### 上传失败
- 检查 API token 是否正确
- 确认版本号未重复（PyPI 不允许覆盖已发布的版本）
- 检查网络连接

### 依赖问题
确保 `requirements.txt` 和 `setup.py` 中的依赖版本一致。

## 自动发布（推荐）

### 配置 GitHub Actions 自动发布

项目已配置 GitHub Actions 工作流，可以在推送 tag 时自动发布到 PyPI。

#### 1. 设置 PyPI API Token

1. 登录 [PyPI](https://pypi.org/)
2. 进入 Account Settings → API tokens
3. 创建新的 API token（选择 "Entire account" 或指定项目）
4. 复制生成的 token（格式：`pypi-...`）

#### 2. 添加 GitHub Secret

1. 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: 粘贴你的 PyPI API token
5. 点击 "Add secret"

#### 3. 发布新版本

```bash
# 1. 更新版本号
# 编辑 blocklink/__init__.py 中的 __version__

# 2. 提交代码
git add .
git commit -m "Release v0.1.1"

# 3. 创建并推送 tag
git tag v0.1.1
git push origin main
git push origin v0.1.1

# GitHub Actions 会自动：
# - 构建包
# - 检查包完整性
# - 发布到 PyPI
```

#### 4. 监控发布状态

- 进入 GitHub 仓库 → Actions 标签
- 查看 "Publish to PyPI" 工作流运行状态
- 如果失败，检查日志排查问题

### 使用 GitHub Release 发布

也可以通过创建 GitHub Release 触发自动发布：

1. 进入 GitHub 仓库 → Releases → "Create a new release"
2. 选择或创建 tag（如 v0.1.1）
3. 填写 Release 标题和说明
4. 点击 "Publish release"
5. GitHub Actions 自动发布到 PyPI

## 最佳实践

1. 始终先在 TestPyPI 测试
2. 使用 API token 而非密码
3. 遵循语义化版本规范
4. 每次发布前运行测试
5. 保持 README 和文档更新
6. 使用 Git tags 标记版本
7. 编写 CHANGELOG.md 记录变更
8. 使用 GitHub Actions 自动化发布流程
9. 在 GitHub Release 中记录版本变更

## 参考资源

- PyPI 官方文档：https://packaging.python.org/
- Twine 文档：https://twine.readthedocs.io/
- 语义化版本：https://semver.org/lang/zh-CN/
