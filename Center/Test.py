import joblib
import numpy as np
import time
import re

try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
    dataset_means = joblib.load('dataset_means.pkl')
    print("🚀 Модель успешно загружена!")
except FileNotFoundError:
    print("❌ Ошибка: Файлы модели не найдены!")
    exit()


def extract_advanced_features(url):
    features = dataset_means.copy()
    
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0] 
        
    features[0] = len(url)                    
    features[1] = url.count('.')              
    features[2] = url.count('-')              
    features[3] = url.count('/')              
    
    features[18] = len(domain)                
    features[19] = domain.count('.')          
    features[20] = domain.count('-')          
    
    features[104] = 1 if url.startswith("https") else 0
        
    return features


print("Вход в режим проверки ссылок.")
print("Для выхода введи 'exit'\n")

while True:
    test_url = input("🔗 Введи URL для проверки: ")
    
    if test_url.strip().lower() == 'exit':
        break
        
    if not test_url.strip():
        continue

    clean_url = test_url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0]
    
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        if not domain.startswith("192.168.") and not domain.startswith("10.") and not domain.startswith("127."):
            print("-" * 50)
            print("🎯 [Сработало правило: Прямой IP адрес]")
            print(f"🛑 ВЕРДИКТ: [ ОПАСНО ] (Угроза: 99.99%)")
            print("⏱️ Время проверки: 0.000000 сек.")
            print("-" * 50 + "\n")
            continue

    t_start = time.time()

    raw_features = extract_advanced_features(test_url)
    features_reshaped = raw_features.reshape(1, -1)

    features_scaled = scaler.transform(features_reshaped)
    prediction = model.predict(features_scaled)
    probability = model.predict_proba(features_scaled)[0][1] * 100

    t_end = time.time()

    print("-" * 50)
    if prediction[0] == 1:
        print(f"🛑 ВЕРДИКТ: [ ОПАСНО ] (Угроза: {probability:.2f}%)")
    else:
        print(f"🟢 ВЕРДИКТ: [ БЕЗОПАСНО ] (Угроза: {probability:.2f}%)")
    print(f"⏱️ Время проверки: {(t_end - t_start):.6f} сек.")
    print("-" * 50 + "\n")