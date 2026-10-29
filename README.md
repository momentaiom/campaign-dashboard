# لوحة متابعة حملة إيميلات تنويل

Built by Moment Plus · © 2026 Moment Plus

لوحة تعرض تقدّم الحملة من SendGrid بشكل شبه مباشر (كل 5 دقائق تقريباً).

## كيف تعمل

- **GitHub Actions** يشغّل `scripts/fetch_stats.py` كل 5 دقائق، يسحب الأرقام من SendGrid بمفتاح محفوظ كـ Secret، ويحفظها في `data.json`.
- **GitHub Pages** يعرض `index.html` اللي يقرأ `data.json` ويتحدث تلقائياً كل دقيقة.
- مفتاح SendGrid **لا يظهر أبداً** في الصفحة أو الكود.

## الملفات

| الملف | الوظيفة |
|---|---|
| `index.html` | لوحة المتابعة |
| `config.json` | اسم الحملة، الدومين، تاريخ البداية، وجدول الدفعات (عدّله من هنا) |
| `data.json` | الأرقام (يتحدث تلقائياً، لا تعدّله) |
| `scripts/fetch_stats.py` | يسحب الأرقام من SendGrid |
| `.github/workflows/update-stats.yml` | التشغيل التلقائي كل 5 دقائق |

## خطوات التشغيل

### 1. مفتاح API للقراءة فقط
في SendGrid: **Settings ← API Keys ← Create API Key**
- الاسم: `dashboard-stats`
- النوع: **Restricted Access**
- فعّل **Stats** على **Read Access** فقط، وخلّ الباقي **No Access**
- انسخ المفتاح (يظهر مرة واحدة)

### 2. ارفع الملفات على GitHub
أنشئ Repository جديد وارفع كل الملفات **مع مجلد `.github`** (مجلد مخفي، تأكد إنه انرفع).

### 3. أضف المفتاح كـ Secret
في الـ Repository: **Settings ← Secrets and variables ← Actions ← New repository secret**
- Name: `SENDGRID_API_KEY`
- Secret: الصق المفتاح

### 4. اسمح لـ Actions بالكتابة
**Settings ← Actions ← General ← Workflow permissions** ← اختر **Read and write permissions** ← Save

### 5. فعّل GitHub Pages
**Settings ← Pages** ← Source: **Deploy from a branch** ← Branch: `main` / `/ (root)` ← Save
بعد دقيقة يظهر رابط مثل: `https://USERNAME.github.io/REPO/`

### 6. شغّل أول تحديث يدوياً
**Actions ← Update SendGrid stats ← Run workflow**
بعد دقيقة إلى دقيقتين يظهر "مباشر" في اللوحة.

## ملاحظات

- **التوقيت:** GitHub يشغّل المهام المجدولة كل 5 دقائق كحد أدنى، وأحياناً يتأخر عدة دقائق وقت الضغط. اللوحة تعرض "آخر تحديث قبل X د".
- **الأرقام تشمل كل إيميلات الحساب** من تاريخ `start_date`، بما فيها الإيميلات التجريبية.
- **نسبة الفتح** تقريبية، لأن بعض برامج البريد (مثل Apple Mail) تفتح الإيميل تلقائياً.
- **Repository عام أو خاص:** GitHub Pages مجاني للـ Repository العام. الملف `data.json` فيه أرقام فقط بدون أي إيميلات. للـ Repository الخاص مع Pages تحتاج باقة GitHub مدفوعة.
- **بعد انتهاء الحملة:** عطّل الـ workflow من **Actions ← Update SendGrid stats ← ⋯ ← Disable workflow**، واحذف المفتاح من SendGrid.
