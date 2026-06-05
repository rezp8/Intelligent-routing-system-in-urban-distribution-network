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
│   ├── ucs.py               # Uniform Cost Search   ✅  [علیرضا]
│   ├── astar.py             # A* Search             ✅  [رضا]
│   ├── genetic.py           # Genetic Algorithm     ✅  [رضا]
│   └── idastar.py           # IDA* Search           ✅  [علیرضا]
├── utils/
│   ├── __init__.py
│   ├── heuristics.py        # manhattan(pos, goal)
│   └── visualize.py         # render_path() — ASCII مسیر روی نقشه
├── maps/
│   ├── scenario1_sample.txt
│   ├── scenario1_test1.txt  # ۴×۴ کریدور
│   ├── scenario1_test2.txt  # ۵×۵ زیگزاگ
│   ├── scenario2_sample.txt
│   ├── scenario2_test1.txt  # ۳×۵ با Z
│   ├── scenario2_test2.txt  # ۴×۵ با Z پراکنده
│   ├── scenario3_sample.txt
│   ├── scenario3_test1.txt  # ۵×۵، ۳ عامل
│   ├── scenario3_test2.txt  # ۴×۵، ۲ عامل ۴ هدف
│   ├── scenario4_sample.txt
│   ├── scenario4_test1.txt  # ۳×۵، B2×4
│   └── scenario4_test2.txt  # ۴×۶، B3×5
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

`algorithms/astar.py` — پیاده‌سازی شده ✅ (فاز ۲)

`algorithms/genetic.py` — پیاده‌سازی شده ✅ (فاز ۳)

`algorithms/idastar.py` — پیاده‌سازی شده ✅ (فاز ۴)

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

### فاز ۳ — Genetic Algorithm `[رضا پیردیر]` ✅

> **هدف:** تخصیص بهینه اهداف بین چند عامل برای کمینه کردن Makespan.

**وظایف:**
- [x] تعریف کروموزوم (نمایش تخصیص اهداف به عاملها + ترتیب بازدید)
- [x] پیاده‌سازی تابع Fitness:
  `Makespan = max(T1, T2, ..., Tk)` — هزینه هر مسیر با Manhattan Distance
- [x] پیاده‌سازی عملگر Crossover (OX1 — Order Crossover)
- [x] پیاده‌سازی عملگر Mutation (جابجایی تصادفی دو موقعیت)
- [x] انتخاب با Tournament Selection
- [x] تعیین پارامترها: جمعیت ۱۵۰، نرخ جهش ۱۵٪، ۴۰۰ نسل، elitism

**جزئیات پیاده‌سازی:**

**نمایش کروموزوم — route-with-separators:**
کروموزوم یک permutation با طول `num_goals + num_agents - 1` است.
عناصر `0..m-1` ایندکس اهداف هستند؛ عناصر `m..` توکن جداکننده بین عامل‌ها.
```
مثال (2 عامل، 2 هدف): [0, SEP, 1]  →  S1:[G1]  S2:[G2]  makespan=3 ✓
```
این نمایش OX crossover استاندارد را مستقیماً ممکن می‌کند.

**عملگرها:**
- `_ox_crossover(p1, p2)` — یک بازه تصادفی از p1 نگه می‌دارد، بقیه را از p2 به ترتیب پر می‌کند
- `_mutate(chrom, rate)` — با احتمال `rate` دو موقعیت تصادفی را عوض می‌کند
- `_tournament(pop, scores, k=3)` — کمترین makespan را از k نامزد تصادفی انتخاب می‌کند

**نتایج تست:**

| نقشه | Makespan | تخصیص |
|------|----------|--------|
| `scenario3_sample.txt` (۲ عامل، ۲ هدف) | 3 min | S1→G1, S2→G2 |
| نقشه ۳ عامل ۴ هدف | 4 min | S1→G1, S2→G2, S3→[G3,G4] |

**خروجی نمونه:**
```
Best makespan (minutes): 3.00
  S1 at (0, 0) assigned targets: ['G1'] -> coords: [(0, 3)]
  S2 at (2, 0) assigned targets: ['G2'] -> coords: [(2, 2)]
```

