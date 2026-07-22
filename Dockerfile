# सबसे हल्की और तेज़ Python इमेज
FROM python:3.10-slim

# Working directory
WORKDIR /app

# पहले सिर्फ requirements कॉपी करो – ताकि Docker cache काम करे (build तेज़)
COPY requirements.txt .

# Dependencies install करो – verbose हटाओ, cache clean करो, ताकि image छोटी हो
RUN pip install --no-cache-dir -r requirements.txt

# बाकी सारी files कॉपी करो (bot.py, bomber.py, आदि)
COPY . .

# (Optional) अगर bomber.py नहीं मिली तो कोई दिक्कत नहीं – bot.py में error handle है

# Bot चलाने का command
CMD ["python3", "bot.py"]
