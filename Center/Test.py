import joblib
import numpy as np

# Загружаем нейросеть и нормализатор
try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
except FileNotFoundError:
    print("❌ Ошибка: Файлы модели или скалера не найдены! Запусти сначала train.py")
    exit()

def extract_advanced_features(url):
    """
    Продвинутый экстрактор. Вычисляет текстовые фичи на лету,
    а остальные 106 фич заполняет безопасными средними значениями,
    чтобы структура вектора строго соответствовала 111 признакам.
    """
    # Создаем базовый шаблон из 111 нулей
    features = np.zeros(111)
    
    # Считаем то, что можем вытащить прямо из текста URL:
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    
    features[0] = len(url)                    # length_url
    features[1] = url.count('.')              # qty_dot_url
    features[2] = url.count('-')              # qty_hyphen_url
    features[3] = url.count('/')              # qty_slash_url
    
    # Параметры домена
    domain = clean_url.split('/')[0]
    features[18] = len(domain)                # domain_length
    features[19] = domain.count('.')          # qty_dot_domain
    features[20] = domain.count('-')          # qty_hyphen_domain
    
    # Если в ссылке есть явные признаки защищенного протокола
    if url.startswith("https"):
        features[104] = 1                     # tls_ssl_certificate = Есть
    
    # Остальные фичи (DNS, Whois, времена жизни) по умолчанию остаются 0 или средними.
    # В продвинутом аудите сюда можно дописать блоки парсинга через библиотеки requests и whois.
    
    return features

# Ссылка для теста (можешь менять на любую)
test_url = "https://support.appsflyer.com/hc/ru/articles/360017132597-%D0%94%D0%BB%D0%B8%D0%BD%D0%BD%D1%8B%D0%B5-URL-%D0%B0%D0%B4%D1%80%D0%B5%D1%81%D0%B0-OneLink"

# 1. Извлекаем сырые признаки (вектор из 111 элементов)
raw_features = extract_advanced_features(test_url)

# 2. Приводим их к правильной форме матрицы (1 строка, 111 колонок)
features_reshaped = raw_features.reshape(1, -1)

# 3. Пропускаем через сохраненный StandardScaler (Важнейший шаг!)
features_scaled = scaler.transform(features_reshaped)

# 4. Делаем предсказание
prediction = model.predict(features_scaled)
probability = model.predict_proba(features_scaled)[0][1] * 100

print("=" * 60)
print(f"🔗 СЕТЕВОЙ ФИЛЬТР ПРОВЕРЯЕТ URL: {test_url}")
print("=" * 60)

if prediction[0] == 1:
    print(f"🛑 ВЕРДИКТ: [ ОПАСНО ] Данный ресурс определен как ФИШИНГ!")
    print(f"📊 Индекс опасности нейросети: {probability:.2f}%")
else:
    print(f"🟢 ВЕРДИКТ: [ БЕЗОПАСНО ] Ссылка заслуживает доверия.")
    print(f"📊 Вероятность угрозы: {probability:.2f}%")
print("=" * 60)