#!/usr/bin/env python3
"""
简化的 Document 类
用于处理解包后的 Word 文档（OOXML 格式）
兼容 update_fc_insider_v3.py 的需求
"""

import os
from pathlib import Path
from xml.dom import minidom


class XMLPart:
    """表示 Word 文档中的一个 XML 部分"""

    def __init__(self, path):
        self.path = path
        with open(path, 'r', encoding='utf-8') as f:
            self.dom = minidom.parseString(f.read())

    def get_node(self, tag=None, contains=None):
        """
        查找节点

        Args:
            tag: 要查找的标签名（如 "w:r", "w:p"）
            contains: 节点必须包含的文本

        Returns:
            找到的第一个匹配节点，或 None
        """
        if tag:
            elements = self.dom.getElementsByTagName(tag)
        else:
            elements = self.dom.getElementsByTagName("*")

        if contains is None:
            return elements[0] if elements else None

        # 查找包含特定文本的节点
        for element in elements:
            node_text = self._get_node_text(element)
            if contains in node_text:
                return element

        return None

    def _get_node_text(self, node):
        """递归获取节点的所有文本内容"""
        texts = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                texts.append(child.nodeValue or '')
            elif child.hasChildNodes():
                texts.append(self._get_node_text(child))
        return ''.join(texts)

    def replace_node(self, old_node, replacement_xml):
        """
        替换节点

        Args:
            old_node: 要替换的节点
            replacement_xml: 替换内容（XML 字符串）
        """
        # 解析替换内容
        temp_doc = minidom.parseString(f"<root>{replacement_xml}</root>")
        parent = old_node.parentNode

        # 导入新节点
        for new_node in temp_doc.documentElement.childNodes:
            if new_node.nodeType == new_node.ELEMENT_NODE:
                imported = self.dom.importNode(new_node, True)
                parent.insertBefore(imported, old_node)

        # 移除旧节点
        parent.removeChild(old_node)

    def save(self):
        """保存 XML 到文件"""
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(self.dom.toxml())


class Document:
    """
    简化的 Document 类
    用于处理解包后的 Word 文档（OOXML）
    """

    def __init__(self, unpacked_dir, author="Claude", rsid="00000000", track_revisions=True):
        """
        初始化 Document

        Args:
            unpacked_dir: 解包后的 Word 文档目录
            author: 作者名称
            rsid: RSID 值
            track_revisions: 是否启用追踪修订
        """
        self.unpacked_dir = Path(unpacked_dir)
        self.author = author
        self.rsid = rsid
        self.track_revisions = track_revisions

        # 加载 XML 部分
        self.parts = {}
        self._load_parts()

    def _load_parts(self):
        """加载所有 XML 部分"""
        # 加载主文档
        doc_path = self.unpacked_dir / 'word' / 'document.xml'
        if doc_path.exists():
            self.parts['word/document.xml'] = XMLPart(str(doc_path))

        # 可以根据需要加载其他部分（styles, settings 等）

    def __getitem__(self, key):
        """允许通过 doc["word/document.xml"] 访问部分"""
        return self.parts.get(key)

    def save(self):
        """保存所有修改过的 XML 部分"""
        for part in self.parts.values():
            part.save()

    @property
    def part_settings(self):
        """
        获取 settings 部分（用于启用追踪修订）
        这是一个模拟实现，返回一个简化的对象
        """
        class SettingsPart:
            def __init__(self, doc):
                self.doc = doc
                self._element = None

            @property
            def _element(self):
                # 简化实现：直接操作 document.xml
                # 实际上 settings 在 word/settings.xml 中
                return self

            def find(self, tag):
                # 简化：总是返回 None，让 enable_track_changes 添加元素
                return None

            def append(self, element):
                # 简化：什么都不做
                pass

        return SettingsPart(self)
