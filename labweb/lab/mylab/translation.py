from googletrans import Translator 

# 翻譯文字的函數
def translate_text(text, target_lang='en'):  
    try:
        translator = Translator() 
        result = translator.translate(text, dest=target_lang)
        
        # 輸出詳細信息，幫助定位問題
        print(f"Source: {text}, Target: {target_lang}, Translated: {result.text}")
        
        return result.text  
    except Exception as e: 
        print(f"Translation failed: {str(e)}")
        raise Exception(f"Translation failed: {str(e)}")

 # 儲存對話的函數
def save_conversation(session, source_text, target_lang, translated_text): 
    conversation = session.get('conversation', [])  # 從 session 中獲取 'conversation' 鍵的值，若無則預設為空列表
    conversation.append({  # 向對話列表中追加一筆新的對話記錄
        'source_text': source_text,  # 儲存原始文字
        'target_lang': target_lang,  # 儲存目標語言
        'translated_text': translated_text  # 儲存翻譯後的文字
    })
    session['conversation'] = conversation  # 更新 session 中的 'conversation' 鍵值
    session.modified = True  # 標記 session 已修改，確保 Django 保存變更

# 定義獲取對話歷史的函數
def get_conversation(session):  
    return session.get('conversation', [])  # 返回 session 中的 'conversation' 鍵值，若無則返回空列表

# 清除對話歷史的函數
def clear_conversation(session):  
    if 'conversation' in session:  # 檢查 'conversation' 鍵是否存在於 session 中
        del session['conversation']  # 如果存在，刪除該鍵值
        session.modified = True  