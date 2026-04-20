#!/usr/bin/env python3
"""
从 tophub.today 抓取热榜数据，更新到 index.html 的 FALLBACK_DATA 中
"""
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

CORS_PROXY = 'https://api.allorigins.win/raw?url='
TOPHUB_URL = 'https://tophub.today/c/news'

print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M")}] 开始抓取 tophub.today...')

try:
    resp = requests.get(CORS_PROXY + TOPHUB_URL, timeout=30)
    html = resp.text
    print(f'  获取到 HTML: {len(html)} bytes')
except Exception as e:
    print(f'  获取失败: {e}')
    exit(0)

soup = BeautifulSoup(html, 'html.parser')
items = []
seen = set()

# 遍历所有外链
for link in soup.find_all('a', href=True):
    href = link['href']
    text = link.get_text(strip=True)

    # 过滤：排除站内链接、太短的标题、导航菜单
    if 'tophub.today' in href or 'javascript' in href or href == '#':
        continue
    if len(text) < 10:
        continue
    skip_words = ['登录', '注册', '首页', '晚报', '动态', '追踪', '榜中榜',
                   '热文库', '话题', '日历', '更多', '热搜']
    if any(text.startswith(w) for w in skip_words):
        continue

    # 去重
    if text in seen:
        continue
    seen.add(text)

    # 获取热度值
    hot_val = ''
    parent = link.find_parent('.w1')
    if parent:
        span = parent.find('span')
        if span:
            hot_val = span.get_text(strip=True).replace('热度', '').strip()

    # 获取来源
    source = ''
    node = link.find_parent('.node-i') or link.find_parent('.nodeblock')
    if node:
        t = node.find('.t')
        if t:
            source = t.get_text(strip=True)
        else:
            for a in node.find_all('a', href=True):
                if 'tophub' not in a['href'] and 'javascript' not in a['href'] and a != link:
                    source = a.get_text(strip=True)[:20]
                    break

    items.append({
        'title': text[:100],
        'source': source or '热榜',
        'hot': hot_val,
        'url': href
    })

print(f'  抓取到 {len(items)} 条数据')

# 取前 20 条
top_items = items[:20]
for i, item in enumerate(top_items):
    print(f'  {i+1}. [{item["source"]}] {item["title"][:35]}... {item["hot"]}')

# 生成 JS 数据
def js_str(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

lines = ['var FALLBACK_DATA = {', '  all: [']
for item in top_items:
    lines.append(
        f'    {{title: "{js_str(item["title"])}", '
        f'source: "{js_str(item["source"])}", '
        f'hot: "{js_str(item["hot"])}", '
        f'url: "{js_str(item["url"])}"}},'
    )
lines.append('  ]')
lines.append('};')
fallback_js = '\n'.join(lines)

# 读取 index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 FALLBACK_DATA 区域并替换
marker_start = '// ============================================================\n// 兜底数据'
start_idx = content.find(marker_start)
end_marker = 'var FALLBACK_DATA = {'
end_idx = content.find(end_marker)

# 找到 FALLBACK_DATA 的结束位置（最后一个 };）
last_brace = content.rfind('};')
if last_brace != -1:
    last_brace += 2  # include };

if start_idx != -1 and end_idx != -1 and last_brace > end_idx:
    new_content = (
        content[:start_idx]
        + marker_start
        + f'（自动更新于 {datetime.now().strftime("%Y-%m-%d %H:%M")}）\n'
        + fallback_js
        + '\n'
        + content[last_brace:]
    )
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'\n✅ index.html 更新成功！')
else:
    print(f'\n⚠️ 未找到 FALLBACK_DATA 区域，跳过更新')
    print(f'  start_idx={start_idx}, end_idx={end_idx}, last_brace={last_brace}')
