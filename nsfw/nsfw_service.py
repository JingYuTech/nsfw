#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: 李权威
Email: cnlqws@gmail.com
Date: 2024-10-23
Description: A library for detecting NSFW content in images.
"""

import os
import base64
from io import BytesIO
from typing import Union, Optional

import numpy as np
from PIL import Image
import onnxruntime
import skimage.io
from enum import auto, Enum

from conf import settings_aiplugs


class ImagePreprocessing(Enum):
    AUTO = auto()
    SIMPLE = auto()


class NSFWClassifier:
    DEFAULT_MODEL_PATH = settings_aiplugs.NSFW_WEIGHTS

    _instance = None

    def __new__(cls, model_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(NSFWClassifier, cls).__new__(cls)
            cls._instance.__initialized = False
            cls._instance.model_path = model_path or cls.DEFAULT_MODEL_PATH
        return cls._instance

    def __init__(self, model_path: Optional[str] = None):
        if not hasattr(self, 'initialized') or not self.initialized:
            self.model_path = model_path or self.DEFAULT_MODEL_PATH
            self.load_model()
            self.initialized = True

    def load_model(self):
        self.ort_session = onnxruntime.InferenceSession(self.model_path)
        self.input_name = self.ort_session.get_inputs()[0].name
        self.output_name = self.ort_session.get_outputs()[0].name

    @staticmethod
    def preprocess_image(
            pil_image: Image.Image,
            preprocessing: ImagePreprocessing = ImagePreprocessing.AUTO
    ) -> np.ndarray:
        """
        Preprocessing for the pre-trained Open NSFW model weights.
        """
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        if preprocessing == ImagePreprocessing.AUTO:
            pil_image_resized = pil_image.resize(
                (256, 256), resample=Image.BILINEAR
            )

            fh_im = BytesIO()
            pil_image_resized.save(fh_im, format="JPEG")
            fh_im.seek(0)

            image = skimage.io.imread(fh_im, as_gray=False).astype(np.float32)

            height, width, _ = image.shape
            h, w = (224, 224)

            h_off = max((height - h) // 2, 0)
            w_off = max((width - w) // 2, 0)
            image = image[h_off:h_off + h, w_off:w_off + w, :]

        elif preprocessing == ImagePreprocessing.SIMPLE:
            pil_image_resized = pil_image.resize(
                (224, 224), resample=Image.BILINEAR
            )
            image = np.array(pil_image_resized).astype(np.float32)

        else:
            raise ValueError("Invalid preprocessing option.")

        # RGB to BGR
        image = image[:, :, ::-1]

        # Subtract the training dataset mean value of each channel.
        vgg_mean = [104, 117, 123]
        image = image - np.array(vgg_mean, dtype=np.float32)

        # 添加 batch 维度
        image = np.expand_dims(image, axis=0)

        return image

    def pil_load_image(self, input_image: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        根据输入类型加载图像，并返回一个 Pillow Image 对象。
        """
        base64_prefixes = ['data:image/png;base64,', 'data:image/jpeg;base64,', 'data:image/webp;base64,']
        if isinstance(input_image, str):
            # 去除 data URL 前缀
            if any(input_image.startswith(prefix) for prefix in base64_prefixes):
                input_image = input_image.split(',')[1]

            if os.path.isfile(input_image):
                # 如果是文件路径，则直接打开文件
                image = Image.open(input_image)
            else:
                try:
                    # 尝试解码Base64字符串
                    image_data = base64.b64decode(input_image)
                    image_buffer = BytesIO(image_data)
                    image = Image.open(image_buffer)
                except Exception as e:
                    raise ValueError("Invalid Base64 string.") from e
        elif isinstance(input_image, bytes):
            # 如果是字节，则解码Base64字符串
            image_data = base64.b64decode(input_image)
            image_buffer = BytesIO(image_data)
            image = Image.open(image_buffer)
        elif isinstance(input_image, Image.Image):
            # 如果已经是Image对象，则直接返回
            image = input_image
        else:
            raise TypeError("Unsupported input type. Expected str, bytes, or PIL.Image.Image.")

        return image

    def check_risk_level(
            self,
            risk_values: float | list[float | int],
            threshold: float = 0.8
    ) -> bool | list[bool]:
        # todo
        '''
        :param risk_values:
        :param threshold:
        :return:
        '''
        pass

    def nsfw_risk_ndh(self, input_image: Union[str, bytes, Image.Image]):
        '''
        :param input_image:
        :return:
        '''
        img = self.pil_load_image(input_image)
        input_data = self.preprocess_image(img, preprocessing=ImagePreprocessing.AUTO)
        ort_outputs = self.ort_session.run([self.output_name], {self.input_name: input_data})
        output_probabilities = ort_outputs[0][0]  # 假设只有一个输出，且batch size为1
        sfw_probability = output_probabilities[0]
        nsfw_probability = output_probabilities[1]
        return nsfw_probability

    def nsfw_risk_tf(self, input_image: Union[str, bytes, Image.Image], threshold: float = 0.8) -> bool:
        '''
        nsfw 返回归一化结果
        :param input_image:
        :param threshold: 阈值，建议0.8
        :return: True 违规，False安全
        '''
        pil_image = self.pil_load_image(input_image)
        input_data = self.preprocess_image(pil_image, preprocessing=ImagePreprocessing.AUTO)
        ort_outputs = self.ort_session.run([self.output_name], {self.input_name: input_data})

        output_probabilities = ort_outputs[0][0]  # 假设只有一个输出，且batch size为1
        nsfw_probability = output_probabilities[1]
        return nsfw_probability > threshold


def setup_nsfw(nsfw_weights=None):
    return NSFWClassifier(nsfw_weights)

# Example usage:
# if __name__ == "__main__":
#     # 创建分类器实例
#     classifier = setup_nsfw()  # 使用默认模型路径
#
#     # 或者指定模型路径
#     # classifier = setup_nsfw(os.path.join(settings_aiplugs.MODELS_DIR, 'you_new_.onnx'))
#
#     # 测试图片路径
#     # image_path = '/Users/MsJo/Desktop/sexy/99.jpg'
#
#     image_path = '/Users/MsJo/Desktop/sexy/1.PNG'
#     # image_path = '/Users/MsJo/Desktop/sexy/2.PNG'
#     # image_path = '/Users/MsJo/Desktop/sexy/3.PNG'
#
#     result = classifier.nsfw_risk_ndh(image_path)
#
#     # 使用 归一化 nsfw 方法进行分类
#     result2 = classifier.nsfw_risk_tf(image_path)
#     print(f"result image: {result}")
#     print(f"result image2: {result2}")
#     print("-" * 40)
