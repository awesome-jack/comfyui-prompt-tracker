import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

try:
    import folder_paths
except ImportError:
    folder_paths = None

# API配置
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


class PromptTrackerUpload:
    """上传提示词到Prompt Tracker API（支持图床上传图片）"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "title": ("STRING", {"default": "ComfyUI生成", "multiline": False}),
                "positive_prompt": ("STRING", {"multiline": True, "placeholder": "正向提示词"}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "placeholder": "负面提示词"}),
                "model_name": ("STRING", {"default": "", "multiline": False, "placeholder": "模型名称"}),
                "image": ("IMAGE",),
                "imgbed_url": ("STRING", {"default": "https://image.6677811.xyz", "multiline": False, "placeholder": "图床地址"}),
                "imgbed_auth": ("STRING", {"default": "", "multiline": False, "placeholder": "图床认证码（可选）"}),
                "auto_upload": ("BOOLEAN", {"default": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("status", "prompt_id", "image_url")
    FUNCTION = "upload"
    CATEGORY = "Prompt Tracker"
    OUTPUT_NODE = True
    
    def upload(self, title, positive_prompt, negative_prompt="", model_name="", image=None, imgbed_url="", imgbed_auth="", auto_upload=True, unique_id=""):
        if not auto_upload:
            return ("已禁用自动上传", -1, "")
        
        image_urls = []
        
        # 如果有图片且配置了图床，先上传图片
        if image is not None and imgbed_url:
            try:
                # 保存临时图片
                if folder_paths:
                    temp_dir = folder_paths.get_temp_directory()
                else:
                    temp_dir = os.path.join(os.path.expanduser("~"), "comfyui_temp")
                    os.makedirs(temp_dir, exist_ok=True)
                
                temp_path = os.path.join(temp_dir, f"prompt_tracker_{unique_id}.png")
                
                # 将tensor转为PIL图片并保存
                from PIL import Image
                import numpy as np
                
                # ComfyUI的图片格式是 [batch, height, width, channels]
                img_array = image[0].cpu().numpy()
                img_array = (img_array * 255).astype(np.uint8)
                pil_image = Image.fromarray(img_array)
                pil_image.save(temp_path)
                
                # 上传到图床
                result = upload_to_imgbed(temp_path, imgbed_url, imgbed_auth)
                image_urls.append(result)
                
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                return (f"图片上传失败: {str(e)}", -1, "")
        
        # 上传提示词到API
        try:
            result = create_prompt(
                title=title,
                prompt_text=positive_prompt,
                negative_prompt=negative_prompt,
                model_name=model_name,
                images=image_urls
            )
            prompt_id = result.get("id", -1)
            image_url = image_urls[0] if image_urls else ""
            return (f"上传成功! ID: {prompt_id}", prompt_id, image_url)
        except Exception as e:
            return (f"上传失败: {str(e)}", -1, "")


class PromptTrackerDownload:
    """从Prompt Tracker API下载提示词"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_id": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
            "optional": {
                "auto_download": ("BOOLEAN", {"default": True}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("title", "positive_prompt", "negative_prompt", "model_name", "status")
    FUNCTION = "download"
    CATEGORY = "Prompt Tracker"
    
    def download(self, prompt_id, auto_download=True):
        if not auto_download:
            return ("", "", "", "", "已禁用自动下载")
        
        if prompt_id <= 0:
            return ("", "", "", "", "请输入有效的提示词ID")
        
        try:
            prompt = get_prompt(prompt_id)
            return (
                prompt.get("title", ""),
                prompt.get("prompt_text", ""),
                prompt.get("negative_prompt", "") or "",
                prompt.get("model_name", "") or "",
                f"下载成功: {prompt.get('title', '')}"
            )
        except Exception as e:
            return ("", "", "", "", f"下载失败: {str(e)}")


class PromptTrackerSelect:
    """从Prompt Tracker列表中选择提示词"""
    
    _cached_prompts = []
    
    @classmethod
    def INPUT_TYPES(cls):
        try:
            prompts = get_prompts()
            cls._cached_prompts = prompts
        except:
            prompts = cls._cached_prompts
        
        prompt_choices = ["无 (刷新列表)"]
        for p in prompts:
            pid = p.get("id", "?")
            title = p.get("title", "未命名")
            preview = p.get("prompt_text", "")[:30]
            prompt_choices.append(f"[{pid}] {title} - {preview}...")
        
        if not prompt_choices:
            prompt_choices = ["暂无提示词"]
        
        return {
            "required": {
                "prompt_select": (prompt_choices, {"default": prompt_choices[0]}),
            },
            "optional": {
                "refresh": ("BOOLEAN", {"default": False}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("title", "positive_prompt", "negative_prompt", "model_name", "prompt_id", "status")
    FUNCTION = "select"
    CATEGORY = "Prompt Tracker"
    
    def select(self, prompt_select, refresh=False):
        if refresh:
            try:
                prompts = get_prompts()
                self.__class__._cached_prompts = prompts
            except Exception as e:
                return ("", "", "", "", -1, f"刷新失败: {str(e)}")
        
        if prompt_select.startswith("无") or prompt_select.startswith("暂无"):
            return ("", "", "", "", -1, "请先刷新列表或添加提示词")
        
        try:
            pid_str = prompt_select.split("]")[0].replace("[", "")
            prompt_id = int(pid_str)
        except:
            return ("", "", "", "", -1, "解析提示词ID失败")
        
        try:
            prompt = get_prompt(prompt_id)
            return (
                prompt.get("title", ""),
                prompt.get("prompt_text", ""),
                prompt.get("negative_prompt", "") or "",
                prompt.get("model_name", "") or "",
                prompt_id,
                f"已选择: {prompt.get('title', '')}"
            )
        except Exception as e:
            return ("", "", "", "", -1, f"获取失败: {str(e)}")


class PromptTrackerList:
    """获取Prompt Tracker提示词列表"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "refresh": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "search_keyword": ("STRING", {"default": "", "multiline": False}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("list_text",)
    FUNCTION = "get_list"
    CATEGORY = "Prompt Tracker"
    OUTPUT_NODE = True
    
    def get_list(self, refresh=True, search_keyword=""):
        try:
            prompts = get_prompts()
            
            if search_keyword:
                prompts = [p for p in prompts if search_keyword.lower() in p.get("title", "").lower() 
                          or search_keyword.lower() in p.get("prompt_text", "").lower()]
            
            if not prompts:
                return ("暂无提示词记录",)
            
            lines = ["=" * 50]
            lines.append(f"提示词列表 (共 {len(prompts)} 条)")
            lines.append("=" * 50)
            
            for p in prompts:
                pid = p.get("id", "?")
                title = p.get("title", "未命名")
                preview = p.get("prompt_text", "")[:50]
                model = p.get("model_name", "")
                images = p.get("images", [])
                lines.append(f"[{pid}] {title}")
                lines.append(f"    提示词: {preview}...")
                if model:
                    lines.append(f"    模型: {model}")
                if images:
                    lines.append(f"    图片: {len(images)}张")
                lines.append("-" * 30)
            
            return ("\n".join(lines),)
        
        except Exception as e:
            return (f"获取列表失败: {str(e)}",)
