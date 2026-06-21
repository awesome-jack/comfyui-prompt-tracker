import json
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://prompt-tracker-api.3313844974.workers.dev"


def api_request(method, path, data=None):
    """发送API请求"""
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"API错误 {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"网络错误: {e.reason}")


def get_prompts():
    """获取所有提示词"""
    return api_request("GET", "/api/prompts")


def get_prompt(prompt_id):
    """获取单个提示词"""
    return api_request("GET", f"/api/prompts/{prompt_id}")


def create_prompt(title, prompt_text, negative_prompt="", model_name="", images=None):
    """创建提示词"""
    data = {
        "title": title,
        "prompt_text": prompt_text,
        "negative_prompt": negative_prompt or None,
        "model_name": model_name or None,
        "images": images or []
    }
    return api_request("POST", "/api/prompts", data)


def update_prompt(prompt_id, title=None, prompt_text=None, negative_prompt=None, model_name=None, images=None):
    """更新提示词"""
    data = {}
    if title is not None:
        data["title"] = title
    if prompt_text is not None:
        data["prompt_text"] = prompt_text
    if negative_prompt is not None:
        data["negative_prompt"] = negative_prompt
    if model_name is not None:
        data["model_name"] = model_name
    if images is not None:
        data["images"] = images
    return api_request("PUT", f"/api/prompts/{prompt_id}", data)


def delete_prompt(prompt_id):
    """删除提示词"""
    return api_request("DELETE", f"/api/prompts/{prompt_id}")


def get_highlights():
    """获取高频词"""
    return api_request("GET", "/api/highlights")


def upload_to_imgbed(file_path, imgbed_url, auth_code=""):
    """上传图片到图床"""
    import os
    
    if not os.path.exists(file_path):
        raise Exception(f"文件不存在: {file_path}")
    
    # 使用URL参数传递authCode
    url = f"{imgbed_url}/upload"
    if auth_code:
        url += f"?authCode={urllib.parse.quote(auth_code)}"
    
    # 构建multipart/form-data
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    filename = os.path.basename(file_path)
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"图床上传失败 {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"网络错误: {e.reason}")
