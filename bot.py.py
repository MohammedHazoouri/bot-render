from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import BotCommand
from telegram.request import HTTPXRequest
from googleapiclient.discovery import build
from telegram.request import HTTPXRequest
import requests
import pandas as pd
import io
import datetime

request = HTTPXRequest(
       connect_timeout=60.0,  # مهلة الاتصال
       read_timeout=60.0,     # مهلة القراءة
       write_timeout=60.0,    # مهلة الكتابة
       pool_timeout=60.0
   )
#--------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------- 
csvurl1 = "https://docs.google.com/spreadsheets/d/1g0k8NeXDUP2esAWd7_omYRKrrRn1gn7EjthPyvv6j1A/gviz/tq?tqx=out:csv"
sheet1 = None
def load_sheets():
    global sheet1
    try:
        r1 = requests.get(csvurl1, timeout=20)
        r1.raise_for_status()
        sheet1 = pd.read_csv(io.BytesIO(r1.content), encoding="utf-8", on_bad_lines="skip")
        print("✅ تم تحديث البيانات من Google Sheets")
    except Exception as e:
        sheet1 = None
        print(f"⚠️ خطأ أثناء تحديث البيانات: {e}")
#--------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------- 
def getbalancefrom_sheet1():
    global sheet1
    load_sheets()
    if sheet1 is None or sheet1.empty:
        return 0
    try:
        col_balance = sheet1["الرصيد الجديد"].dropna().tolist()
        for val in reversed(col_balance):
            try:
                return int(str(val).strip())
            except:
                continue
        return 0
    except Exception as e:
        print(f"⚠️ خطأ أثناء قراءة الرصيد: {e}")
        return 0
#--------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------- 
FORMURL = "https://docs.google.com/forms/d/e/1FAIpQLSfzaGxh6Zw8TROklDq0oZZbvoyN-0FlPXG1Q7Xyc_wTL2lCXA/formResponse?usp=dialog"
def sendtoform(operation, points):
    today = str(datetime.date.today())
    data = {
        "entry.984469603": operation,   # غيّر الرقم حسب الفورم
        "entry.2143204570": points,
    }
    r = requests.post(FORMURL, data=data)
    return r.status_code == 200
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------        
def colloculation_summary():
    global sheet1
    load_sheets()
    if sheet1 is None or sheet1.empty:
        return "⚠️ لا توجد بيانات اليوم."
    today = str(datetime.date.today())
    todayrows = sheet1[sheet1["Timestamp"].astype(str).str.startswith(today)]
    if todayrows.empty:
        return "⚠️ لا توجد عمليات مسجلة اليوم."
    gained = todayrows[todayrows["النقاط (+ أو −)"] > 0]["النقاط (+ أو −)"].sum()
    consumed = todayrows[(todayrows["النقاط (+ أو −)"] < 0) & (todayrows["العملية"].str.contains("أكلة|مشوار|أغنية|استراحة|حلقة"))]["النقاط (+ أو −)"].sum()
    deducted = todayrows[(todayrows["النقاط (+ أو −)"] < 0) & (todayrows["العملية"].str.contains("تسميعة تحت|يوم بلا|خطأ كبير"))]["النقاط (+ أو −)"].sum()
    summary = (
    f"📊 ملخص اليوم:\n"
    f"✅ النقاط المكتسبة: {gained}\n"
    f"🎁 النقاط المستهلكة (جوائز): {abs(consumed)}\n"
    f"⚠️ النقاط المخصومة (خصومات): {abs(deducted)}"
    )
    return summary
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------       
async def setup_commands(app):
    commands = [
        BotCommand("start", "بدء المحادثة"),
        BotCommand("help", "المواد"),
        BotCommand("about", "حول البوت")
    ]
    await app.bot.set_my_commands(commands)

