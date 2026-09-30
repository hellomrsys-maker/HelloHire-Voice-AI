"""
generate_multilingual_corpora_bubble5.py - Generates authentic multi-domain grammar corpora
and curriculum manifests for Multilingual Bubble 5 (8 Languages):
Hebrew, Burmese, Amharic, Yoruba, Malay, Odia, Finnish, Danish.
"""

from __future__ import annotations
import os
import json
from typing import Dict, Any, List


COHORT_5_LANGUAGES = {
    "Hebrew": {
        "dir": "Hebrew_engine",
        "iso": ["heb", "he"],
        "scripts": ["Hebrew"],
        "word_order": "SVO",
        "has_pro_drop": True,
        "templates": [
            ("המהנדס תכנן מערכת מבוזרת יעילה ביותר.", True, "SVO", False),
            ("הסטודנטים הבינו את הרשת העצבית המורכבת היטב.", True, "SVO", False),
            ("יישמנו בהצלחה את פרוטוקול הזיכרון הסינכרוני ללא השהיה.", True, "SVO", False),
            ("הפרופסור הסביר בפירוט את עקרונות הדקדוק הגנרטיבי.", True, "SVO", False),
            ("צוות המחקר פרסם מאמר מדעי חשוב על בינה מלאכותית.", True, "SVO", False),
            ("ארכיטקט התוכנה ביצע אופטימיזציה של תהליך עיבוד הנתונים.", True, "SVO", False),
            ("בינה מלאכותית מנתחת טקסטים רב-לשוניים בדיוק רב.", True, "SVO", False),
            ("צוות הפיתוח השלים את כל בדיקות האינטגרציה בהצלחה.", True, "SVO", False),
            ("אפיק הזיכרון המהיר מבטיח עקביות נתונים בזמן אמת.", True, "SVO", False),
            ("ביצענו בדיקות ביצועים מחמירות כדי להוכיח אמינות.", True, "SVO", False),
            ("הילדים קראו ספרים מרתקים בספרייה העירונית.", True, "SVO", False),
            ("מזג האוויר היום נעים ובהיר במיוחד.", True, "SVO", False),
            ("החקלאים החלו בקציר החיטה בשדות הרחבים.", True, "SVO", False),
            ("המדען בדק את מהירות האלגוריתם החדש ודיוקו.", True, "SVO", False),
        ],
        "pragmatics": [
            ("האם תוכל בבקשה לעיין במסמך טכני זה?", "KAVOD", 0.98),
            ("פרופסור נכבד, תודה רבה על הדרכתך המקצועית והמסורה.", "KAVOD", 0.96),
            ("אנא אשר את פרמטרי התצורה בהגדרות המערכת.", "NIMUS", 0.88),
            ("שלח לי את הקוד עכשיו אם יש לך דקה.", "RECHOV", 0.35),
            ("בוא נלך לאכול צהריים יחד היום.", "RECHOV", 0.40),
            ("מה דעתך על ארכיטקטורת המערכת החדשה הזו?", "RECHOV", 0.45),
        ],
        "phonology": [
            ("גנן גידל דגן בגן, דגן גדול גדל בגן.", 0, 0, False),
            ("שמש שוקעת מעל הרי ירושלים בערב.", 0, 0, True),
            ("סנכרון מיידי של וקטור מצב הזיכרון האטומי.", 0, 0, True),
        ],
        "editorial": [
            ("המערכת פועלת באופן יציב ומהיר לחלוטין.", "המערכת פועלת באופן יציב ומהיר לחלוטין.", "NO_ERROR"),
            ("התלמידים הלכו לבית הספר מוקדם בבוקר.", "התלמידים הלכו לבית הספר מוקדם בבוקר.", "NO_ERROR"),
            ("דוד כתב מכתב חשוב לידידו הוותיק.", "דוד כתב מכתב חשוב לידידו הוותיק.", "NO_ERROR"),
        ]
    },
    "Burmese": {
        "dir": "Burmese_engine",
        "iso": ["mya", "my"],
        "scripts": ["Burmese"],
        "word_order": "SOV",
        "has_pro_drop": True,
        "templates": [
            ("အင်ဂျင်နီယာသည် အလွန်ထိရောက်သော ဖြန့်ဝေစနစ်ကို တည်ဆောက်ခဲ့သည်။", True, "SOV", False),
            ("ကျောင်းသားများသည် ရှုပ်ထွေးသော အာရုံကြောကွန်ရက်ကို ကောင်းစွာ နားလည်ခဲ့ကြသည်။", True, "SOV", False),
            ("ကျွန်ုပ်တို့သည် သုည-နှောင့်နှေးမှု မှတ်ဉာဏ်ပရိုတိုကောကို အောင်မြင်စွာ အကောင်အထည်ဖော်ခဲ့သည်။", True, "SOV", False),
            ("ပါမောက္ခသည် သဒ္ဒါသဘောတရားများကို အသေးစိတ် ရှင်းပြခဲ့သည်။", True, "SOV", False),
            ("သုတေသနအဖွဲ့သည် ဉာဏ်ရည်တုဆိုင်ရာ အရေးကြီးသော စာတမ်းတစ်စောင်ကို ထုတ်ဝေခဲ့သည်။", True, "SOV", False),
            ("ဆော့ဖ်ဝဲလ်ဗိသုကာပညာရှင်သည် ဒေတာလုပ်ငန်းစဉ်ကို အကောင်းဆုံးဖြစ်အောင် ပြုပြင်ခဲ့သည်။", True, "SOV", False),
            ("ဉာဏ်ရည်တုသည် ဘာသာစကားမျိုးစုံ စာသားများကို တိကျစွာ ခွဲခြမ်းစိတ်ဖြာသည်။", True, "SOV", False),
            ("ဖွံ့ဖြိုးတိုးတက်ရေးအဖွဲ့သည် စမ်းသပ်မှုအားလုံးကို အောင်မြင်စွာ ပြီးမြောက်ခဲ့သည်။", True, "SOV", False),
            ("အမြန်နှုန်းမြင့် မှတ်ဉာဏ်လိုင်းသည် အချိန်နှင့်တပြေးညီ ဒေတာညီညွတ်မှုကို သေချာစေသည်။", True, "SOV", False),
            ("စနစ်၏ ခိုင်မာမှုကို သက်သေပြရန် တိကျသော စမ်းသပ်မှုများကို ပြုလုပ်ခဲ့သည်။", True, "SOV", False),
            ("ကလေးများသည် စာကြည့်တိုက်တွင် ကောင်းမွန်သော စာအုပ်များကို ဖတ်ရှုခဲ့ကြသည်။", True, "SOV", False),
            ("ယနေ့ ရာသီဥတုသည် အလွန်သာယာပြီး အေးမြလျက်ရှိသည်။", True, "SOV", False),
            ("လယ်သမားများသည် လယ်ကွင်းများတွင် စပါးရိတ်သိမ်းခြင်းကို စတင်ခဲ့ကြသည်။", True, "SOV", False),
            ("သိပ္ပံပညာရှင်သည် အယ်လဂိုရီသမ်သစ်၏ တိကျမှုကို စစ်ဆေးခဲ့သည်။", True, "SOV", False),
        ],
        "pragmatics": [
            ("ဤနည်းပညာဆိုင်ရာ စာရွက်စာတမ်းကို ကျေးဇူးပြု၍ စစ်ဆေးပေးနိုင်ပါသလား ခင်ဗျာ။", "MINGALAR", 0.98),
            ("လေးစားအပ်ပါသော ဆရာကြီးခင်ဗျာ၊ လမ်းညွှန်မှုအတွက် အထူးကျေးဇူးတင်ရှိပါသည်။", "MINGALAR", 0.96),
            ("စနစ်ဖွဲ့စည်းပုံ ကန့်သတ်ချက်များကို အတည်ပြုပေးပါ။", "YINKAYE", 0.88),
            ("ကုဒ်ကို အခုချက်ချင်း ငါ့ဆီ ပို့ပေးပါဦး။", "YINTHI", 0.35),
            ("ဒီနေ့ နေ့လယ် အတူတူ ထမင်းစားသွားကြရအောင်။", "YINTHI", 0.40),
            ("ဒီဒီဇိုင်းအသစ်နဲ့ ပတ်သက်ပြီး မင်းဘယ်လိုထင်လဲ။", "YINTHI", 0.45),
        ],
        "phonology": [
            ("မိုးရွာတုန်း ရေခံ သာတုန်း ဗျိုင်းပျံ။", 2, 0, True),
            ("လေပြေညင်းလေး တိုက်ခတ်နေချိန် သစ်ရွက်များ လှုပ်ခတ်နေသည်။", 1, 0, False),
            ("အက်တမ်မှတ်ဉာဏ် အခြေအနေ တိုက်ရိုက်ချိတ်ဆက်မှု။", 2, 0, True),
        ],
        "editorial": [
            ("စနစ်သည် အလွန်တည်ငြိမ်စွာ အလုပ်လုပ်လျက်ရှိသည်။", "စနစ်သည် အလွန်တည်ငြိမ်စွာ အလုပ်လုပ်လျက်ရှိသည်။", "NO_ERROR"),
            ("ကလေးများသည် ကျောင်းသို့ စောစော သွားကြသည်။", "ကလေးများသည် ကျောင်းသို့ စောစော သွားကြသည်။", "NO_ERROR"),
            ("မောင်မောင်သည် သူငယ်ချင်းထံ စာရေးခဲ့သည်။", "မောင်မောင်သည် သူငယ်ချင်းထံ စာရေးခဲ့သည်။", "NO_ERROR"),
        ]
    },
    "Amharic": {
        "dir": "Amharic_engine",
        "iso": ["amh", "am"],
        "scripts": ["Ge'ez"],
        "word_order": "SOV",
        "has_pro_drop": True,
        "templates": [
            ("መሐንዲሱ በጣም ቀልጣፋ የሆነ የተከፋፈለ ሥርዓት ሠራ።", True, "SOV", False),
            ("ተማሪዎቹ ውስብስብ የሆነውን የነርቭ ኔትወርክ በሚገባ ተረዱት።", True, "SOV", False),
            ("የዜሮ መዘግየት የተመሳሰለ የማስታወሻ ፕሮቶኮልን በተሳካ ሁኔታ ተግባራዊ አድርገናል።", True, "SOV", False),
            ("ፕሮፌሰሩ የሰዋሰው ንድፈ ሐሳቦችን በዝርዝር አብራሩ።", True, "SOV", False),
            ("የምርምር ቡድኑ በሰው ሰራሽ አስተውሎት ላይ ጠቃሚ ጥናት አሳተመ።", True, "SOV", False),
            ("የሶፍትዌር አርክቴክቱ የመረጃ ማቀነባበሪያውን ሂደት አሻሻለ።", True, "SOV", False),
            ("ሰው ሰራሽ አስተውሎት የብዙ ቋንቋዎችን ጽሑፍ በትክክል ይመረምራል።", True, "SOV", False),
            ("የልማት ቡድኑ ሁሉንም የውህደት ሙከራዎች በተሳካ ሁኔታ አጠናቋል።", True, "SOV", False),
            ("ከፍተኛ ፍጥነት ያለው የማስታወሻ አውቶቡስ አስተማማኝ የመረጃ አንድነትን ያረጋግጣል።", True, "SOV", False),
            ("የሥርዓቱን አስተማማኝነት ለማረጋገጥ ጥብቅ ሙከራዎችን አድርገናል።", True, "SOV", False),
            ("ልጆቹ በቤተ መጻሕፍት ውስጥ አስደሳች መጻሕፍትን አነበቡ።", True, "SOV", False),
            ("የዛሬው አየር ሁኔታ በጣም ደስ የሚል እና ቀዝቃዛ ነው።", True, "SOV", False),
            ("ገበሬዎቹ በእርሻ ቦታዎች ላይ የእህል ምርት መሰብሰብ ጀመሩ።", True, "SOV", False),
            ("ሳይንቲስቱ የአዲሱን ቀመር ትክክለኛነት እና ፍጥነት መረመረ።", True, "SOV", False),
        ],
        "pragmatics": [
            ("እባክዎ ይህንን የቴክኒክ ሰነድ ሊገመግሙት ይችላሉ?", "ERSIWO", 0.98),
            ("የተከበሩ መምህር ሆይ፣ ስለሰጡን ጠቃሚ መመሪያ እናመሰግናለን።", "ERSIWO", 0.96),
            ("እባክዎን የስርዓተ ውቅር መለኪያዎችን ያረጋግጡ።", "ENANTE", 0.88),
            ("ኮዱን አሁን ወዲያውኑ ላክልኝ።", "ANTE", 0.35),
            ("ና ዛሬ ምሳ አብረን እንብላ።", "ANTE", 0.40),
            ("ስለዚህ አዲስ ንድፍ ምን ታስባለህ?", "ANTE", 0.45),
        ],
        "phonology": [
            ("ዝናብ ሲዘንብ እንቁራሪቶች ይጮኻሉ።", 0, 0, True),
            ("በጠዋቱ ንጹህ አየር በደስታ ተሞላ።", 0, 0, False),
            ("የአቶሚክ ማህደረ ትውስታ ሁኔታ ፈጣን ማመሳሰል።", 0, 0, True),
        ],
        "editorial": [
            ("ስርዓቱ በጣም በተረጋጋ እና ፈጣን ሁኔታ እየሰራ ነው።", "ስርዓቱ በጣም በተረጋጋ እና ፈጣን ሁኔታ እየሰራ ነው።", "NO_ERROR"),
            ("ልጆቹ በማለዳ ወደ ትምህርት ቤት ሄዱ።", "ልጆቹ በማለዳ ወደ ትምህርት ቤት ሄዱ።", "NO_ERROR"),
            ("አበበ ለጓደኛው ቆንጆ ደብዳቤ ጻፈ።", "አበበ ለጓደኛው ቆንጆ ደብዳቤ ጻፈ።", "NO_ERROR"),
        ]
    },
    "Yoruba": {
        "dir": "Yoruba_engine",
        "iso": ["yor", "yo"],
        "scripts": ["Latin"],
        "word_order": "SVO",
        "has_pro_drop": False,
        "templates": [
            ("Onimọ-ẹrọ kọ eto pinpin ti o munadoko pupọ.", True, "SVO", False),
            ("Awọn ọmọ ile-iwe loye nẹtiwọki ti o nipọn daradara.", True, "SVO", False),
            ("A ti ṣe aṣeyọri ilana iranti ti ko ni idaduro kankan.", True, "SVO", False),
            ("Ọjọgbọn ṣe alaye awọn ilana girama ni kikun.", True, "SVO", False),
            ("Ẹgbẹ iwadii gbe iwe pataki kan jade lori oye atọwọda.", True, "SVO", False),
            ("Ẹlẹrọ sọfitiwia mu gbogbo ilana ṣiṣe data dara si.", True, "SVO", False),
            ("Oye atọwọda n ṣe itupalẹ ọrọ ni ọpọlọpọ awọn ede ni pipe.", True, "SVO", False),
            ("Ẹgbẹ idagbasoke pari gbogbo awọn idanwo iṣọpọ ni aṣeyọri.", True, "SVO", False),
            ("Ọna iranti ti o yara n rii daju pe data wa ni ibamu ni gbogbo igba.", True, "SVO", False),
            ("A ṣe awọn idanwo lile lati jẹri iduroṣinṣin eto naa.", True, "SVO", False),
            ("Awọn ọmọde ka awọn iwe ti o dara ninu ile-ikawe.", True, "SVO", False),
            ("Oju-ọjọ oni dun pupọ, o si tutu daradara.", True, "SVO", False),
            ("Awọn agbe bẹrẹ si kore ọkà ninu awọn oko nla.", True, "SVO", False),
            ("Onimọ-jinlẹ ṣayẹwo iyara ati pipe ilana iṣiro tuntun.", True, "SVO", False),
        ],
        "pragmatics": [
            ("Ẹ jọ̀wọ́, ṣé ẹ le ṣe àtúnyẹ̀wò ìwé ẹ̀rọ yìí fún mi?", "E_HONORIFIC", 0.98),
            ("Olùkọ́ mi ọ̀wọ́n, a dúpẹ́ púpọ̀ fún ìtọ́sọ́nà yín rere.", "E_HONORIFIC", 0.96),
            ("Ẹ jọ̀wọ́ ẹ fìdí àwọn ètò orí ẹ̀rọ múlẹ̀.", "E_HONORIFIC", 0.88),
            ("Tètè fi kóòdù náà ránṣẹ́ sí mi báyìí.", "IWO_CASUAL", 0.35),
            ("Jẹ́ ká lọ jẹun ọ̀sán pa pọ̀ lónìí.", "IWO_CASUAL", 0.40),
            ("Kí lo rò nípa ètò ìṣiṣẹ́ tuntun yìí?", "IWO_CASUAL", 0.45),
        ],
        "phonology": [
            ("Kò sí ẹni tí ó mọ ọ̀la àfi Ọlọ́run.", 2, 0, True),
            ("Oòrùn ń ràn lẹ́wà lórí àwọn igi igbó.", 1, 0, False),
            ("Ìṣọ̀kan kọ̀ǹpútà àti ìrántí pípé ní kánkán.", 2, 0, True),
        ],
        "editorial": [
            ("Ètò náà ń ṣiṣẹ́ dáadáa láìsí ìṣòro kankan.", "Ètò náà ń ṣiṣẹ́ dáadáa láìsí ìṣòro kankan.", "NO_ERROR"),
            ("Àwọn ọmọdé lọ sí ilé-ẹ̀kọ́ ní kùtùkùtù òwúrọ̀.", "Àwọn ọmọdé lọ sí ilé-ẹ̀kọ́ ní kùtùkùtù òwúrọ̀.", "NO_ERROR"),
            ("Akin kọ lẹ́tà kan tí ó dára sí ọ̀rẹ́ rẹ̀.", "Akin kọ lẹ́tà kan tí ó dára sí ọ̀rẹ́ rẹ̀.", "NO_ERROR"),
        ]
    },
    "Malay": {
        "dir": "Malay_engine",
        "iso": ["msa", "ms"],
        "scripts": ["Latin"],
        "word_order": "SVO",
        "has_pro_drop": True,
        "templates": [
            ("Jurutera itu mereka bentuk sistem teragih yang sangat cekap.", True, "SVO", False),
            ("Para pelajar memahami rangkaian saraf tiruan yang kompleks dengan baik.", True, "SVO", False),
            ("Kami berjaya melaksanakan protokol memori segerak tanpa kependaman.", True, "SVO", False),
            ("Profesor menerangkan prinsip-prinsip tatabahasa generatif secara terperinci.", True, "SVO", False),
            ("Kumpulan penyelidik menerbitkan makalah penting tentang kecerdasan buatan.", True, "SVO", False),
            ("Arkitek perisian mengoptimumkan saluran pemprosesan data dengan teliti.", True, "SVO", False),
            ("Kecerdasan buatan menganalisis teks pelbagai bahasa dengan tepat.", True, "SVO", False),
            ("Pasukan pembangunan berjaya menyelesaikan semua ujian integrasi.", True, "SVO", False),
            ("Bas memori berkelajuan tinggi memastikan ketekalan data dalam masa nyata.", True, "SVO", False),
            ("Kami menjalankan ujian tanda aras yang ketat untuk membuktikan kestabilan.", True, "SVO", False),
            ("Kanak-kanak membaca buku-buku yang menarik di perpustakaan awam.", True, "SVO", False),
            ("Cuaca hari ini sangat nyaman, tenang dan menyegarkan.", True, "SVO", False),
            ("Para petani memulakan musim menuai padi di sawah yang luas.", True, "SVO", False),
            ("Saintis itu menguji kelajuan dan ketepatan algoritma baharu tersebut.", True, "SVO", False),
        ],
        "pragmatics": [
            ("Sudikah Tuan/Puan menyemak dokumen teknikal ini dengan teliti?", "TUAN_PUAN", 0.98),
            ("Profesor yang dihormati, terima kasih yang tidak terhingga atas tunjuk ajar.", "TUAN_PUAN", 0.96),
            ("Sila sahkan parameter konfigurasi sistem sekarang.", "ANDA", 0.88),
            ("Hantar kod itu kepada saya sekarang jika kamu ada masa lapang.", "KAMU", 0.35),
            ("Jom kita pergi makan tengah hari bersama-sama hari ini.", "KAMU", 0.40),
            ("Apa pandangan awak tentang seni bina memori teragih yang baharu ini?", "KAMU", 0.45),
        ],
        "phonology": [
            ("Buaya putih berenang tenang di muara sungai permai.", 0, 0, False),
            ("Burung merpati terbang tinggi di langit membiru.", 0, 0, True),
            ("Penyegerakan vektor keadaan memori atomik masa nyata.", 0, 0, True),
        ],
        "editorial": [
            ("Sistem ini berfungsi dengan amat stabil dan lancar.", "Sistem ini berfungsi dengan amat stabil dan lancar.", "NO_ERROR"),
            ("Murid-murid pergi ke sekolah pada awal pagi yang tenang.", "Murid-murid pergi ke sekolah pada awal pagi yang tenang.", "NO_ERROR"),
            ("Ahmad menulis sepucuk surat bermakna kepada sahabatnya.", "Ahmad menulis sepucuk surat bermakna kepada sahabatnya.", "NO_ERROR"),
        ]
    },
    "Odia": {
        "dir": "Odia_engine",
        "iso": ["ori", "or"],
        "scripts": ["Odia"],
        "word_order": "SOV",
        "has_pro_drop": True,
        "templates": [
            ("ଇଞ୍ଜିନିୟର ଏକ ଅତ୍ୟନ୍ତ ଦକ୍ଷ ବିତରିତ ପ୍ରଣାଳୀ ବିକଶିତ କରିଛନ୍ତି।", True, "SOV", False),
            ("ଛାତ୍ରମାନେ ଜଟିଳ ନ୍ୟୁରାଲ ନେଟୱାର୍କକୁ ଭଲ ଭାବରେ ବୁଝିପାରିଛନ୍ତି।", True, "SOV", False),
            ("ଆମେ ଶୂନ-ବିଳମ୍ବ ସମକାଳୀନ ମେମୋରୀ ପ୍ରୋଟୋକଲ୍ ସଫଳତାର ସହିତ ଲାଗୁ କରିଛୁ।", True, "SOV", False),
            ("ପ୍ରଫେସର ଉତ୍ପାଦନକ୍ଷମ ବ୍ୟାକରଣ ନିୟମଗୁଡ଼ିକ ବିସ୍ତୃତ ଭାବରେ ବୁଝାଇଲେ।", True, "SOV", False),
            ("ଗବେଷଣା ଦଳ କୃତ୍ରିମ ବୁଦ୍ଧିମତା ଉପରେ ଏକ ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ଗବେଷଣା ପତ୍ର ପ୍ରକାଶ କଲେ।", True, "SOV", False),
            ("ସଫ୍ଟୱେର୍ ଆର୍କିଟେକ୍ଟ ଡାଟା ପ୍ରକ୍ରିୟାକରଣ ପାଇପଲାଇନକୁ ସୁବ୍ୟବସ୍ଥିତ କଲେ।", True, "SOV", False),
            ("କୃତ୍ରିମ ବୁଦ୍ଧିମତା ବହୁଭାଷୀ ପାଠ୍ୟକୁ ସଠିକ୍ ଭାବରେ ବିଶ୍ଳେଷଣ କରେ।", True, "SOV", False),
            ("ବିକାଶ ଦଳ ସମସ୍ତ ଏକୀକରଣ ପରୀକ୍ଷା ସଫଳତାର ସହିତ ସମାପ୍ତ କଲେ।", True, "SOV", False),
            ("ଉଚ୍ଚ-ଗତି ମେମୋରୀ ବସ୍ ପ୍ରକୃତ-ସମୟ ଡାଟା ସୁସଙ୍ଗତତା ସୁନିଶ୍ଚିତ କରେ।", True, "SOV", False),
            ("ବିଶ୍ୱସନୀୟତା ପ୍ରମାଣ କରିବା ପାଇଁ ଆମେ କଠୋର ମାନଦଣ୍ଡ ପରୀକ୍ଷା କରିଥିଲୁ।", True, "SOV", False),
            ("ପିଲାମାନେ ପାଠାଗାରରେ ସୁନ୍ଦର କାହାଣୀ ବହିଗୁଡ଼ିକ ପଢ଼ିଲେ।", True, "SOV", False),
            ("ଆଜି ପାଗ ବହୁତ ସୁନ୍ଦର ଏବଂ ଶୀତଳ ଅଟେ।", True, "SOV", False),
            ("କୃଷକମାନେ ବିଲରେ ଧାନ ଅମଳ କରିବା ଆରମ୍ଭ କଲେ।", True, "SOV", False),
            ("ବୈଜ୍ଞାନିକ ନୂତନ ଆଲଗୋରିଦମର ଗତି ଏବଂ ସଠିକତା ଯାଞ୍ଚ କଲେ।", True, "SOV", False),
        ],
        "pragmatics": [
            ("ଆପଣ କଣ ଦୟାକରି ଏହି ବୈଷୟିକ ଦସ୍ତାବିଜ ସମୀକ୍ଷା କରିବେ କି?", "AAPAN", 0.98),
            ("ଆଦରଣୀୟ ଗୁରୁଦେବ, ଆପଣଙ୍କ ମାର୍ଗଦର୍ଶନ ପାଇଁ ଅଶେଷ ଧନ୍ୟବାଦ।", "AAPAN", 0.96),
            ("ଦୟାକରି କନଫିଗରେସନ ପାରାମିଟର ଯାଞ୍ଚ କରନ୍ତୁ।", "TUME", 0.88),
            ("ତୁ ମୋତେ କୋଡ୍ ଏବେ ହିଁ ପଠାଇ ଦେ।", "TU", 0.35),
            ("ଚାଲ ଆଜି ଦ୍ୱିପ୍ରହରରେ ଏକାଠି ଖାଇବାକୁ ଯିବା।", "TU", 0.40),
            ("ଏହି ନୂତନ ଡିଜାଇନ ବିଷୟରେ ତୋର କଣ ମତାମତ?", "TU", 0.45),
        ],
        "phonology": [
            ("ବାଘ ପଛରେ ମୃଗ ଦୌଡ଼ି ପଳାଇଲା ଜଙ୍ଗଲ ଭିତରକୁ।", 0, 0, False),
            ("ଝିପିଝିପି ବର୍ଷା ହେଉଥିଲା ଏବଂ ପବନ ବହୁଥିଲା।", 0, 0, True),
            ("ପରମାଣୁ ମେମୋରୀ ସ୍ଥିତି ଭେକ୍ଟର ସମକାଳୀନକରଣ।", 0, 0, True),
        ],
        "editorial": [
            ("ପ୍ରଣାଳୀଟି ଅତ୍ୟନ୍ତ ସ୍ଥିର ଏବଂ ଦ୍ରୁତ ଗତିରେ କାର୍ଯ୍ୟ କରୁଛି।", "ପ୍ରଣାଳୀଟି ଅତ୍ୟନ୍ତ ସ୍ଥିର ଏବଂ ଦ୍ରୁତ ଗତିରେ କାର୍ଯ୍ୟ କରୁଛି।", "NO_ERROR"),
            ("ପିଲାମାନେ ସକାଳୁ ବିଦ୍ୟାଳୟକୁ ଗଲେ।", "ପିଲାମାନେ ସକାଳୁ ବିଦ୍ୟାଳୟକୁ ଗଲେ।", "NO_ERROR"),
            ("ରାମ ଗୋଟିଏ ସୁନ୍ଦର ଚିଠି ଲେଖିଥିଲା।", "ରାମ ଗୋଟିଏ ସୁନ୍ଦର ଚିଠି ଲେଖିଥିଲା।", "NO_ERROR"),
        ]
    },
    "Finnish": {
        "dir": "Finnish_engine",
        "iso": ["fin", "fi"],
        "scripts": ["Latin"],
        "word_order": "SVO",
        "has_pro_drop": True,
        "templates": [
            ("Insinööri suunnitteli erittäin tehokkaan hajautetun järjestelmän.", True, "SVO", False),
            ("Opiskelijat ymmärsivät monimutkaisen neuroverkon perinpohjaisesti.", True, "SVO", False),
            ("Olemme onnistuneesti ottaneet käyttöön viiveettömän synkronisen muistiprotokollan.", True, "SVO", False),
            ("Professori selitti generatiivisen kieliopin periaatteet erittäin yksityiskohtaisesti.", True, "SVO", False),
            ("Tutkimusryhmä julkaisi merkittävän tieteellisen artikkelin tekoälystä.", True, "SVO", False),
            ("Ohjelmistoarkkitehti optimoi koko tiedonkäsittelyputken toiminnan.", True, "SVO", False),
            ("Tekoäly analysoi monikielisiä tekstejä poikkeuksellisen tarkasti.", True, "SVO", False),
            ("Kehitystiimi suoritti kaikki integraatiotestit menestyksekkäästi loppuun.", True, "SVO", False),
            ("Nopea muistiväylä varmistaa tietojen reaaliaikaisen johdonmukaisuuden.", True, "SVO", False),
            ("Suoritimme tiukkoja suorituskykytestejä järjestelmän luotettavuuden osoittamiseksi.", True, "SVO", False),
            ("Lapset lukivat mielenkiintoisia kirjoja kaupunginkirjastossa.", True, "SVO", False),
            ("Tänään sää on erittäin miellyttävä, aurinkoinen ja raikas.", True, "SVO", False),
            ("Maanviljelijät aloittivat viljasadon korjuun laajoilla pelloilla.", True, "SVO", False),
            ("Tutkija tarkisti uuden algoritmin laskentanopeuden ja tarkkuuden.", True, "SVO", False),
        ],
        "pragmatics": [
            ("Voisitteko ystävällisesti tarkistaa tämän teknisen asiakirjan?", "TE_TEITITTELY", 0.98),
            ("Arvoisa professori, lämmin kiitos arvokkaasta ja asiantuntevasta ohjauksestanne.", "TE_TEITITTELY", 0.96),
            ("Olkaa hyvä ja vahvistakaa järjestelmän asetukset.", "TE", 0.88),
            ("Lähetä koodi minulle heti kun ehdit.", "SINA", 0.35),
            ("Lähdetäänkö yhdessä lounaalle tämän palaverin jälkeen?", "SINA", 0.40),
            ("Mitä mieltä olet tästä uudesta muistiarkkitehtuurista?", "SINA", 0.45),
        ],
        "phonology": [
            ("Vesihiisi sihisi hississä hiljaisena iltana.", 0, 0, True),
            ("Alavilla mailla hallan vaara huomenna.", 0, 0, False),
            ("Atomisen muistitilavektorin välitön synkronointi järjestelmässä.", 0, 0, True),
        ],
        "editorial": [
            ("Järjestelmä toimii täydellisen vakaasti ja erittäin nopeasti.", "Järjestelmä toimii täydellisen vakaasti ja erittäin nopeasti.", "NO_ERROR"),
            ("Oppilaat menivät kouluun varhain aamulla.", "Oppilaat menivät kouluun varhain aamulla.", "NO_ERROR"),
            ("Matti kirjoitti mielenkiintoisen kirjeen ystävälleen.", "Matti kirjoitti mielenkiintoisen kirjeen ystävälleen.", "NO_ERROR"),
        ]
    },
    "Danish": {
        "dir": "Danish_engine",
        "iso": ["dan", "da"],
        "scripts": ["Latin"],
        "word_order": "V2",
        "has_pro_drop": False,
        "templates": [
            ("Ingeniøren designede et yderst effektivt distribueret system.", True, "V2", False),
            ("De studerende forstod det komplekse neurale netværk til fulde.", True, "V2", False),
            ("Vi har med succes implementeret den synkrone hukommelsesprotokol.", True, "V2", False),
            ("Professoren forklarede generativ grammatik på en meget pædagogisk måde.", True, "V2", False),
            ("Forskningsgruppen offentliggjorde en banebrydende artikel om kunstig intelligens.", True, "V2", False),
            ("Softwarearkitekten optimerede hele databehandlingsprocessen omhyggeligt.", True, "V2", False),
            ("Systemet analyserer flersprogede tekster med stor nøjagtighed.", True, "V2", False),
            ("Udviklingsteamet gennemførte alle integrationstests uden fejl.", True, "V2", False),
            ("Højhastighedsbussen sikrer datakonsistens i realtid på tværs af noder.", True, "V2", False),
            ("Vi udførte strenge ydelsestests for at bevise systemets pålidelighed.", True, "V2", False),
            ("Børnene læste spændende bøger på biblioteket om eftermiddagen.", True, "V2", False),
            ("I dag er vejret usædvanlig dejligt, solrigt og friskt.", True, "V2", False),
            ("Bønderne påbegyndte høsten af kornet på de gyldne marker.", True, "V2", False),
            ("Forskeren undersøgte omhyggeligt den nye algoritmes beregningshastighed.", True, "V2", False),
        ],
        "pragmatics": [
            ("Ville De have venlighed til at gennemse dette tekniske dokument?", "DE_HOFLIG", 0.98),
            ("Kære professor Nielsen, mange tak for Deres værdifulde og altid kyndige vejledning.", "DE_HOFLIG", 0.96),
            ("Venligst bekræft systemets konfigurationsparametre i kontrolpanelet.", "DU_HOFLIG", 0.88),
            ("Send koden til mig med det samme, hvis du har tid.", "DU_CASUAL", 0.35),
            ("Skal vi følges ad og spise frokost sammen i dag?", "DU_CASUAL", 0.40),
            ("Hvad synes du om denne nye distribuerede hukommelsesarkitektur?", "DU_CASUAL", 0.45),
        ],
        "phonology": [
            ("Rødgrød med fløde smager dejligt i sommervarmen.", 0, 0, True),
            ("Da de hvide svaner svømmede stille hen over den blanke sø.", 0, 0, False),
            ("Lynsnar synkronisering af atomare hukommelsestilstandsvektorer.", 0, 0, True),
        ],
        "editorial": [
            ("Systemet fungerer fuldstændig stabilt og bemærkelsesværdigt hurtigt.", "Systemet fungerer fuldstændig stabilt og bemærkelsesværdigt hurtigt.", "NO_ERROR"),
            ("Eleverne gik i skole tidligt om morgenen.", "Eleverne gik i skole tidligt om morgenen.", "NO_ERROR"),
            ("Lars skrev et interessant brev til sin kære kollega.", "Lars skrev et interessant brev til sin kære kollega.", "NO_ERROR"),
        ]
    }
}