**فایل:** `algorithms/genetic.py`

---

### فاز ۴ — IDA* `[علیرضا نصیری]` ✅

> **هدف:** مسیریابی بهینه با حافظه محدود در نقشه‌ای با پل‌ها.

**وظایف:**
- [x] پیاده‌سازی IDA* با depth-first iterative deepening روی `f(n)`
- [x] مدیریت `State` با وضعیت پل: `(row, col, bridge_chain_id)`
- [x] اعمال قوانین پل:
  - ورود به اولین خانه پل: هزینه `k`
  - حرکت روی خانه‌های همان زنجیره: هزینه `0`
  - خروج و ورود مجدد: پرداخت مجدد `k`
- [x] جلوگیری از حلقه در مسیر جاری (نه visited سراسری)
- [x] شمارش `Expanded Nodes`

**جزئیات پیاده‌سازی:**
- **هیوریستیک: `h = 0`** — Manhattan در نقشه‌های پل‌دار Admissible نیست؛ یک زنجیره Bk به طول L هزینه k دارد اما Manhattan می‌گوید L. اگر k < L آنگاه Manhattan هزینه واقعی را بیشتر از واقع برآورد می‌کند. h=0 همیشه admissible است و بهینگی را تضمین می‌کند.
- **آستانه اولیه `threshold = 0`**، هر تکرار آستانه را به کمترین `f` که از آستانه قبل تجاوز کرد افزایش می‌دهد
- **جلوگیری از حلقه:** مجموعه `on_path` شامل state‌های مسیر DFS جاری — نه visited سراسری؛ یک state ممکن است از مسیر دیگری با هزینه کمتر قابل دسترس باشد
- **State** شامل `bridge_chain_id` است تا ورود به زنجیره جدید از ورود مجدد به همان زنجیره تفکیک شود

**نتایج تست:**

| نقشه | Cost | Actions | Expanded |
|------|------|---------|----------|
| `scenario4_sample.txt` (۳×۴، B4) | 6 min | `DOWN, RIGHT, RIGHT, RIGHT, DOWN` | 6 |
| نقشه ۵×۴ با دو زنجیره B2 و B3 | 14 min | از B2 عبور، سپس مستقیم به G | 23 |
| تست re-entry (دو زنجیره B2 جدا) | 6 min | جریمه ورود مجدد k=2 اعمال شد ✅ | — |

**خروجی نمونه:**
```
Cost: 6 min
Actions: ['DOWN', 'RIGHT', 'RIGHT', 'RIGHT', 'DOWN']
Expanded nodes: 6
```

**فایل:** `algorithms/idastar.py`

---

### فاز ۵ — تست و مستندسازی `[هر دو نفر]` ✅

> **هدف:** اطمینان از صحت پیاده‌سازی و آماده‌سازی گزارش.

**وظایف:**
- [x] تست تمام ۴ سناریو با نقشه‌های نمونه
- [x] ساخت ۲ نقشه جدید برای هر سناریو (۸ نقشه جدید)
- [x] مقایسه `Expanded Nodes` بین UCS و A*
- [x] نمایش ASCII مسیر روی نقشه (`--visualize`)
- [ ] نوشتن گزارش ۳ تا ۵ صفحه‌ای شامل توضیح ساختار داده‌ها، طراحی الگوریتم ژنتیک، تحلیل نتایج

---

#### نقشه‌های جدید

| فایل | سناریو | اندازه | توضیح |
|------|--------|--------|-------|
| `scenario1_test1.txt` | ۱ — UCS | ۴×۴ | کریدور ارزان در میان خانه‌های ۹ |
| `scenario1_test2.txt` | ۱ — UCS | ۵×۵ | کریدور زیگزاگ |
| `scenario2_test1.txt` | ۲ — A* | ۳×۵ | مسیر بهینه از میان سلول‌های Z |
| `scenario2_test2.txt` | ۲ — A* | ۴×۵ | سلول‌های Z پراکنده |
| `scenario3_test1.txt` | ۳ — ژنتیک | ۵×۵ | ۳ عامل، ۳ هدف |
| `scenario3_test2.txt` | ۳ — ژنتیک | ۴×۵ | ۲ عامل، ۴ هدف |
| `scenario4_test1.txt` | ۴ — IDA* | ۳×۵ | پل B2 مستقیم به هدف |
| `scenario4_test2.txt` | ۴ — IDA* | ۴×۶ | پل B3 بلند |

