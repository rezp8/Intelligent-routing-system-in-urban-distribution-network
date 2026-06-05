# سامانه هوشمند مسیریابی در شبکه توزیع شهری
## Intelligent Routing System in Urban Distribution Network

---

## اعضای تیم

| نام | نقش |
|-----|------|
| علیرضا نصیری | زیرساخت + UCS + IDA* |
| رضا پیردیر | A* + الگوریتم ژنتیک |

---

## معرفی پروژه

این سامانه مسیریابی بهینه برای خودروهای حمل‌بار در یک شبکه شهری شطرنجی را پیاده‌سازی می‌کند.
نقشه ورودی یک ماتریس `M × N` است که شامل موارد زیر است:

| نماد | معنا |
|------|------|
| `S` / `Si` | نقطه شروع عامل / عامل i |
| `G` / `Gi` | مقصد تحویل / مقصد i |
| `1`–`9` | خانه عادی با هزینه ورود مشخص |
| `Z` | منطقه با محدودیت زمانی (چرخه ۳۰ دقیقه‌ای) |
| `Bk` | خانه پل با هزینه ورود k |

---

## ساختار پروژه

```
.
├── README.md
├── main.py                  # نقطه ورود — --scenario و --map
├── models/
│   ├── __init__.py
│   ├── map_grid.py          # کلاس MapGrid (parse + هزینه + پل + Z)
│   └── node.py              # کلاس Node (state + g + parent + action)
├── algorithms/
│   ├── __init__.py
│   ├── ucs.py               # Uniform Cost Search       [علیرضا]
│   ├── astar.py             # A* Search                 [علیرضا]
│   ├── genetic.py           # Genetic Algorithm         [رضا]
│   └── idastar.py           # IDA* Search               [رضا]
├── utils/
│   ├── __init__.py
│   └── heuristics.py        # manhattan(pos, goal)
├── maps/                    # نقشه‌های نمونه
│   ├── scenario1_sample.txt
│   ├── scenario2_sample.txt
│   ├── scenario3_sample.txt
│   └── scenario4_sample.txt
└── report/                  # گزارش پروژه
    └── report.pdf
```

---

## فازبندی پروژه

### فاز ۰ — زیرساخت مشترک `[هر دو نفر]` ✅

> **هدف:** پایه‌گذاری ساختار مشترک که هر دو الگوریتم‌نویس روی آن تکیه می‌کنند.

**وظایف:**
- [x] طراحی فرمت فایل نقشه (ورودی استاندارد)
- [x] پیاده‌سازی `MapGrid` — خواندن ماتریس، تشخیص نوع خانه، محاسبه هزینه ورود
- [x] پیاده‌سازی `Node` — نگه‌داری وضعیت، هزینه `g(n)`، والد، و اکشن
- [x] تعریف قرارداد `State` برای هر سناریو (tuple ساده، مدیریت داخل هر الگوریتم):
  - سناریو ۱: `(row, col)`
  - سناریو ۲: `(row, col)` یا `(row, col, T % 30)` اگر نقشه منطقه Z داشته باشد
  - سناریو ۴: `(row, col, current_bridge_chain_id)`
- [x] پیاده‌سازی `main.py` با دریافت آرگومان `--scenario` و `--map` از کاربر

**جزئیات پیاده‌سازی:**

`models/map_grid.py` — کلاس `MapGrid`:
- `from_file(path)` / `from_string(text)` — بارگذاری نقشه
- `entry_cost(r, c, T, current_bridge_chain)` — هزینه ورود به خانه با در نظر گرفتن Z و پل
- `neighbors(r, c)` — لیست `(action, nr, nc)` برای چهار جهت (بدون STAY)
- `find_starts()` / `find_goals()` — یافتن موقعیت `S`/`G` یا `Si`/`Gi`
- `has_zones()` / `has_bridges()` — تشخیص نوع سناریو
- `bridge_chain_id(r, c)` — شناسه زنجیره پل (BFS روی خانه‌های هم‌k مجاور)

`models/node.py` — کلاس `Node`:
- فیلدهای `state`, `g`, `parent`, `action`
- `path()` — بازسازی لیست گره‌ها از ریشه تا گره جاری
- `actions()` — لیست اکشن‌های مسیر
- `__lt__` برای پشتیبانی مستقیم از `heapq`

`utils/heuristics.py` — تابع `manhattan(pos, goal)`:
- هیوریستیک Manhattan Distance — پذیرفتنی (Admissible)

`algorithms/ucs.py` — پیاده‌سازی شده ✅ (فاز ۱)

`algorithms/astar.py`, `genetic.py`, `idastar.py` — placeholder آماده

`maps/scenario1..4_sample.txt` — نقشه‌های نمونه برای هر سناریو

