import os
import json
import jieba
from collections import Counter, defaultdict
# 加载文件
def load_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            chunks = [p.strip() for p in content.split('\n\n') if p.strip()]
            return chunks  
    else:
        return None
# 加载目录下的所有文件
def load_file_from_dir(dirpath):
    allchunks = []
    for filename in sorted(os.listdir(dirpath)):
        if filename.endswith(('.txt', '.md')):
            file_path = os.path.join(dirpath, filename)
            chunks = load_file(file_path)
            if chunks:
                allchunks.extend(chunks)
    return allchunks
# 添加笔记
def add_note(chunks, index, path):
    new_chunks = []
    if os.path.isfile(path):
        file_chunks = load_file(path)
        if file_chunks:
            new_chunks = file_chunks
    elif os.path.isdir(path):
        new_chunks = load_file_from_dir(path)
    else:
        return chunks, index, 0
    if not new_chunks:
        return chunks, index, 0
    count = len(new_chunks)
    chunks.extend(new_chunks)
    index = build_index(chunks)
    return chunks, index, count

STOP_WORDS = {'的','了','在','是','我','你','他','它','她','们','这','那',
               '和','就','不'}

# 构建索引
def build_index(chunks):
    index = defaultdict(set)
    for i, chunk in enumerate(chunks):
        words = jieba.lcut(chunk)
        for word in words:
            if len(word) >= 2 and word not in STOP_WORDS:
                index[word].add(i)
    return {k: list(v) for k, v in index.items()}
# 计算问题与文档的相关性分数
def relevance_score(query, doc):
    q_words = jieba.lcut(query)
    d_words = jieba.lcut(doc)
    q_counter = Counter(q_words)
    d_counter = Counter(d_words)
    score = 0
    for word in set(q_words) & set(d_words):
        score += q_counter[word] * d_counter[word]
    return score
# 搜索
def search(query, chunks, index, top_k=3):
    q_words = [w for w in jieba.lcut(query) if len(w) >= 2 and w not in STOP_WORDS]
    candidates = set()
    for word in q_words:
        if word in index:
            candidates.update(index[word])
    if not candidates:
        return []
    ranked = []
    for idx in candidates:
        rel = relevance_score(query, chunks[idx])
        norm_score = rel / (len(chunks[idx]) )
        ranked.append((idx, norm_score, chunks[idx]))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
# 删除段落
def delete_chunk(chunks, index, idx):
    if idx < 0 or idx >= len(chunks):
        return chunks, index, False
    del chunks[idx]
    for word in list(index.keys()):
        new_ids = []
        for i in index[word]:
            if i == idx:
                continue          
            if i > idx:
                new_ids.append(i - 1)  
            else:
                new_ids.append(i)     
        if new_ids:
            index[word] = new_ids
        else:
            del index[word]
    return chunks, index, True
# 列出所有段落
def list_chunks(chunks):
    return chunks
#工具处理函数
def handle_help(chunks, index,arg):
    print("\n可用命令：")
    for name, info in TOOLS.items():
        print(f"  {info['usage']:<20}{name}")
    print("  ? 或 help          显示此帮助")
    print("  q                  退出程序")
    return chunks, index

def handle_list(chunks, index,arg):
    if not chunks:
        print("暂无笔记，请先用 add 导入")
    else:
        for i, chunk in enumerate(chunks):
            preview = chunk[:60].replace('\n', ' ')
            print(f"[{i}] {preview}{'...' if len(chunk) > 60 else ''}")
    return chunks, index

def handle_add(chunks, index, path):
    chunks, index, count = add_note(chunks, index, path)
    if count == 0:
        print("未找到笔记文件，请检查路径")
    else:
        print(f"已添加 {count} 个段落，共 {len(chunks)} 个段落")
    return chunks, index

