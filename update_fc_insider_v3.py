#!/usr/bin/env python3
"""
FC Insider 翻譯更新腳本 V3（修正版 + 追蹤修訂強化版）
- 啟用文件層級追蹤修訂
- 低階 XML 控制 <w:del>/<w:ins>
- 空白儲存格也可正確插入翻譯
"""

import sys
import json
import argparse
import html
from pathlib import Path
from xml.dom import minidom
from datetime import datetime
from docx.oxml import OxmlElement

# 加載 docx skill（保留你原本的 Document 類別）
sys.path.insert(0, '/mnt/skills/public/docx')
from scripts.document import Document

# 加載標籤保護工具（保留原有實作）
from tag_protector import protect_tags, restore_tags


def get_direct_children_by_tagname(node, tagname):
    children = []
    for ch in node.childNodes:
        if getattr(ch, "nodeName", None) == tagname:
            children.append(ch)
    return children


def get_normalized_formats_and_text(para_node):
    ppr_nodes = get_direct_children_by_tagname(para_node, "w:pPr")
    ppr_xml = ppr_nodes[0].toxml() if ppr_nodes else ""

    rpr_xml = ""
    runs = get_direct_children_by_tagname(para_node, "w:r")
    for run in runs:
        rpr_tags = get_direct_children_by_tagname(run, "w:rPr")
        if rpr_tags:
            r_style = get_direct_children_by_tagname(rpr_tags[0], "w:rStyle")
            if r_style and r_style[0].getAttribute("w:val") == "Tag":
                continue
            rpr_xml = rpr_tags[0].toxml()
            break

    text_parts = []
    for run in get_direct_children_by_tagname(para_node, "w:r"):
        rpr_in_run = get_direct_children_by_tagname(run, "w:rPr")
        if rpr_in_run:
            r_style = get_direct_children_by_tagname(rpr_in_run[0], "w:rStyle")
            if r_style and r_style[0].getAttribute("w:val") == "Tag":
                continue
        for t in get_direct_children_by_tagname(run, "w:t"):
            if t.firstChild and t.firstChild.nodeValue is not None:
                text_parts.append(t.firstChild.nodeValue)

    raw_text = ''.join(text_parts)
    unescaped_text = html.unescape(raw_text)
    aggregated_text = protect_tags(unescaped_text)

    # 移除段落的直接 child <w:r>
    runs_to_remove = list(get_direct_children_by_tagname(para_node, "w:r"))
    for run in runs_to_remove:
        try:
            para_node.removeChild(run)
        except Exception:
            pass

    return ppr_xml, rpr_xml, aggregated_text


def locate_row_by_segment_id(all_rows, segment_id):
    for row in all_rows:
        cells = get_direct_children_by_tagname(row, "w:tc")
        if not cells:
            continue
        first_cell = cells[0]
        paras = get_direct_children_by_tagname(first_cell, "w:p")
        for para in paras:
            parts = []
            for r in get_direct_children_by_tagname(para, "w:r"):
                for t in get_direct_children_by_tagname(r, "w:t"):
                    if t.firstChild and t.firstChild.nodeValue is not None:
                        parts.append(t.firstChild.nodeValue)
            text = "".join(parts).strip()
            if text == str(segment_id).strip():
                return row
    return None


def find_target_cell_in_row(row_node):
    cells = get_direct_children_by_tagname(row_node, "w:tc")
    if len(cells) >= 4:
        return cells[3]
    return None


def find_target_paragraph_in_cell(cell_node):
    paras = get_direct_children_by_tagname(cell_node, "w:p")
    for para in paras:
        runs = get_direct_children_by_tagname(para, "w:r")
        has_non_tag_run = False
        for run in runs:
            rpr_nodes = get_direct_children_by_tagname(run, "w:rPr")
            is_tag = False
            if rpr_nodes:
                r_style_nodes = get_direct_children_by_tagname(rpr_nodes[0], "w:rStyle")
                if r_style_nodes:
                    val = r_style_nodes[0].getAttribute("w:val")
                    if val == "Tag":
                        is_tag = True
            if not is_tag:
                t_nodes = get_direct_children_by_tagname(run, "w:t")
                found_text = False
                for t in t_nodes:
                    if t.firstChild and t.firstChild.nodeValue and t.firstChild.nodeValue.strip() != "":
                        found_text = True
                        break
                if found_text:
                    has_non_tag_run = True
                    break
        if has_non_tag_run:
            return para
    if paras:
        return paras[0]
    return None


def replace_paragraph_with_xml(dom, old_para, replacement_xml):
    try:
        new_doc = minidom.parseString(replacement_xml)
        new_node = new_doc.documentElement
        imported = dom.importNode(new_node, True)
        parent = old_para.parentNode
        parent.replaceChild(imported, old_para)
        return True
    except Exception as e:
        raise RuntimeError(f"DOM replace failed: {e}")


# ------------------------------
# 新增功能：啟用文件層級追蹤修訂
# ------------------------------
def enable_track_changes(doc):
    settings_part = doc.part_settings
    settings = settings_part._element
    if not settings.find('w:trackRevisions'):
        track_revisions = OxmlElement('w:trackRevisions')
        settings.append(track_revisions)
        print("✓ 文件層級追蹤修訂已啟用")
    else:
        print("✓ 文件層級追蹤修訂已存在")


# ------------------------------
# 新增功能：低階插入 <w:del>/<w:ins>
# ------------------------------
def create_delete_element(text, author, rid, rpr_xml=""):
    del_elem = OxmlElement("w:del")
    del_elem.set("w:id", str(rid))
    del_elem.set("w:author", author)
    del_elem.set("w:date", datetime.now().isoformat())

    r = OxmlElement("w:r")
    if rpr_xml:
        r_pr_node = minidom.parseString(rpr_xml).documentElement
        r.append(r_pr_node)
    del_text = OxmlElement("w:delText")
    del_text.set("xml:space", "preserve")
    del_text.text = text
    r.append(del_text)
    del_elem.append(r)
    return del_elem


