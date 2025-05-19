import requests
from datetime import datetime
import csv
from gtts import gTTS
import os

# === Config ===
API_KEY = '6239b278e2047d244d62cb46bfac508f'
CITY = 'Tunis'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

# === Crop recommendations by month and weather ===
crop_recommendations = {
    1: {"Clear": ["ثوم", "بصل", "فاصوليا عريضة"], "Rain": ["بازلاء", "سبانخ"], "Thunderstorm": ["انتظر الطقس الهادئ قبل الزراعة."]},
    2: {"Clear": ["جزر", "فجل", "خس"], "Rain": ["سلق", "كالي"], "Thunderstorm": ["تجنب الزراعة خلال العواصف."]},
    3: {"Clear": ["طماطم", "فلفل", "خيار"], "Rain": ["بطاطا", "كراث"], "Thunderstorm": ["أوقف خطط الزراعة للسلامة."]},
    4: {"Clear": ["بطيخ", "قرع", "ذرة"], "Rain": ["فاصوليا", "كرنب"], "Thunderstorm": ["تأجيل الزراعة حتى يعود الطقس الجاف."]},
    5: {"Clear": ["بامية", "عباد الشمس", "كوسا"], "Rain": ["بطاطا حلوة"], "Thunderstorm": ["تم الكشف عن عاصفة. انتظر الزراعة."]},
    6: {"Clear": ["باذنجان", "فاصوليا خضراء", "خوخ"], "Rain": ["طماطم", "توت"], "Thunderstorm": ["انتظر توقف العاصفة قبل الزراعة."]},
    7: {"Clear": ["فلفل حار", "كوسا", "بطيخ"], "Rain": ["فاصوليا", "باذنجان"], "Thunderstorm": ["انتظر حتى تهدأ العاصفة."]},
    8: {"Clear": ["مشمش", "ذرة", "باذنجان"], "Rain": ["بطاطا حلوة", "طماطم"], "Thunderstorm": ["تجنب الزراعة خلال العواصف."]},
    9: {"Clear": ["كوسا", "خيار", "قرع"], "Rain": ["سبانخ", "جرجير"], "Thunderstorm": ["انتظر استقرار الطقس."]},
    10: {"Clear": ["طماطم", "بطاطا", "فلفل"], "Rain": ["كراث", "جزر"], "Thunderstorm": ["تأجيل الزراعة حتى هدوء الطقس."]},
    11: {"Clear": ["قرنبيط", "كرنب", "سبانخ"], "Rain": ["فاصوليا", "خس"], "Thunderstorm": ["انتظر الطقس الهادئ قبل الزراعة."]},
    12: {"Clear": ["ثوم", "بصل", "فاصوليا عريضة"], "Rain": ["سلق", "سبانخ"], "Thunderstorm": ["انتظر العاصفة ثم استأنف الزراعة."]},
}

# === Helpers ===
def get_current_month():
    return datetime.now().month

def give_farming_advice(weather_main):
    month = get_current_month()
    crops = crop_recommendations.get(month, {}).get(weather_main, [])
    if not crops:
        return "لا توجد توصية زراعية محددة اليوم. تابع مراقبة حالة الطقس."
    if isinstance(crops, list):
        return f"✅ يمكنك زراعة: {', '.join(crops)}."
    return f"⚠️ {crops}"

def fetch_weather():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()

        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        advice = give_farming_advice(weather_main)

        return weather_main, weather_desc, temp, advice

    except Exception as e:
        return "Error", str(e), "", "⚠️ فشل في جلب الطقس."

def log_to_csv(weather_main, weather_desc, temp, advice):
    with open('weather_log.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), weather_main, weather_desc, temp, advice])

# === Generate TTS (Text to Speech) for Weather Advice ===
def generate_tts(advice):
    tts = gTTS(advice, lang='ar')
    tts.save('weather_advice_arabic.mp3')  # Save the generated audio as 'weather_advice_arabic.mp3'

# === Main ===
if __name__ == "__main__":
    weather_main, weather_desc, temp, advice = fetch_weather()
    log_to_csv(weather_main, weather_desc, temp, advice)
    generate_tts(advice)  # Generate the text-to-speech audio for the advice
    print("✅ Weather data logged successfully.")
