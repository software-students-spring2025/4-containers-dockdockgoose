FROM python:3.10

WORKDIR /app

# Install OS dependencies early
RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

# Pre-copy only requirements first to cache pip install
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Now copy the rest of your source code
COPY . .
COPY face_model.h5 ./

CMD ["python", "app.py"]