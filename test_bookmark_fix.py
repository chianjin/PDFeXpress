#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify the bookmark page number extraction and hierarchy fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from toolkit.core.edit_bookmark_worker import get_outlines, set_outlines


def test_bookmark_extraction(pdf_path):
    """
    Test function to extract bookmarks from a PDF and print results
    """
    print(f"Testing bookmark extraction for: {pdf_path}")
    
    try:
        bookmarks = get_outlines(pdf_path)
        print(f"Found {len(bookmarks)} bookmarks:")
        
        for i, bookmark in enumerate(bookmarks):
            level, title, page_num = bookmark
            print(f"  {i+1}. Level: {level}, Title: '{title}', Page: {page_num}")
            
        return bookmarks
    except Exception as e:
        print(f"Error extracting bookmarks: {e}")
        return []


def test_bookmark_save(tmp_pdf_path, original_bookmarks):
    """
    Test function to save bookmarks to a new PDF and verify structure
    """
    print(f"Testing bookmark saving to: {tmp_pdf_path}")
    
    try:
        # 使用原始书签创建新的PDF
        set_outlines(original_pdf_path, original_bookmarks, tmp_pdf_path)
        print(f"Bookmarks saved successfully to: {tmp_pdf_path}")
        
        # 读取新保存的PDF的书签
        saved_bookmarks = get_outlines(tmp_pdf_path)
        print(f"Bookmarks in saved PDF ({len(saved_bookmarks)}):")
        
        for i, bookmark in enumerate(saved_bookmarks):
            level, title, page_num = bookmark
            print(f"  {i+1}. Level: {level}, Title: '{title}', Page: {page_num}")
            
        # 比较原始和保存后的结构
        print("\nComparing structures:")
        for i, (orig, saved) in enumerate(zip(original_bookmarks, saved_bookmarks)):
            orig_level, orig_title, orig_page = orig
            saved_level, saved_title, saved_page = saved
            match = "✓" if orig == saved else "✗"
            print(f"  {i+1}. {match} Original: Level {orig_level}, '{orig_title}', Page {orig_page} | Saved: Level {saved_level}, '{saved_title}', Page {saved_page}")
        
        return saved_bookmarks
    except Exception as e:
        print(f"Error saving or verifying bookmarks: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_bookmark_fix.py <pdf_file_path> [output_pdf_path]")
        print("Please provide a PDF file path as an argument")
        print("Optional: provide an output PDF path to test saving bookmarks")
        sys.exit(1)
    
    original_pdf_path = sys.argv[1]
    
    if not os.path.exists(original_pdf_path):
        print(f"Error: PDF file does not exist: {original_pdf_path}")
        sys.exit(1)
    
    # 测试提取功能
    original_bookmarks = test_bookmark_extraction(original_pdf_path)
    
    # 如果提供了输出路径，测试保存功能
    if len(sys.argv) >= 3:
        output_pdf_path = sys.argv[2]
        test_bookmark_save(output_pdf_path, original_bookmarks)