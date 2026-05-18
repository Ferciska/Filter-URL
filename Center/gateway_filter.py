import joblib
import numpy as np
import re
import os
from urllib.parse import urlparse
from mitmproxy import http

# =====================================================================
# 1. ЗАГРУЗКА МОЗГОВ СИСТЕМЫ И НАСТРОЙКИ ОБХОДА
# =====================================================================
try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
    dataset_means = joblib.load('dataset_means.pkl')
    print("🚀 [AI GATEWAY] Модель машинного обучения успешно внедрена в прокси!")
except FileNotFoundError:
    print("❌ [AI GATEWAY] Ошибка: Не найдены файлы модели в текущей папке!")
    exit()

# Глобальный белый список доменов (чтобы не ломать системный софт и доверенные ресурсы)
WHITELIST_DOMAINS = {
    "google.com", "googleapis.com", "gstatic.com", "googleads.g.doubleclick.net", "googlevideo.com", "youtube.com",
    "yandex.kz", "yandex.net", "ya.ru", "yastatic.net",
    "microsoft.com", "windows.com", "azurefd.net", "bing.com", "msn.com", "live.com", "office.com", "msedge.net",
    "github.com", "jsdelivr.net", "kaspersky.com"
}

# Безопасные расширения (статические файлы не могут быть фишинговыми веб-страницами)
SAFE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
    '.css', '.js', '.woff', '.woff2', '.ttf', '.mp4', '.webm'
}


# =====================================================================
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И СКОРИНГ
# =====================================================================
def extract_advanced_features(url):
    """Экстрактор фич (8 активных + маска средних значений)"""
    features = dataset_means.copy()
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0] 
        
    features[0] = len(url)                    # length_url
    features[1] = url.count('.')              # qty_dot_url
    features[2] = url.count('-')              # qty_hyphen_url
    features[3] = url.count('/')              # qty_slash_url
    
    features[18] = len(domain)                # domain_length
    features[19] = domain.count('.')          # qty_dot_domain
    features[20] = domain.count('-')          # qty_hyphen_domain
    
    features[104] = 1 if url.startswith("https") else 0
    return features


def is_whitelisted(url, domain):
    """Проверка: находится ли ресурс в списке исключений"""
    # 1. Проверка по жестким ключевым словам (твоя старая логика)
    if "update" in url or "windowsupdate" in url or "msedge" in url:
        return True

    # 2. Проверка по базе доверенных доменов и их поддоменов
    for trusted_domain in WHITELIST_DOMAINS:
        if domain == trusted_domain or domain.endswith("." + trusted_domain):
            return True

    # 3. Проверка на безопасный статический контент (картинки, шрифты, стили)
    try:
        path = urlparse(url).path.lower()
        if any(path.endswith(ext) for ext in SAFE_EXTENSIONS):
            return True
    except Exception:
        pass

    return False


# =====================================================================
# 3. ПЕРЕХВАТ ТРАФИКА (ОСНОВНОЙ ЦИКЛ MITMPROXY)
# =====================================================================
def request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    
    # Вытаскиваем чистый домен для эвристики и проверок
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0].lower()

    # --- ЭТАП 1: ЭВРИСТИЧЕСКИЙ ФИЛЬТР (Сырые IP) ---
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        # Если это внешний сырой IP - рубим сразу, минуя ИИ
        if not domain.startswith("192.168.") and not domain.startswith("10.") and not domain.startswith("127."):
            block_request(flow, url, method="Эвристика (Сырой IP)", prob=100.0)
            return

    # --- ЭТАП 2: ФИЛЬТР ИСКЛЮЧЕНИЙ (Белый список) ---
    if is_whitelisted(url, domain):
        # Пропускаем без спама в консоль и без дерганья ML-модели
        return

# --- ЭТАП 3: НЕЙРОСЕТЕВОЙ АНАЛИЗ ---
    raw_features = extract_advanced_features(url)
    features_reshaped = raw_features.reshape(1, -1)
    features_scaled = scaler.transform(features_reshaped)
    
    # Считаем вероятность фишинга
    probability = model.predict_proba(features_scaled)[0][1] * 100

    # НАСТРОЙКА УРОВНЕЙ РЕАГИРОВАНИЯ (Максимальная защита: бан от 55%)
    # >= 55.0% -> Жесткая блокировка
    # от 40.0% до 55.0% -> Подозрительно (Пропускаем, но логируем)
    if probability >= 55.0:
        block_request(flow, url, method="Нейросеть (ML-Детект)", prob=probability)
    elif probability >= 40.0:
        print(f"🟡 [ПОДОЗРИТЕЛЬНО] {url[:60]}... | Угроза: {probability:.2f}% (Пропущено)")
    else:
        print(f"🟢 [ПРОПУЩЕН] {url[:60]}... | Угроза: {probability:.2f}%")


# =====================================================================
# 4. ГЕНЕРАЦИЯ СТРАНИЦЫ БЛОКИРОВКИ
# =====================================================================
def block_request(flow, url, method, prob):
    """Функция генерации страницы блокировки для нарушителя"""
    print(f"🛑 [БЛОКИРОВКА] [{method}] Ссылка: {url[:70]}... | Степень угрозы: {prob:.2f}%")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Система безопасности школы</title>
        <style>
            body {{ background-color: #1a1a1a; color: #ffffff; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 10%; }}
            .card {{ background: #2d2d2d; border-radius: 8px; padding: 40px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 600px; }}
            h1 {{ color: #ff4d4d; font-size: 48px; margin-bottom: 10px; }}
            .url-box {{ background: #111; padding: 15px; border-radius: 4px; font-family: monospace; word-break: break-all; color: #ff9999; margin: 20px 0; }}
            .info {{ color: #aaaaaa; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>ДОСТУП ОГРАНИЧЕН</h1>
            <p>Внимание! Наша гибридная ИИ-система безопасности заблокировала переход.</p>
            <div class="url-box">{url}</div>
            <p><strong>Метод обнаружения:</strong> {method}<br>
            <strong>Вероятность фишинга:</strong> {prob:.2f}%</p>
            <p class="info">Запрос заблокирован на уровне интернет-шлюза школы.</p>
        </div>
    </body>
    </html>
    """
    
    flow.response = http.Response.make(
        403, 
        html_content.encode('utf-8'), 
        {"Content-Type": "text/html; charset=utf-8"}
    )