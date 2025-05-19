import pandas as pd
import streamlit as st
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from gtts import gTTS
import io

# Function to get weather log from CSV
def get_weather_log():
    try:
        df = pd.read_csv('weather_log.csv', header=None, names=['Timestamp', 'Weather', 'Description', 'Temperature', 'Advice'])
        if df.empty:
            st.write("سجل الطقس فارغ.")
        return df
    except FileNotFoundError:
        st.error("ملف سجل الطقس 'weather_log.csv' غير موجود.")
        return pd.DataFrame()

# Function to generate farming advice based on the weather condition and the month
def give_farming_advice(weather_main, current_month):
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

    recommendations = crop_recommendations.get(current_month, {}).get(weather_main, "لا توجد نصائح خاصة لليوم. استمر في متابعة الطقس.")
    if isinstance(recommendations, list):
        return f"✅ يمكنك زراعة: {', '.join(recommendations)}."
    else:
        return f"⚠️ {recommendations}"

# Load tokenizer and model safely
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("asafaya/bert-base-arabic")
    model = AutoModelForQuestionAnswering.from_pretrained("asafaya/bert-base-arabic", low_cpu_mem_usage=False, torch_dtype=None)
    return tokenizer, model

tokenizer, model = load_model()

# Function to get an answer from the context
def get_answer(question, context):
    inputs = tokenizer(question, context, add_special_tokens=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer_tokens = inputs.input_ids[0][answer_start:answer_end]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
    return answer

# Expanded agriculture context (Richer answers)
context = """
أفضل وقت لزراعة الطماطم هو عندما تكون درجات الحرارة ما بين 18 إلى 24 درجة مئوية، وعادةً في أشهر أبريل ومايو.
إذا كنت في مناطق ذات مناخ دافئ، يمكن زراعتها في بداية الربيع. يجب تجنب الزراعة عندما تكون درجات الحرارة أقل من 10 درجات مئوية، لأن ذلك قد يؤثر سلباً على نمو النبات.

أسباب اصفرار أوراق الطماطم تشمل نقص النيتروجين في التربة، زيادة الري، نقص الضوء، أو أمراض فطرية. من المهم إجراء اختبار للتربة لتحديد مستوى العناصر الغذائية. يمكن تحسين خصوبة التربة بإضافة السماد العضوي والدبال بشكل دوري.

لحماية المحاصيل من الجراد، يجب استخدام شبكات واقية أو رش مبيدات حيوية طبيعية مثل النيم. من الأفضل تجنب استخدام المبيدات الكيميائية قدر الإمكان للحفاظ على البيئة والتنوع البيولوجي.

أفضل طريقة لري الطماطم هي الري بالتنقيط، حيث يساعد ذلك في توفير الماء وتقليل خطر الأمراض النباتية. يُفضل سقي النباتات في الصباح الباكر أو مساءً لتقليل التبخر الناتج عن الحرارة.

عند زراعة الذرة، يجب التأكد من أن التربة خصبة وجيدة التهوية مع ري منتظم، خاصة أثناء مرحلة التزهير. يجب زراعة الذرة في مناطق مشمسة لتأمين نموها الجيد.

زراعة الفلفل تحتاج إلى درجات حرارة معتدلة وتربة جيدة الصرف مع توفير سماد غني بالبوتاسيوم. يمكن زراعة الفلفل في شهري أبريل ومايو في المناطق المعتدلة.

أفضل وقت لزراعة الخيار هو من مارس إلى يونيو حسب المنطقة. يفضل زراعته في تربة جيدة التصريف مع توافر الضوء الكافي.

لحماية النباتات من الرياح الشديدة، يمكن استخدام مصدات رياح طبيعية مثل الأشجار أو تركيب حواجز صناعية.

زراعة البطاطا في المناخ الحار تتم من فبراير إلى مارس لتجنب الحرارة الشديدة في الصيف، مما يساعد على نمو جيد.

كيف يمكن تحسين خصوبة التربة؟ يمكن تحسين خصوبة التربة بإضافة السماد العضوي والدبال بانتظام. إضافة الكومبوست والمواد العضوية الأخرى يمكن أن يساعد في تحسين بنية التربة وزيادة محتوى المغذيات.

أسباب تساقط أزهار الطماطم يمكن أن تشمل درجات الحرارة المرتفعة أو انخفاض الرطوبة، بالإضافة إلى نقص العناصر الغذائية مثل البوتاسيوم أو الفوسفور. قد يكون أيضاً نتيجة لنقص التلقيح.
"""

# UI Start
st.title("مساعد الطقس والزراعة 🌱🌦️")

# Weather Section
st.header("اتجاهات الطقس")
df = get_weather_log()
if df.empty:
    st.write("لا توجد بيانات الطقس لعرضها.")
else:
    st.write(df.tail())

    try:
        df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    except Exception as e:
        st.error(f"خطأ في تحويل بيانات الحرارة: {e}")

    if not df['Temperature'].isnull().all():
        st.line_chart(df['Temperature'])
    else:
        st.write("بيانات الحرارة مفقودة أو غير صحيحة.")

    latest_weather = df.iloc[-1]['Weather']
    current_month = datetime.now().month
    current_advice = give_farming_advice(latest_weather, current_month)

    st.header("النصيحة الزراعية الحالية")
    st.success(current_advice)

# Question Answering Section
st.header("الإجابة على الأسئلة الزراعية")
st.write("اسأل سؤالاً عن الزراعة، وسنقدم لك إجابة مع إمكانية الاستماع لها.")

user_question = st.text_input("📝 اكتب سؤالك هنا:")

if user_question:
    answer = get_answer(user_question, context)
    if answer.strip():
        st.info(f"الإجابة: {answer}")
        audio_option = st.radio("🎧 هل ترغب في سماع الإجابة؟", ("نعم", "لا"))
        if audio_option == "نعم":
            tts = gTTS(answer, lang='ar')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            st.audio(audio_buffer, format="audio/mp3")
    else:
        st.warning("❗ لم يتم العثور على إجابة دقيقة. حاول طرح سؤال آخر.")
