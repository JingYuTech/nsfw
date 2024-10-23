#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: 李权威
Email: cnlqws@gmail.com
Date: 2024-10-23
Description: A library for detecting NSFW content in images.
"""


# 引入文件
from  nsfw.nsfw_service import setup_nsfw



# Example usage:
if __name__ == "__main__":

    classifier = setup_nsfw()  # 使用默认模型路径

    # 或者指定模型路径
    # classifier = setup_nsfw(os.path.join(settings_aiplugs.MODELS_DIR, 'you_new_.onnx'))

    # 测试图片路径
    # image_path = '/Users/MsJo/Desktop/sexy/99.jpg'

    image_path = '/Users/MsJo/Desktop/sexy/1.PNG'
    # image_path = '/Users/MsJo/Desktop/sexy/2.PNG'
    # image_path = '/Users/MsJo/Desktop/sexy/3.PNG'

    result = classifier.nsfw_risk_ndh(image_path)

    # 使用 归一化 nsfw 方法进行分类
    result2 = classifier.nsfw_risk_tf(image_path)
    print(f"result image: {result}")
    print(f"result image2: {result2}")
    print("-" * 40)

