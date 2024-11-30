from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_groq import ChatGroq
import gradio as gr

def setup_chatbot():
    groq_api_key = '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'
    model_name = 'llama-3.1-8b-instant'

    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)

    memory = ConversationBufferMemory(
        memory_key="history",  # 與 Prompt 一致
        return_messages=True
    )

    template = """
    以下是先前的對話記錄：
    {history}

    使用者的最新提問：
    {input}

    請提取出新聞稿中的所有地點和災害，並以「地點：xxx、yyy、zzz，災害：xxx」的格式返回。
    """
    prompt = PromptTemplate(input_variables=["history", "input"], template=template)

    chat_chain = ConversationChain(
        llm=groq_chat,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

    return chat_chain

def main():
    chat_chain = setup_chatbot()

    def chat_function(message, history):
        try:
            response = chat_chain({"input": message, "history": history})  # 傳遞 history
            # 確保非 ASCII 字符處理正常
            result = response["response"].encode('utf-8').decode('utf-8')

            # 定義有效的災害類別
            valid_disasters = [
                "豪雨", "大雨", "暴雨", "淹水", "洪水", "水災",
                "颱風", "風災", "地震", "海嘯", "乾旱", "旱災"
            ]

            # 檢查提取的災害是否在有效類別中
            main_disasters = []  # 修改為列表以收集所有災害
            for disaster in valid_disasters:
                if disaster in result:
                    main_disasters.append(disaster)  # 將符合的災害添加到列表中

            # 提取地點（假設地點在結果中以某種方式表示）
            locations = []
            if "地點：" in result:
                locations = result.split("地點：")[1].split("災害：")[0].strip().split("、")

            # 格式化輸出
            if main_disasters and locations:
                return f"地點: {', '.join(locations)}，災害: {', '.join(main_disasters)}"  # 修改為列出所有災害
            else:
                return "未識別到有效的地點或災害。"

        except Exception as e:
            return f"發生錯誤: {str(e)}"

    with gr.Blocks() as iface:
        gr.Markdown("# ChatBot Assistant\n### 輸入新聞稿，我將提取地點和災害！")
        chatbot = gr.ChatInterface(
            fn=chat_function,
            title="AI 助理",
            description="基於 ChatGroq 的簡易聊天機器人，提取新聞稿中的地點和災害",
            theme="soft",
            examples=[
                "在加州發生了大地震，造成了嚴重損失。",
                "颱風襲擊了日本，導致了洪水。",
                "紐約市的暴風雪影響了交通。"
            ]
        )
    iface.launch(share=True)

if __name__ == "__main__":
    main()