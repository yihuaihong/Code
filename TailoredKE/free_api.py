import requests

base_url = "https://api.gptgod.online"
api_key = "sk-OsMMq65tXdfOIlTUYtocSL7NCsmA7CerN77OkEv29dODg1EA"

# 要使用的模型名称
model_name = "gpt-3.5-turbo"

# 构建完整的 API 调用 URL
url = f"{base_url}/models/{model_name}/completions"

# 构建请求标头，包括 API 密钥
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 向 API 发送 GET 请求
response = requests.get(url, headers=headers)

# 打印响应
print(response)
