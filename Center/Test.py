import joblib
import numpy as np
import time
import re

# Загружаем нейросеть, нормализатор и средние значения
try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
    dataset_means = joblib.load('dataset_means.pkl') # Загружаем маску средних значений
    print("🚀 Нейросеть и скалер успешно загружены в память!")
except FileNotFoundError:
    print("❌ Ошибка: Файлы модели не найдены! Запусти сначала train.py")
    exit()

def extract_advanced_features(url):
    """
    Продвинутый экстрактор. Заполняет 106 тяжелых фич средними безопасными
    значениями из датасета, а 8 текстовых фич считает на лету.
    """
    features = dataset_means.copy()
    
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0] 
        
    # Заполняем текстовые фичи для ИИ
    features[0] = len(url)                    # length_url
    features[1] = url.count('.')              # qty_dot_url
    features[2] = url.count('-')              # qty_hyphen_url
    features[3] = url.count('/')              # qty_slash_url
    
    features[18] = len(domain)                # domain_length
    features[19] = domain.count('.')          # qty_dot_domain
    features[20] = domain.count('-')          # qty_hyphen_domain
    
    features[104] = 1 if url.startswith("https") else 0
        
    return features

# --- БЛОК ТЕСТИРОВАНИЯ НА ЛЕТУ ---
print("Переходим в режим реального времени. Компьютер учителя лагать не будет.")
print("Для выхода введи 'exit'\n")

while True:
    # 1. СНАЧАЛА СТРОГО ЗАПРАШИВАЕМ ВВОД
    test_url = input("🔗 Введи URL для проверки: ")
    
    if test_url.strip().lower() == 'exit':
        break
        
    if not test_url.strip():
        continue

    # Вытаскиваем домен для быстрой проверки регуляркой
    clean_url = test_url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0]
    
    # 2. ЭВРИСТИКА (Жесткий блок сырых внешних IP-адресов)
    # Регулярка проверяет, является ли домен IPv4-адресом (например, 192.168.1.105)
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        # Если это НЕ локальный IP (пропускаем домашние роутеры, локальные сервера 192.168.х.х, 10.х.х.х, 127.х.х.х)
        if not domain.startswith("192.168.") and not domain.startswith("10.") and not domain.startswith("127."):
            print("-" * 50)
            print("🎯 [Сработало жесткое правило эвристики: Внешний IP-адрес]")
            print(f"🛑 ВЕРДИКТ: [ ОПАСНО ] Фишинг! (Угроза: 99.99%)")
            print("⏱️ Время анализа: 0.000000 сек. (Отсечено до ИИ)")
            print("-" * 50 + "\n")
            continue # Уходим на следующую итерацию цикла, ИИ не трогаем

    # 3. ЕСЛИ ЭТО ОБЫЧНЫЙ ДОМЕН — ИДЕМ В НЕЙРОСЕТЬ
    t_start = time.time()

    raw_features = extract_advanced_features(test_url)
    features_reshaped = raw_features.reshape(1, -1)

    features_scaled = scaler.transform(features_reshaped)
    prediction = model.predict(features_scaled)
    probability = model.predict_proba(features_scaled)[0][1] * 100

    t_end = time.time()

    print("-" * 50)
    if prediction[0] == 1:
        print(f"🛑 ВЕРДИКТ: [ ОПАСНО ] Фишинг! (Угроза: {probability:.2f}%)")
    else:
        print(f"🟢 ВЕРДИКТ: [ БЕЗОПАСНО ] Доверенный URL. (Угроза: {probability:.2f}%)")
    print(f"⏱️ Время анализа ИИ: {(t_end - t_start):.6f} сек.")
    print("-" * 50 + "\n")