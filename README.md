# ComfyUI Prompt Tracker 节点

与 Prompt Tracker API 集成的 ComfyUI 自定义节点，支持上传、下载提示词，并支持图床上传图片。

## 安装方法

1. 将整个 `comfyui-prompt-tracker` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录
2. 重启 ComfyUI

## 节点说明

### 1. Prompt Tracker 上传
将 ComfyUI 的提示词和图片上传到 Prompt Tracker API

**输入：**
- `title`：提示词标题
- `positive_prompt`：正向提示词
- `negative_prompt`：负面提示词（可选）
- `model_name`：模型名称（可选）
- `image`：图片输入（可选，连接VAE Decode的IMAGE输出）
- `imgbed_url`：图床地址（可选，如 `https://img.example.com`）
- `imgbed_auth`：图床认证码（可选）
- `auto_upload`：是否自动上传

**输出：**
- `status`：上传状态
- `prompt_id`：上传后的提示词ID
- `image_url`：上传后的图片URL（如果上传了图片）

### 2. Prompt Tracker 下载
从 API 下载指定ID的提示词

**输入：**
- `prompt_id`：提示词ID
- `auto_download`：是否自动下载

**输出：**
- `title`：标题
- `positive_prompt`：正向提示词
- `negative_prompt`：负面提示词
- `model_name`：模型名称
- `status`：下载状态

### 3. Prompt Tracker 选择
从列表中可视化选择提示词

**输入：**
- `prompt_select`：下拉列表选择
- `refresh`：刷新列表

**输出：**
- 同下载节点

### 4. Prompt Tracker 列表
获取并显示所有提示词列表

**输入：**
- `refresh`：是否刷新
- `search_keyword`：搜索关键词

**输出：**
- `list_text`：格式化的列表文本

## 使用示例

### 上传提示词和图片
```
[KSampler] → [VAE Decode] → [Prompt Tracker 上传]
                                    ↓
                              [显示状态]
```

### 下载提示词使用
```
[Prompt Tracker 选择] → [CLIP Text Encode (Positive)]
                      → [CLIP Text Encode (Negative)]
```

## 图床配置

支持对接 CloudFlare-ImgBed 等图床服务：

1. 在节点中填写 `imgbed_url`（如 `https://img.example.com`）
2. 如果需要认证，填写 `imgbed_auth`
3. 连接图片输入（VAE Decode 的 IMAGE 输出）

图片会自动上传到图床，返回的URL会保存到提示词记录中。

## API 地址

默认API地址：`https://prompt-tracker-api.3313844974.workers.dev`

如需修改，编辑 `api_client.py` 文件中的 `API_BASE` 变量。