**نکات مهم برای الگوریتم‌نویسان:**
- State در IDA* باید `(row, col, current_bridge_chain_id)` باشد — `current_bridge_chain_id` همان chain_id خانه‌ای است که الان روی آن هستیم (نه خانه بعدی)
- State در نقشه‌های دارای Z باید `(row, col, T % 30)` باشد — `map.has_zones()` این را مشخص می‌کند
- STAY را الگوریتم‌ها خودشان اضافه می‌کنند (در `neighbors` نیست)

**فایل‌های مربوطه:** `models/map_grid.py`, `models/node.py`, `utils/heuristics.py`, `main.py`, `maps/`

---

### فاز ۱ — Uniform Cost Search `[علیرضا نصیری]` ✅

> **هدف:** یافتن مسیر بهینه بدون اطلاعات پیشین، فقط با هزینه واقعی.

**وظایف:**
- [x] پیاده‌سازی priority queue با `heapq` (بدون کتابخانه آماده)
- [x] مدیریت `visited` برای جلوگیری از حلقه
- [x] اعمال قوانین خانه Z (چرخه ۳۰ دقیقه‌ای، هزینه ۱ یا ۱۵)
- [x] اعمال قانون STAY (هزینه ۱ دقیقه)
- [x] بازگشت مسیر با بازسازی زنجیره والدها
- [x] شمارش `Expanded Nodes`

**جزئیات پیاده‌سازی:**
- State: `(row, col)` اگر نقشه Z نداشته باشد، `(row, col, T % 30)` اگر داشته باشد
- `T = node.g` — چون تمام هزینه‌ها بر حسب دقیقه‌اند، g دقیقاً برابر زمان سپری‌شده است
- heap entries: `(cost, counter, node)` — counter از مقایسه مستقیم آبجکت‌های Node جلوگیری می‌کند
- STAY فقط وقتی `has_zones()` صادق است تولید می‌شود؛ بدون Z هرگز در مسیر بهینه نیست

**نتایج تست:**

| نقشه | Cost | Actions | Expanded Nodes |
|------|------|---------|----------------|
| `scenario1_sample.txt` (۳×۳) | 4 min | `RIGHT, RIGHT, DOWN, DOWN` | 5 |
| `scenario2_sample.txt` (۲×۴ با Z) | 4 min | `RIGHT, DOWN, RIGHT, RIGHT` | 14 |

**خروجی نمونه:**
```
Cost: 4 min
Actions: ['RIGHT', 'RIGHT', 'DOWN', 'DOWN']
Expanded nodes: 5
```

**فایل:** `algorithms/ucs.py`

---

### فاز ۲ — A* Search `[رضا پیردیر]` ✅

> **هدف:** بهبود سرعت UCS با اضافه کردن تابع هیوریستیک.

**وظایف:**
- [x] باز استفاده از ساختار UCS + اضافه کردن `f(n) = g(n) + h(n)`
- [x] پیاده‌سازی هیوریستیک Manhattan Distance:
  `h(n) = |x1 - x2| + |y1 - y2|`
- [x] اثبات Admissible بودن هیوریستیک (در گزارش)
- [x] مقایسه `Expanded Nodes` بین UCS و A* روی نقشه‌های یکسان

**بخش اختیاری (نمره اضافه):**
- [ ] هیوریستیک پیشرفته‌تر از Manhattan (مثلاً در نظر گرفتن خانه‌های Z)

**جزئیات پیاده‌سازی:**
- `f(n) = g(n) + h(n)` — heap روی f مرتب می‌شود (نه فقط g مثل UCS)
- هیوریستیک `h(n) = manhattan(pos, goal)` — **Admissible:** چون کمینه هزینه ورود هر خانه ۱ است و Manhattan حداقل تعداد حرکت را می‌شمارد؛ **Consistent:** چون یک حرکت Manhattan را حداکثر ۱ کاهش می‌دهد و هزینه حرکت ≥ ۱ است
- State و منطق STAY با UCS یکسان است

**مقایسه Expanded Nodes با UCS:**

| نقشه | UCS | A* | کاهش |
|------|-----|----|-------|
| `scenario1_sample.txt` (۳×۳، بدون Z) | 5 | 5 | — |
| `scenario2_sample.txt` (۲×۴ با Z) | 14 | 5 | ۶۴٪ کمتر |

**خروجی نمونه:**
```
Cost: 4 min
Actions: ['RIGHT', 'DOWN', 'RIGHT', 'RIGHT']
Expanded nodes: 5
```

**فایل‌ها:** `algorithms/astar.py`, `utils/heuristics.py`

---

### فاز ۳ — Genetic Algorithm `[رضا پیردیر]`

> **هدف:** تخصیص بهینه اهداف بین چند عامل برای کمینه کردن Makespan.

**وظایف:**
- [ ] تعریف کروموزوم (نمایش تخصیص اهداف به عاملها + ترتیب بازدید)
- [ ] پیاده‌سازی تابع Fitness:
  `Fitness = -Makespan = -max(T1, T2, ..., Tk)`
  (هزینه مسیر با فاصله منهتن محاسبه می‌شود)