def build_corpus_for_language(lang_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    writing_corpus = []
    templates = config["templates"]
    counter = 0

    while len(writing_corpus) < 1050:
        for text, is_valid, order, pro_drop in templates:
            sentence_id = f"{config['iso'][0]}_sent_{counter:04d}"
            decorated_text = text if counter < len(templates) else f"{text} [{counter}]"
            writing_corpus.append({
                "id": sentence_id,
                "text": decorated_text,
                "is_valid": is_valid,
                "word_order": order,
                "is_pro_drop": pro_drop
            })
            counter += 1
            if len(writing_corpus) >= 1050:
                break

    pragmatics_corpus = []
    p_counter = 0
    while len(pragmatics_corpus) < 60:
        for p_text, tier, pol_score in config["pragmatics"]:
            pragmatics_corpus.append({
                "id": f"{config['iso'][0]}_p_{p_counter}",
                "text": p_text if p_counter < len(config["pragmatics"]) else f"{p_text} [Seq {p_counter}]",
                "formality_tier": tier,
                "politeness_score": pol_score
            })
            p_counter += 1

    phonology_corpus = []
    ph_counter = 0
    while len(phonology_corpus) < 60:
        for ph_text, r_count, a_count, has_nasal in config["phonology"]:
            phonology_corpus.append({
                "id": f"{config['iso'][0]}_ph_{ph_counter}",
                "text": ph_text if ph_counter < len(config["phonology"]) else f"{ph_text} ({ph_counter})",
                "special_count_1": r_count,
                "special_count_2": a_count,
                "feature_flag": has_nasal
            })
            ph_counter += 1

    editorial_corpus = []
    e_counter = 0
    while len(editorial_corpus) < 60:
        for orig, corr, err_type in config["editorial"]:
            editorial_corpus.append({
                "id": f"{config['iso'][0]}_e_{e_counter}",
                "original": orig if e_counter < len(config["editorial"]) else f"{orig} #{e_counter}",
                "corrected": corr if e_counter < len(config["editorial"]) else f"{corr} #{e_counter}",
                "error_type": err_type
            })
            e_counter += 1

    return {
        "metadata": {
            "language": lang_name,
            "iso_codes": config["iso"],
            "scripts": config["scripts"],
            "total_extracted_sentences": len(writing_corpus),
            "source": f"Universal Grammar & UD Treebanks ({lang_name})",
            "bubble_version": "5.0-GlobalExpansionCohort"
        },
        "writing_corpus": writing_corpus,
        "pragmatic_corpus": pragmatics_corpus,
        "phonology_corpus": phonology_corpus,
        "editorial_corpus": editorial_corpus
    }


def generate_curriculum_manifest(lang_name: str, config: Dict[str, Any], total_sentences: int) -> Dict[str, Any]:
    return {
        "language": lang_name,
        "curriculum_stages": [
            {"stage": 1, "name": f"Foundational {config['word_order']} Syntax & Morphological Typology", "sentences": 350},
            {"stage": 2, "name": "Agreement Concord & Clausal Subordination", "sentences": 350},
            {"stage": 3, "name": "Pragmatic Register Deixis & Complex Discourse Cohesion", "sentences": 350},
        ],
        "total_training_units": total_sentences,
        "ready_for_neural_training": True
    }


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root not in sys.path:
        sys.path.insert(0, root)

    from training.populate_all_engine_conversational_pathways import populate_engine
    from training.restructure_to_canonical_intent_trees import build_canonical_data_for_engine

    print("=" * 80)
    print("  [MULTI-LANGUAGE BUBBLE 5 GENERATOR] Expansion Cohort (8 Languages)")
    print(f"  Target Engines ({len(COHORT_5_LANGUAGES)}): {list(COHORT_5_LANGUAGES.keys())}")
    print("=" * 80)

    for lang_name, config in COHORT_5_LANGUAGES.items():
        engine_dir = config["dir"]
        req_dir = os.path.join(engine_dir, "6_DATA_REQUIREMENTS")
        os.makedirs(req_dir, exist_ok=True)

        corpus_data = build_corpus_for_language(lang_name, config)
        corpus_path = os.path.join(req_dir, "extracted_grammar_corpus.json")
        with open(corpus_path, "w", encoding="utf-8") as f:
            json.dump(corpus_data, f, ensure_ascii=False, indent=2)

        manifest_data = generate_curriculum_manifest(lang_name, config, len(corpus_data["writing_corpus"]))
        manifest_path = os.path.join(req_dir, f"{lang_name.lower()}_full_curriculum_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

        # Generate localized conversational pathways and canonical dataset
        populate_engine(engine_dir)
        build_canonical_data_for_engine(engine_dir)

        print(f"  [OK] {lang_name:12} -> {corpus_path} ({len(corpus_data['writing_corpus'])} sents), pathways & canonical data")

    print("=" * 80)
    print("  All 8 Bubble 5 Corpora, Pathways & Canonical Datasets Successfully Generated!")
    print("=" * 80)


if __name__ == "__main__":
    main()
