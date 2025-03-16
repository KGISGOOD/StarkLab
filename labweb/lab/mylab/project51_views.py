from django.shortcuts import render
import speech_recognition as sr
import pyttsx3
from django.http import JsonResponse

def translate(request):
    return render(request, 'translate.html')

engine = pyttsx3.init()

def speak(text): #電腦說
    engine.say(text)
    engine.runAndWait()

def listen(request): #電腦聽
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("請說出您的問題...")
        recognizer.adjust_for_ambient_noise(source) #根據背景噪音自動調整麥克風的靈敏度，避免噪音干擾
        audio = recognizer.listen(source) #錄製使用者的語音

    try:
        print("識別中...")
        content = recognizer.recognize_google(audio, language='zh-TW')
        #使用 Google Speech Recognition API 將語音轉換為文字
        print(f"您說: {content}")
        return render(request, 'translate.html', {'speech_result': content})
    
    except sr.UnknownValueError:
        speak("抱歉，我無法聽懂您的語音。")
        return None
    
    except sr.RequestError:
        speak("語音服務無法使用，請稍後再試。")
        return None
    
    