def create_insert_element(text, author, rid, rpr_xml=""):
    ins_elem = OxmlElement("w:ins")
    ins_elem.set("w:id", str(rid))
    ins_elem.set("w:author", author)
    ins_elem.set("w:date", datetime.now().isoformat())

    r = OxmlElement("w:r")
    if rpr_xml:
        r_pr_node = minidom.parseString(rpr_xml).documentElement
        r.append(r_pr_node)
    t_elem = OxmlElement("w:t")
    t_elem.set("xml:space", "preserve")
    t_elem.text = text
    r.append(t_elem)
    ins_elem.append(r)
    return ins_elem


def insert_translation_with_track_changes(p_element, original_text, new_text, author, revision_id, rpr_xml=""):
    if original_text.strip():
        del_element = create_delete_element(original_text, author, revision_id, rpr_xml)
        p_element.append(del_element)
        revision_id += 1
    if new_text.strip():
        ins_element = create_insert_element(new_text, author, revision_id, rpr_xml)
        p_element.append(ins_element)
        revision_id += 1
    return revision_id


def update_translations(doc, translations):
    successful = 0
    failed = []
    dom = doc["word/document.xml"].dom
    all_rows = dom.getElementsByTagName("w:tr")

    print(f"開始處理 {len(translations)} 個翻譯...")
    print("=" * 80)

    for i, trans in enumerate(translations, 1):
        segment_id = trans.get('segment_id', 'Unknown')
        old_text = trans.get('old_text', '')
        new_text = trans.get('new_text', '')

        print(f"[{i}/{len(translations)}] 處理 {segment_id[:40]}...", end=' ')

        try:
            target_row = locate_row_by_segment_id(all_rows, segment_id)
            if not target_row:
                raise ValueError("找不到 segment（嚴格比對）")
            target_cell = find_target_cell_in_row(target_row)
            if not target_cell:
                raise ValueError("無法定位第 4 欄")
            old_para = find_target_paragraph_in_cell(target_cell)
            if not old_para:
                raise ValueError("找不到目標段落（cell 內無段落）")

            ppr_xml, rpr_xml, aggregated_text = get_normalized_formats_and_text(old_para)

            old_protected = protect_tags(old_text)
            new_protected = protect_tags(new_text)

            allow_empty_old = (old_text is None) or (str(old_text).strip() == "")
            if not allow_empty_old:
                if old_protected not in aggregated_text:
                    raise ValueError(
                        f"文本不匹配 - 預期: '{old_text[:30]}...', "
                        f"實際: '{html.unescape(aggregated_text)[:30]}...'"
                    )

            revision_id = i * 2
            revision_id = insert_translation_with_track_changes(
                old_para, old_protected, new_protected, doc.author, revision_id, rpr_xml
            )

            successful += 1
            print("✓")
        except Exception as e:
            error_msg = str(e)
            failed.append((segment_id, error_msg))
            print(f"✗ ({error_msg[:60]})")

    return successful, failed


def batch_update(unpacked_dir, translations_file, rsid, author='Claude'):
    with open(translations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        translations = data.get('translations', data)

    doc = Document(
        unpacked_dir,
        author=author,
        rsid=rsid,
        track_revisions=True
    )

    # 啟用文件層級追蹤修訂
    enable_track_changes(doc)

    print(f"FC Insider 翻譯更新 V3（修正版）")
    print(f"作者: {author}")
    print(f"RSID: {rsid}")
    print(f"追蹤修訂: 已啟用")
    print(f"翻譯數量: {len(translations)}")
    print("=" * 80)

    successful, failed = update_translations(doc, translations)

    print("=" * 80)
    print(f"✓ 更新完成: {successful}/{len(translations)}")

    if failed:
        print(f"✗ 失敗: {len(failed)} 個")
        print("\n失敗詳情（前 10 個）:")
        for seg_id, error in failed[:10]:
            print(f"  • {seg_id[:40]}: {error[:200]}")

    print("=" * 80)

    print("\n恢復標籤保護...")
    doc_path = Path(unpacked_dir) / 'word' / 'document.xml'
    with open(doc_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    xml_content = restore_tags(xml_content)
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print("✓ 標籤恢復完成")

    print("\n保存變更...")
    try:
        doc.save()
        print("✓ 變更已保存")
    except Exception as e:
        print(f"✗ 保存失敗: {e}")
        raise

    return successful, failed


def main():
    parser = argparse.ArgumentParser(
        description='FC Insider 翻譯更新 V3（修正版 - DOM safe）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python update_fc_insider_v3.py \\
    --unpacked ./unpacked_doc \\
    --translations translations.json \\
    --rsid 00AB12CD \\
    --author "Claire"
        '''
    )

    parser.add_argument('--unpacked', required=True, help='解包後的 DOCX 目錄')
    parser.add_argument('--translations', required=True, help='翻譯 JSON 文件路徑')
    parser.add_argument('--rsid', required=True, help='RSID 值（從 unpack 腳本獲取，例如：00AB12CD）')
    parser.add_argument('--author', default='Claude', help='作者名稱（預設: Claude）')

    args = parser.parse_args()

    try:
        successful, failed = batch_update(
            args.unpacked,
            args.translations,
            args.rsid,
            args.author
        )

        if successful == 0:
            exit(2)
        elif failed:
            exit(1)
        else:
            exit(0)

    except Exception as e:
        print(f"\n致命錯誤: {e}")
        import traceback
        traceback.print_exc()
        exit(2)


if __name__ == '__main__':
    main()
