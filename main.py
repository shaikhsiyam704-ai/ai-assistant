import os
import sys
import json
import time
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import speech_recognition as sr
from gtts import gTTS

# Gemini API Key & URL
API_KEY = "AQ.Ab8RN6Kw2-3_uccb9GNhbZ6R5PwRb9CprONNPiRywVO99d3iQw"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

class BossAssistantUI(BoxLayout):
    def __init__(self, **kwargs):
        super(BossAssistantUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        # বটের স্ট্যাটাস ও হেডার
        self.status_label = Label(
            text="🤖 Boss Assistant\n(কথা বলতে নিচের বাটনে চাপ দিন)",
            font_size='20sp',
            halign='center'
        )
        self.add_widget(self.status_label)

        # মাইক্রোফোন বাটন
        self.listen_btn = Button(
            text="🎙️ Talk to Assistant",
            font_size='18sp',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.listen_btn.bind(on_press=self.start_listening)
        self.add_widget(self.listen_btn)

    def speak(self, text):
        """টেক্সটকে বাংলায় ভয়েসে প্লে করার ফাংশন"""
        try:
            tts = gTTS(text=text, lang='bn')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3 > /dev/null 2>&1")
        except Exception as e:
            print("ভয়েস সমস্যা:", e)

    def ask_gemini(self, prompt):
        """জেমিনি থেকে সরাসরি উত্তর আনার ফাংশন"""
        payload = {
            "contents": [{
                "parts": [{
                    "text": "তুমি একজন বুদ্ধিমান পার্সোনাল অ্যাসিস্ট্যান্ট। তুমি আপনার মালিককে সবসময় 'Boss' (বস) বলে ডাকবে। তুমি সংক্ষিপ্ত, সম্মানজনক ও সুন্দর বাংলায় উত্তর দেবে। Boss বলেছে: " + prompt
                }]
            }]
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception:
            return "Boss, আমার ইন্টারনেট কানেকশনে সমস্যা হচ্ছে!"

    def start_listening(self, instance):
        self.status_label.text = "🎙️ শুনছি, বলুন Boss..."
        Clock.schedule_once(self.process_audio, 0.5)

    def process_audio(self, dt):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                user_input = recognizer.recognize_google(audio, language="bn-BD")
                self.status_label.text = f"👤 Boss: {user_input}"
                
                # Gemini থেকে উত্তর আনা
                reply = self.ask_gemini(user_input)
                self.status_label.text = f"🤖 Assistant:\n{reply}"
                self.speak(reply)
            except Exception:
                self.status_label.text = "⚠️ স্পষ্ট শুনতে পাইনি। আবার চেষ্টা করুন Boss!"

class BossAssistantApp(App):
    def build(self):
        return BossAssistantUI()

if __name__ == "__main__":
    BossAssistantApp().run()