import json
import os

# Load the main results file to see what content was passed to LLM
main_file = 'results/fpga_documents.json'
if os.path.exists(main_file):
    with open(main_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('=== LLMに送られているコンテンツの分析 ===')
    
    for source_name, source_data in data['sources'].items():
        if source_name in ['xilinx', 'altera']:
            print(f'\n📁 Source: {source_name.upper()}')
            doc_count = source_data['document_count']
            print(f'Documents: {doc_count}')
            
            for doc in source_data['documents']:
                title = doc['name'][:50]
                print(f'\n📄 Document: {title}...')
                print(f'URL: {doc["url"]}')
                print(f'Abstract: {doc.get("abstract", "None")}')
                content_len = len(str(doc.get('content', ''))) if doc.get('content') else 0
                print(f'Content length: {content_len} chars')
                
                # Check if there's any content field
                if 'content' in doc:
                    content = doc['content']
                    if len(content) > 200:
                        preview = content[:200]
                        print(f'Content preview: {preview}...')
                    else:
                        print(f'Content: {content}')
                else:
                    print('❌ No content field found - LLM would only see title/URL')
