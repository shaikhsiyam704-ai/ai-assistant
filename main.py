import os
import sys
import json
import datetime
import urllib.request
import subprocess

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

import speech_recognition as sr
from gtts import gTTS

# উইন্ডো ব্যাকগ্রাউন্ড থিম সেটআপ
Window.clearcolor = (0.05, 0.06, 0.09, 1)

# জেমিনি এপিআই কনফিগারেশন
API_KEY = "AQ.Ab8RN6Kw2-3_uccb9GNhbZ6R5PwRb9CprONNPiRywVO99d3iQw"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

class UltimateSiriAssistantUI(BoxLayout):
    def __init__(self, **kwargs):
        super(UltimateSiriAssistantUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        self.chat_history = []

        # ১. প্রিমিয়াম হেডার বার
        self.header = Label(
            text="🌟 ULTIMATE BOSS SIRI ASSISTANT 🌟",
            font_size='20sp',
            bold=True,
            color=(0.1, 0.8, 1, 1),
            size_hint_y=0.07
        )
        self.add_widget(self.header)

        # ২. চ্যাট ডিসপ্লে স্ক্রিন
        self.scroll_view = ScrollView(size_hint=(1, 0.58))
        self.chat_layout = GridLayout(cols=1, spacing=12, size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll_view.add_widget(self.chat_layout)
        self.add_widget(self.scroll_view)

        # প্রাথমিক শুভেচ্ছা বার্তা
        self.add_chat_bubble("Assistant", "স্বাগতম Boss! আপনার পার্সোনাল সিরি-স্টাইল এআই অ্যাসিস্ট্যান্ট সম্পূর্ণ প্রস্তুত রয়েছে। বলুন কি সেবা করতে পারি?")

        # ৩. কুইক টুলস ও সিস্টেম শর্টকাট বার - ১
        self.quick_bar_1 = BoxLayout(orientation='horizontal', spacing=6, size_hint_y=0.07)
        
        btn_battery = Button(text="🔋 ব্যাটারি", background_color=(0.1, 0.6, 0.3, 1))
        btn_battery.bind(on_press=lambda x: self.process_command("ব্যাটারি কত"))
        
        btn_time = Button(text="🕒 সময় ও তারিখ", background_color=(0.2, 0.4, 0.8, 1))
        btn_time.bind(on_press=lambda x: self.process_command("সময় কত"))

        btn_torch_on = Button(text="💡 টর্চ অন", background_color=(0.8, 0.5, 0.1, 1))
        btn_torch_on.bind(on_press=lambda x: self.process_command("টর্চ অন"))

        btn_torch_off = Button(text="🔌 টর্চ অফ", background_color=(0.7, 0.2, 0.2, 1))
        btn_torch_off.bind(on_press=lambda x: self.process_command("টর্চ অফ"))

        self.quick_bar_1.add_widget(btn_battery)
        self.quick_bar_1.add_widget(btn_time)
        self.quick_bar_1.add_widget(btn_torch_on)
        self.quick_bar_1.add_widget(btn_torch_off)
        self.add_widget(self.quick_bar_1)

        # ৪. কুইক টুলস ও সিস্টেম শর্টকাট বার - ২
        self.quick_bar_2 = BoxLayout(orientation='horizontal', spacing=6, size_hint_y=0.07)
        
        btn_bright_high = Button(text="☀️ ফুল ব্রাইটনেস", background_color=(0.9, 0.7, 0.1, 1))
        btn_bright_high.bind(on_press=lambda x: self.process_command("ব্রাইটনেস বাড়াও"))
        
        btn_bright_low = Button(text="🌙 লো ব্রাইটনেস", background_color=(0.3, 0.3, 0.5, 1))
        btn_bright_low.bind(on_press=lambda x: self.process_command("ব্রাইটনেস কমাও"))

        btn_clear = Button(text="🗑️ চ্যাট মুছুন", background_color=(0.6, 0.1, 0.1, 1))
        btn_clear.bind(on_press=self.clear_chat_screen)

        self.quick_bar_2.add_widget(btn_bright_high)
        self.quick_bar_2.add_widget(btn_bright_low)
        self.quick_bar_2.add_widget(btn_clear)
        self.add_widget(self.quick_bar_2)

        # ৫. টেক্সট ইনপুট ও সেন্ড বক্স
        self.input_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=0.08)
        self.txt_input = TextInput(
            hint_text="এখানে কিছু লিখে কমান্ড দিন, Boss...",
            multiline=False,
            font_size='15sp'
        )
        self.send_btn = Button(
            text="সেন্ড",
            size_hint_x=0.25,
            background_color=(0, 0.6, 0.8, 1)
        )
        self.send_btn.bind(on_press=self.on_send_text)
        self.input_box.add_widget(self.txt_input)
        self.input_box.add_widget(self.send_btn)
        self.add_widget(self.input_box)

        # ৬. মূল ভয়েস কমান্ড বাটন
        self.voice_btn = Button(
            text="🎙️ ভয়েস কমান্ড দিন (Tap to Speak)",
            font_size='18sp',
            bold=True,
            size_hint_y=0.13,
            background_color=(0.8, 0.1, 0.6, 1)
        )
        self.voice_btn.bind(on_press=self.start_listening)
        self.add_widget(self.voice_btn)

    def add_chat_bubble(self, sender, text):
        """চ্যাট বাব্বল স্টাইলে মেসেজ যোগ করা"""
        tag = "[color=00ffff]👤 Boss:[/color]" if sender == "Boss" else "[color=ff3366]🤖 Siri AI:[/color]"
        msg = Label(
            text=f"{tag} {text}",
            markup=True,
            font_size='16sp',
            size_hint_y=None,
            text_size=(Window.width - 40, None),
            halign='left'
        )
        msg.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.chat_layout.add_widget(msg)
        self.scroll_view.scroll_y = 0
        self.chat_history.append(f"{sender}: {text}")

    def speak(self, text):
        """টেক্সটকে সুন্দর বাংলায় ভয়েসে রূপান্তর"""
        try:
            tts = gTTS(text=text, lang='bn')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3 > /dev/null 2>&1")
        except Exception as e:
            print("Voice generation error:", e)

    def ask_gemini(self, prompt):
        """জেমিনি এপিআই দিয়ে ইন্টেলিজেন্ট উত্তর জেনারেট করা"""
        payload = {
            "contents": [{
                "parts": [{
                    "text": "তুমি আইফোনের সিরির মতো অত্যন্ত স্মার্ট এবং আধুনিক একজন এআই অ্যাসিস্ট্যান্ট। তোমার মালিকের নাম 'Boss'। তুমি সবসময় তাকে সম্মান জানিয়ে খুব মিষ্টি ও সংক্ষিপ্ত বাংলায় উত্তর দেবে। Boss বলেছে: " + prompt
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
        except Exception as e:
            print("API Connection Error:", e)
            return "Boss, ইন্টারনেটে একটু সমস্যা হচ্ছে, দয়া করে আবার চেষ্টা করুন!"

    def process_command(self, user_input):
        """কমপ্লিট ডিভাইস এবং এআই কমান্ড হ্যান্ডলার"""
        self.add_chat_bubble("Boss", user_input)
        cmd = user_input.lower()
        reply = ""

        # ১. সময় ও তারিখ ম্যানেজমেন্ট
        if "সময়" in cmd or "কয়টা বাজে" in cmd or "টাইম" in cmd:
            now = datetime.datetime.now()
            reply = f"Boss, বর্তমান সময় হচ্ছে {now.strftime('%I:%M %p')}।"
        elif "তারিখ" in cmd or "আজকে কি বার" in cmd:
            now = datetime.datetime.now()
            reply = f"Boss, আজকে {now.strftime('%A, %d %B %Y')}।"

        # ২. ব্যাটারি স্ট্যাটাস চেক
        elif "ব্যাটারি" in cmd or "চার্জ" in cmd:
            try:
                res = subprocess.check_output(["termux-battery-status"]).decode("utf-8")
                info = json.loads(res)
                pct = info.get("percentage", "অজানা")
                status = info.get("status", "")
                reply = f"Boss, আপনার ফোনে এখন {pct}% চার্জ রয়েছে।"
            except Exception:
                reply = "Boss, ডিভাইস থেকে ব্যাটারির তথ্য সংগ্রহ করা যাচ্ছে না।"

        # ৩. ফ্ল্যাশলাইট / টর্চ কন্ট্রোল
        elif "টর্চ অন" in cmd or "ফ্ল্যাশ অন" in cmd or "লাইট জ্বালাও" in cmd:
            os.system("termux-torch on > /dev/null 2>&1")
            reply = "টর্চলাইট অন করে দেওয়া হয়েছে Boss!"
        elif "টর্চ অফ" in cmd or "ফ্ল্যাশ অফ" in cmd or "লাইট বন্ধ" in cmd:
            os.system("termux-torch off > /dev/null 2>&1")
            reply = "টর্চলাইট বন্ধ করে দিয়েছি।"

        # ৪. ব্রাইটনেস কন্ট্রোল
        elif "ব্রাইটনেস বাড়াও" in cmd or "আলো বাড়াও" in cmd:
            os.system("termux-brightness 255 > /dev/null 2>&1")
            reply = "স্ক্রিন ব্রাইটনেস ফুল করে দেওয়া হয়েছে।"
        elif "ব্রাইটনেস কমাও" in cmd or "আলো কমাও" in cmd:
            os.system("termux-brightness 40 > /dev/null 2>&1")
            reply = "স্ক্রিন ব্রাইটনেস কমিয়ে সেভ মোডে রাখা হয়েছে।"

        # ৫. অন্যান্য সব সাধারণ বা জটিল প্রশ্নের জন্য Gemini AI
        else:
            reply = self.ask_gemini(user_input)

        self.add_chat_bubble("Assistant", reply)
        self.speak(reply)

    def on_send_text(self, instance):
        text = self.txt_input.text.strip()
        if text:
            self.txt_input.text = ""
            self.process_command(text)

    def clear_chat_screen(self, instance):
        self.chat_layout.clear_widgets()
        self.add_chat_bubble("Assistant", "স্ক্রিন ক্লিয়ার করা হয়েছে Boss!")

    def start_listening(self, instance):
        self.voice_btn.text = "🔴 শুনছি... কথা বলুন Boss"
        self.voice_btn.background_color = (1, 0.2, 0.2, 1)
        Clock.schedule_once(self.run_speech_recognition, 0.5)

    def run_speech_recognition(self, dt):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
                user_input = recognizer.recognize_google(audio, language="bn-BD")
                self.process_command(user_input)
            except Exception:
                self.add_chat_bubble("Assistant", "উফ Boss, আপনার কণ্ঠটি পরিষ্কার শুনতে পাইনি। আবার একটু বলুন!")
            finally:
                self.voice_btn.text = "🎙️ ভয়েস কমান্ড দিন (Tap to Speak)"
                self.voice_btn.background_color = (0.8, 0.1, 0.6, 1)

class UltimateSiriApp(App):
    def build(self):
        return UltimateSiriAssistantUI()

if __name__ == "__main__":
    UltimateSiriApp().run()
