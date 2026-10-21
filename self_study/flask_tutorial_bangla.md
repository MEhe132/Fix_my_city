# ফ্লাস্ক (Flask) শেখার সম্পূর্ণ গাইড

ফ্লাস্ক (Flask) হলো পাইথনের একটি অত্যন্ত জনপ্রিয় এবং হালকা (micro) ওয়েব ফ্রেমওয়ার্ক। এটি ব্যবহার করে খুব সহজেই ওয়েব অ্যাপ্লিকেশন তৈরি করা যায়। নিচে ফ্লাস্ক শেখার এবং একটি সম্পূর্ণ প্রজেক্ট তৈরি করার ধাপে ধাপে গাইড দেওয়া হলো:

## ধাপ ১: প্রজেক্ট ফোল্ডার এবং ভার্চুয়াল এনভায়রনমেন্ট তৈরি করা
যেকোনো পাইথন প্রজেক্ট করার সময় ভার্চুয়াল এনভায়রনমেন্ট (Virtual Environment) ব্যবহার করা ভালো, যাতে প্রজেক্টের প্যাকেজগুলো অন্য প্রজেক্টের সাথে মিলে না যায়।

১. টার্মিনাল বা কমান্ড প্রম্পট খুলুন এবং আপনার প্রজেক্টের ফোল্ডারে যান।
২. নিচের কমান্ডটি দিয়ে ভার্চুয়াল এনভায়রনমেন্ট তৈরি করুন:
   ```bash
   python -m venv venv
   ```
৩. এবার ভার্চুয়াল এনভায়রনমেন্টটি চালু (Activate) করুন:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

## ধাপ ২: ফ্লাস্ক ইনস্টল করা
ভার্চুয়াল এনভায়রনমেন্ট চালু থাকা অবস্থায় ফ্লাস্ক ইনস্টল করুন:
```bash
pip install Flask
```

## ধাপ ৩: প্রথম ফ্লাস্ক অ্যাপ তৈরি করা (Hello World)
প্রজেক্ট ফোল্ডারে `app.py` নামে একটি ফাইল তৈরি করুন এবং নিচের কোডগুলো লিখুন:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "হ্যালো ওয়ার্ল্ড! ফ্লাস্কে স্বাগতম।"

if __name__ == '__main__':
    app.run(debug=True)
```

**কোড রান করা:**
টার্মিনালে লিখুন: `python app.py`
এরপর ব্রাউজারে গিয়ে `http://127.0.0.0:5000` ঠিকানায় গেলে আপনার মেসেজটি দেখতে পাবেন।

## ধাপ ৪: রাউটিং (Routing)
রাউটিং মানে হলো ইউআরএল (URL) এর উপর ভিত্তি করে বিভিন্ন পেজ দেখানো।

```python
@app.route('/about')
def about():
    return "এটি আমাদের সম্পর্কে পেজ।"

@app.route('/user/<name>')
def user(name):
    return f"হ্যালো, {name}!"
```

## ধাপ ৫: এইচটিএমএল টেমপ্লেট (HTML Templates) ব্যবহার করা
ফ্লাস্কে সরাসরি এইচটিএমএল লেখার বদলে আমরা আলাদা এইচটিএমএল ফাইল ব্যবহার করতে পারি। এর জন্য `templates` নামে একটি ফোল্ডার তৈরি করতে হবে।

`app.py` ফাইলে পরিবর্তন:
```python
from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')
```

`templates/index.html` ফাইলে:
```html
<!DOCTYPE html>
<html>
<head>
    <title>আমার ফ্লাস্ক অ্যাপ</title>
</head>
<body>
    <h1>ফ্লাস্কে স্বাগতম!</h1>
    <p>এটি একটি এইচটিএমএল টেমপ্লেট।</p>
</body>
</html>
```

## ধাপ ৬: স্ট্যাটিক ফাইল (CSS, JavaScript, Images) যোগ করা
সিএসএস (CSS) বা ছবি রাখার জন্য `static` নামে একটি ফোল্ডার তৈরি করতে হবে।

ধরা যাক, `static/style.css` নামে একটি ফাইল আছে। এটি এইচটিএমএল এ যুক্ত করতে:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

## ধাপ ৭: ফর্ম থেকে ডেটা নেওয়া (GET এবং POST Request)
ইউজারের কাছ থেকে ডেটা নেওয়ার জন্য ফর্ম ব্যবহার করা হয়।

```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        return f"লগইন সফল হয়েছে, {username}!"
    
    return render_template('login.html')
```

## ধাপ ৮: ডেটাবেস যুক্ত করা (Flask-SQLAlchemy)
ফ্লাস্কের সাথে ডেটাবেস ব্যবহার করার জন্য `Flask-SQLAlchemy` খুব জনপ্রিয়।

ইনস্টল করুন: `pip install Flask-SQLAlchemy`

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"
```

## একটি সম্পূর্ণ প্রজেক্টের স্ট্রাকচার:
```text
my_flask_app/
│
├── app.py                # মূল পাইথন ফাইল
├── requirements.txt      # প্রজেক্টের সকল প্যাকেজের তালিকা
│
├── templates/            # HTML ফাইলগুলো এখানে থাকবে
│   ├── index.html
│   └── layout.html
│
└── static/               # CSS, JS, এবং ছবিগুলো এখানে থাকবে
    ├── style.css
    └── script.js
```

এই ধাপগুলো অনুসরণ করে আপনি সহজেই ফ্লাস্কে একটি সম্পূর্ণ ওয়েব অ্যাপ্লিকেশন তৈরি করতে পারবেন। শুভকামনা!
