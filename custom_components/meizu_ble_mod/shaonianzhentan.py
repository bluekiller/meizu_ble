import yaml, asyncio, hashlib, os

# MD5加密
def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

# 执行异步方法
def async_create_task(async_func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_func)

# 加载yaml
def load_yaml(file_path):
    # 不存在则返回空字典
    if os.path.exists(file_path) == False:
        return {}
    fs = open(file_path, encoding="UTF-8")
    data = yaml.load(fs, Loader=yaml.FullLoader)
    return data

# 存储为yaml
def save_yaml(file_path, data):
    _dict = {}
    _dict.update(data)
    with open(file_path, 'w') as f:
        yaml.dump(_dict, f)