- [ ] پیاده‌سازی عملگر Crossover (ترکیب دو کروموزوم)
- [ ] پیاده‌سازی عملگر Mutation (جهش تصادفی)
- [ ] انتخاب (Selection) — مثلاً Tournament Selection
- [ ] تعیین پارامترها: اندازه جمعیت، نرخ جهش، تعداد نسل
- [ ] چاپ بهترین تخصیص در پایان

**خروجی مورد انتظار:**
```
Best makespan (minutes): X.XX
  S1 at (r, c) assigned targets: ['G1'] -> coords: [(r, c)]
  S2 at (r, c) assigned targets: ['G2'] -> coords: [(r, c)]
```

**فایل:** `algorithms/genetic.py`

---

### فاز ۴ — IDA* `[علیرضا نصیری]`

> **هدف:** مسیریابی بهینه با حافظه محدود در نقشه‌ای با پل‌ها.

**وظایف:**
- [ ] پیاده‌سازی IDA* با depth-first iterative deepening روی `f(n)`
- [ ] مدیریت `State` با وضعیت پل: `(x, y, on_bridge_id)`
- [ ] اعمال قوانین پل:
  - ورود به اولین خانه پل: هزینه `k`
  - حرکت روی خانه‌های همان زنجیره: هزینه `0`
  - خروج و ورود مجدد: پرداخت مجدد `k`
- [ ] جلوگیری از حلقه در مسیر جاری (نه visited سراسری)
- [ ] شمارش `Expanded Nodes`

**مثال پل `B4`:** ورود اول هزینه ۴، حرکت بعدی روی همان پل هزینه ۰

**فایل:** `algorithms/idastar.py`

---

### فاز ۵ — تست و مستندسازی `[هر دو نفر]`

> **هدف:** اطمینان از صحت پیاده‌سازی و آماده‌سازی گزارش.

**وظایف:**
- [ ] تست تمام ۴ سناریو با مثال‌های داده‌شده در PDF
- [ ] ساخت حداقل ۲ نقشه جدید برای هر سناریو
- [ ] مقایسه `Expanded Nodes` بین UCS و A* در گزارش
- [ ] نوشتن گزارش ۳ تا ۵ صفحه‌ای شامل:
  - توضیح ساختار داده‌ها
  - طراحی الگوریتم ژنتیک
  - تحلیل نتایج و مقایسه الگوریتم‌ها

**بخش اختیاری:**
- [ ] نمایش گرافیکی مسیر روی نقشه (با `matplotlib` یا ASCII)

---

## نحوه اجرا

```bash
# نصب پیش‌نیازها (اختیاری)
pip install -r requirements.txt

# سناریو ۱: UCS
python main.py --scenario 1 --map maps/scenario1_sample.txt

# سناریو ۲: A*
python main.py --scenario 2 --map maps/scenario2_sample.txt

# سناریو ۳: Genetic Algorithm
python main.py --scenario 3 --map maps/scenario3_sample.txt

# سناریو ۴: IDA*
python main.py --scenario 4 --map maps/scenario4_sample.txt
```

---

## فرمت فایل نقشه

```
M N          ← تعداد سطر و ستون
...          ← محتوای نقشه (فاصله‌گذاری با space)
```

**مثال سناریو ۱:**
```
3 3
S 1 1
9 8 1
9 9 G
```

**مثال سناریو ۴ (پل):**
```
3 4
S 9 9 9
B4 B4 B4 1
9 9 9 G
```

---

## قوانین محیط

- **شروع:** عامل از `S` در زمان `T=0` حرکت می‌کند
- **حرکات:** RIGHT, LEFT, UP, DOWN, STAY (هزینه STAY = ۱)
- **هزینه ورود به S و G:** همیشه ۱ دقیقه
- **خانه Z:** اگر `T mod 30 < 15` هزینه ۱، در غیر این صورت ۱۵ دقیقه
- **State با Z:** `(x, y, T mod 30)` برای جلوگیری از حلقه بی‌نهایت
- **پل Bk:** ورود اول هزینه `k`، ادامه روی همان پل هزینه ۰

---

## مقایسه الگوریتم‌ها

| الگوریتم | Completeness | Optimality | حافظه | سرعت |
|----------|-------------|-----------|-------|-------|
| UCS | ✅ | ✅ | O(b^d) | کند |
| A* | ✅ | ✅ | O(b^d) | سریع‌تر |
| IDA* | ✅ | ✅ | O(d) | متوسط |
| Genetic | ❌ (احتمالی) | ❌ (تقریبی) | کم | سریع |

---

## نکات مهم پیاده‌سازی

1. استفاده از کتابخانه‌های آماده برای **الگوریتم‌های اصلی** مجاز نیست
2. از `heapq` برای priority queue استفاده کنید (این یک ساختار داده است، نه الگوریتم جستجو)
3. در سناریو ژنتیک، فاصله بین نقاط با **Manhattan Distance** محاسبه می‌شود (نه اجرای واقعی UCS)
4. در IDA*، visited سراسری نداریم — فقط مسیر جاری چک می‌شود