def generate_answer(query, top_docs):
    answer = f"问题：{query}\n\n"
    answer += "根据检索到的资料：\n"
    for i, (_, score, text) in enumerate(top_docs):
        preview = text[:100].replace('\n', ' ')
        answer += f"  [来源{i+1}] (相关度:{score:.2f}) {preview}...\n"
    answer += "\n回答：根据上述资料，"
    if top_docs:
        keywords = [w for w in jieba.lcut(query) if len(w) >= 2 and w not in STOP_WORDS]
        snippets = []
        for _, _s, text in top_docs:
            for sentence in text.replace('\n', ' ').split('。'):
                if any(kw in sentence for kw in keywords):
                    snippets.append(sentence.strip())
                    break
        if snippets:
            answer += "；".join(snippets[:3]) + "。"
        else:
            answer += "相关内容已在上述来源中列出。"
    answer += "\n（注：本回答基于本地笔记检索生成，引用来源见上方标注。）"
    return answer

def handle_ask(chunks, index, query):
    if not index:
        print("请先导入笔记，例：add ./notes")
        return chunks, index
    results = search(query, chunks, index)
    if not results:
        print("未找到相关内容")
        return chunks, index
    print(generate_answer(query, results))
    return chunks, index

def handle_delete(chunks, index, idx_str):
    try:
        idx = int(idx_str)
    except (ValueError, TypeError):
        print("请提供有效的段落编号，例：delete 0")
        return chunks, index
    chunks, index, ok = delete_chunk(chunks, index, idx)
    if ok:
        print(f"已删除段落 [{idx}]，剩余 {len(chunks)} 个段落")
    else:
        print(f"无效的段落编号：{idx}")
    return chunks, index
# 工具注册表
TOOLS = {
    "add": {
        "handler":  handle_add,
        "keywords": ["添加", "导入", "加载", "add", "import"],
        "usage":    "add <路径>",
    },
    "list": {
        "handler":  handle_list,
        "keywords": ["列出", "显示", "查看", "所有", "list", "show"],
        "usage":    "list",
    },
    "ask": {
        "handler":  handle_ask,
        "keywords": ["问", "查", "什么", "怎么", "如何", "为什么", "ask", "search"],
        "usage":    "ask <问题>",
    },
    "delete": {
        "handler":  handle_delete,
        "keywords": ["删除", "移除", "去掉", "delete", "remove"],
        "usage":    "delete <编号>",
    },
}
#命令解析
def ToolDecide(user_input):
    text = user_input.strip()
    if not text:
        return None, ""
    if text in ('q', 'quit', 'exit', '退出'):
        return 'quit', ''
    if text in ('?', 'help', '帮助'):
        return 'help', ''
    parts = text.split(' ', 1)
    prefix = parts[0]
    rest = parts[1] if len(parts) > 1 else ''
    if prefix in TOOLS:
        need_arg = '<' in TOOLS[prefix]['usage']  # usage 里有 <> 就需要参数
        if not rest:
            if need_arg:
                return None, f"用法：{TOOLS[prefix]['usage']}"
            return prefix, rest
        return prefix, rest
    for name, info in TOOLS.items():
        for kw in info["keywords"]:
            if kw in text:
                arg = text
                for kw2 in info["keywords"]:
                    arg = arg.replace(kw2, '')
                arg = arg.strip()
                if not arg:
                    return None, f"用法：{info['usage']}"
                return name, arg

    return None, f'无法识别"{text}"，输入 ? 查看帮助'

def main():
    chunks = []
    index = {}
    print("个人知识助手")
    print("标准用法:")
    print("?帮助|add<路径>|list|ask<问题>|delete<编号>|q退出")
    print("也可输入自然语言问题")
    while True:
        try:
            cmd = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n程序退出")
            break

        tool_name, arg = ToolDecide(cmd)
        if tool_name is None:
            if arg:
                print(arg)
            print("=" * 50)
            continue
        if tool_name == 'quit':
            print("程序退出")
            break
        if tool_name == 'help':
            chunks, index = handle_help(chunks, index, arg)
            print("=" * 50)
            continue
        handler = TOOLS[tool_name]["handler"]
        print(f"[{tool_name}]")
        chunks, index = handler(chunks, index, arg)
        print("=" * 50)

if __name__ == '__main__':
    main()