#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
main_keyboard = ReplyKeyboardMarkup(
    [["📝 الإنجازات", "🏆 الجوائز "],
     ["⚠️ الخصومات"],
     ["ملخص اليوم", "نقاطي"],
     ["⚙️ تواصل - اقتراحات", "ما فائدة البوت"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("الله معو الاستاذ ...", reply_markup=main_keyboard)
    await update.message.reply_text("الرجاء الاختيار 😊", reply_markup=main_keyboard)
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chatid = update.message.chat.id

    if text == "ما فائدة البوت":
        await update.message.reply_text("رح تصير تشتغل بحياتك على نظام لعبة وتجميع نقاط") 
        await update.message.reply_text(" ما في رقيب فيك تغش") 
        await update.message.reply_text("بس اذا بدك تغش ليش عم تشتغل عليه اساسا")  
        await update.message.reply_text("هو بيعتمد عصدقك مع حالك محدا رح يشوف شو عم تعمل ولا شو عملت ولا الى اخره")  
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "📝 الإنجازات":
        new_keyboard = [["تسميعة فوق 90%","تسميعة فوق 95%"], ["تسميعة 100%"], ["جلسة بومودورو"], ["يوم بلا خبز","يوم بلا سكر"], ["يوم بلا إنستا/فيس/يوتيوب تافه"],["🔙 رجوع"]]
        newmarkup = ReplyKeyboardMarkup(new_keyboard, resize_keyboard=True)
        await update.message.reply_text("💡 اختر ", reply_markup=newmarkup)   

    elif text == "تسميعة فوق 90%":
        ok = sendtoform("تسميعة فوق 90%", 5)
        msg = "✅ سجلت تسميعة فوق 90% (+5)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg) 

    elif text == "تسميعة فوق 95%":
        ok = sendtoform(" تسميعة فوق 95%", 10)
        msg = "✅ سجلت تسميعة فوق 95% (+10)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)

    elif text == "تسميعة 100%":
        ok = sendtoform("تسميعة 100%", 30)
        msg = "✅ سجلت تسميعة 100% (+30)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)

    elif text == "جلسة بومودورو":
        ok = sendtoform("جلسة بومودورو", 2)
        msg = "✅ سجلت جلسة بومودورو (+2)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)

    elif text == "يوم بلا خبز":
        ok = sendtoform("يوم بلا خبز", 5)
        msg = "✅ سجلت يوم بلا خبز (+5)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)

    elif text == "يوم بلا سكر":
        ok = sendtoform("يوم بلا سكر ", 5)
        msg = "✅ سجلت يوم بلا سكر (+5)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)

    elif text == "يوم بلا إنستا/فيس/يوتيوب تافه":
        ok = sendtoform("يوم بلا إنستا/فيس/يوتيوب تافه", 10)
        msg = "✅ يوم بلا إنستا/فيس/يوتيوب تافه (+10)." if ok else "⚠️ خطأ بالإرسال."
        await update.message.reply_text(msg)                      
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "🏆 الجوائز":
        new_keyboard = [["سماع أغنية (5 دقائق)","أكلة طيبة "], ["مشوار/حضور مباراة"], ["مكالمة طويلة/دردشة واتس"], ["استراحة نصف ساعة","نصف ساعة: برمجة/نشاط خارج الدرس"], ["حلقة مسلسل/انمي"],["🔙 رجوع"]]
        newmarkup = ReplyKeyboardMarkup(new_keyboard, resize_keyboard=True)
        await update.message.reply_text("💡 اختر ", reply_markup=newmarkup)

    elif text == "سماع أغنية (5 دقائق)":
        balance = getbalancefrom_sheet1()
        cost = 2
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("سماع أغنية (5 دقائق)", -2)
            msg = "  خصمت 2 نقطة مقابل سماع أغنية (5 دقائق)." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "أكلة طيبة ":
        balance = getbalancefrom_sheet1()
        cost = 10
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("أكلة طيبة", -cost)
            msg = "🍽 خصمت 10 نقاط مقابل أكلة طيبة." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "مشوار/حضور مباراة":
        balance = getbalancefrom_sheet1()
        cost = 100
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("مشوار/حضور مباراة", -cost)
            msg = "🏟 خصمت 100 نقاط مقابل مشوار/حضور مباراة." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "مكالمة طويلة/دردشة واتس":
        balance = getbalancefrom_sheet1()
        cost = 10
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("أكلة طيبة", -10)
            msg = " خصمت 10 نقاط مكالمة طويلة/دردشة واتس." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "استراحة نصف ساعة":
        balance = getbalancefrom_sheet1()
        cost = 6
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("استراحة نصف ساعة", -6)
            msg = " خصمت 6 نقاط مقابل استراحة نصف ساعة ." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "نصف ساعة: برمجة/نشاط خارج الدرس":
        balance = getbalancefrom_sheet1()
        cost = 10
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("نصف ساعة: برمجة/نشاط خارج الدرس", -10)
            msg = " خصمت 3 نقاط مقابل نصف ساعة: برمجة/نشاط خارج الدرس ." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "حلقة مسلسل/انمي":
        balance = getbalancefrom_sheet1()
        cost = 20
        if balance < cost:
            await update.message.reply_text("⚠️ لا يوجد رصيد كافي لتنفيذ هذه الجائزة، انقبر روح اعمول انجاز حضاري")
        else:
            ok = sendtoform("حلقة مسلسل/انمي", -20)
            msg = " خصمت 20 نقاط مقابل حلقة مسلسل/انمي ." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)          
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "⚠️ الخصومات":
        new_keyboard = [["يوم بلا أي جلسة بومودورو ","تسميعة تحت 80%"], ["عمل سيء (تعتبره خطأ كبير)"],["🔙 رجوع"]]
        newmarkup = ReplyKeyboardMarkup(new_keyboard, resize_keyboard=True)
        await update.message.reply_text("💡 اختر ", reply_markup=newmarkup)

    elif text == "يوم بلا أي جلسة بومودورو ":
        balance = getbalancefrom_sheet1()
        cost = 20
        if balance <= cost:
            ok = sendtoform("يوم بلا أي جلسة بومودورو", -balance)
            msg = f"⚠️ تم تصفير رصيدك. رصيدك الآن: 0 نقطة" if ok else "⚠️ خطأ بالإرسال."
        else:
            ok = sendtoform("يوم بلا أي جلسة بومودورو", -20)
            msg = " خصمت 20 نقاط  يوم بلا أي جلسة بومودورو ." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "تسميعة تحت 80%":
        balance = getbalancefrom_sheet1()
        cost = 20
        if balance <= cost:
            ok = sendtoform("تسميعة تحت 80%", -balance)
            msg = f"⚠️ تم تصفير رصيدك. رصيدك الآن: 0 نقطة" if ok else "⚠️ خطأ بالإرسال."
        else:
            ok = sendtoform("تسميعة تحت 80%", -20)
            msg = " خصمت 20 نقاط  تسميعة تحت 80% ." if ok else "⚠️ خطأ بالإرسال."
            await update.message.reply_text(msg)

    elif text == "عمل سيء (تعتبره خطأ كبير)":
        current = getbalancefrom_sheet1()
        ok = sendtoform("تصفير بسبب خطأ كبير", -current)
        if ok:
            await update.message.reply_text(f"⚠️ تم تصفير رصيدك. رصيدك الآن: 0 نقطة")
        else:
          await update.message.reply_text("⚠️ خطأ أثناء محاولة التصفير.")
#--------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------- 
    elif text == "⚙️ تواصل - اقتراحات":
        await update.message.reply_text("@M_HAZZOURY")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "نقاطي":
        balance = getbalancefrom_sheet1()
        await update.message.reply_text(f"📊 رصيدك الحالي: {balance} نقطة")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "ملخص اليوم":
        summary = colloculation_summary()
        await update.message.reply_text(summary)    
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    elif text == "🔙 رجوع":
        await update.message.reply_text("رجعت للقائمة الرئيسية 👇", reply_markup=main_keyboard)
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
    else:
        await update.message.reply_text("🚫 لم أفهم الأمر. الرجاء اختيار أحد الأزرار من الكيبورد.")
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
     
def main():
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = Application.builder().token("8083257429:AAEbtz5zQIifEkJhdVyvkbKy2IwCqh1PQMs").request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot is running...")
    app.run_polling(poll_interval=2.0)

if __name__ == '__main__':
    main()





  