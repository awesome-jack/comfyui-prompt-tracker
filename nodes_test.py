"""
ComfyUI Prompt Tracker Node - Simple Test Version
"""

class PromptTrackerTest:
    """测试节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "test", "multiline": False}),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "test"
    CATEGORY = "Prompt Tracker"
    
    def test(self, text):
        return (f"Hello: {text}",)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PromptTrackerTest": PromptTrackerTest,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptTrackerTest": "Prompt Tracker 测试",
}

print("\033[92m[Prompt Tracker] 测试节点加载成功!\033[0m")