---

#### نتایج کامل — سناریو ۱ و ۲ (UCS در برابر A*)

| نقشه | Cost | UCS Expanded | A* Expanded | کاهش |
|------|------|-------------|------------|-------|
| `scenario1_sample` (۳×۳) | 4 | 5 | 5 | — |
| `scenario1_test1` (۴×۴) | 6 | 7 | 7 | — |
| `scenario1_test2` (۵×۵) | 8 | 9 | 9 | — |
| `scenario2_sample` (۲×۴ + Z) | 4 | 14 | 5 | ۶۴٪ |
| `scenario2_test1` (۳×۵ + Z) | 4 | 14 | 5 | ۶۴٪ |
| `scenario2_test2` (۴×۵ + Z) | 7 | 38 | 9 | ۷۶٪ |

> **نتیجه:** در نقشه‌های بدون Z، UCS و A* تعداد یکسانی گره expand می‌کنند زیرا هزینه‌های بالا (۹) مانع طبیعی هستند. در نقشه‌های با Z، فضای حالت به `(r, c, T%30)` گسترش می‌یابد و هیوریستیک A* تا ۷۶٪ کمتر گره بررسی می‌کند.

---

#### نتایج — سناریو ۳ (ژنتیک)

| نقشه | تعداد عامل | تعداد هدف | Makespan | تخصیص |
|------|-----------|----------|---------|--------|
| `scenario3_sample` (۴×۴) | 2 | 2 | 3 min | S1→G1, S2→G2 |
| `scenario3_test1` (۵×۵) | 3 | 3 | 4 min | S1→G1, S2→G2, S3→G3 |
| `scenario3_test2` (۴×۵) | 2 | 4 | 3 min | S1→[G1,G2], S2→[G3,G4] |

---

#### نتایج — سناریو ۴ (IDA*)

| نقشه | پل | Cost | Expanded | مسیر |
|------|----|------|---------|------|
| `scenario4_sample` (۳×۴) | B4×3 | 6 | 6 | DOWN, RIGHT×3, DOWN |
| `scenario4_test1` (۳×۵) | B2×4 | 3 | 6 | DOWN, RIGHT×4 |
| `scenario4_test2` (۴×۶) | B3×5 | 14 | 19 | DOWN, RIGHT×5, DOWN×2 |

---

#### نمایش ASCII مسیر (`--visualize`)

```bash
python main.py --scenario 1 --map maps/scenario1_test1.txt --visualize
```

```
Cost: 6 min
Actions: ['RIGHT', 'DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'DOWN']
Expanded nodes: 7

---------------
[S] [>]  9   9
 9  [v]  9   9
 9  [v] [>] [>]
 9   9   9  [G]
---------------
```

`S` = شروع، `G` = هدف، `^v<>` = جهت حرکت در هر خانه

**فایل:** `utils/visualize.py` | اجرا: `python main.py ... --visualize`

---

## نحوه اجرا

```bash
# سناریو ۱: UCS
python main.py --scenario 1 --map maps/scenario1_sample.txt

# سناریو ۲: A*
python main.py --scenario 2 --map maps/scenario2_sample.txt

# سناریو ۳: Genetic Algorithm
python main.py --scenario 3 --map maps/scenario3_sample.txt

# سناریو ۴: IDA*
python main.py --scenario 4 --map maps/scenario4_sample.txt

# نمایش ASCII مسیر روی نقشه (سناریوهای ۱، ۲، ۴)
python main.py --scenario 1 --map maps/scenario1_test1.txt --visualize
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
