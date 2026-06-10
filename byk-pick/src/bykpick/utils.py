import random
import string

import os


def generate_random_string(
    length: int = 4,
    charset: str | None = None,
) -> str:
    """生成随机字符串。"""
    if charset is None:
        charset = string.ascii_uppercase + string.digits
    return "".join(random.choice(charset) for _ in range(length))


def get_files_metadata(path: str) -> list[dict]:
    """获取文件或目录下的文件元数据列表。"""
    if not path or not os.path.exists(path):
        return []

    if os.path.isfile(path):
        return [{
            'name': os.path.basename(path),
            'path': path,
            'size': os.path.getsize(path)
        }]

    files = []
    try:
        for name in sorted(os.listdir(path)):
            full_path = os.path.join(path, name)
            if os.path.isfile(full_path):
                files.append({
                    'name': name,
                    'path': full_path,
                    'size': os.path.getsize(full_path)
                })
    except (FileNotFoundError, PermissionError):
        return []
    return files
