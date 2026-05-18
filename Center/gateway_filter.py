import joblib
import numpy as np
import re
import os
import requests
from urllib.parse import urlparse
from mitmproxy import http

try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
    dataset_means = joblib.load('dataset_means.pkl')
    print("🚀 Фильтр ссылок запущен!")
except FileNotFoundError:
    print("❌ Ошибка: Не найдены файлы модели!")
    exit()

WHITELIST_DOMAINS = {
    "google.com", "googleapis.com", "gstatic.com", "googleads.g.doubleclick.net", "googlevideo.com", "youtube.com",
    "yandex.kz", "yandex.net", "ya.ru", "yastatic.net",
    "microsoft.com", "windows.com", "azurefd.net", "bing.com", "msn.com", "live.com", "office.com", "msedge.net",
    "github.com", "jsdelivr.net", "kaspersky.com"
}

SAFE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
    '.css', '.js', '.woff', '.woff2', '.ttf', '.mp4', '.webm'
}

AI_SERVER_URL = "http://127.0.0.1:8001/analyze"


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


def is_whitelisted(url, domain):
    if "update" in url or "windowsupdate" in url or "msedge" in url:
        return True

    for trusted_domain in WHITELIST_DOMAINS:
        if domain == trusted_domain or domain.endswith("." + trusted_domain):
            return True

    try:
        path = urlparse(url).path.lower()
        if any(path.endswith(ext) for ext in SAFE_EXTENSIONS):
            return True
    except Exception:
        pass

    return False


def request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    domain = clean_url.split('/')[0].split(':')[0].lower()

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        if not domain.startswith("192.168.") and not domain.startswith("10.") and not domain.startswith("127."):
            block_request(flow, url, method="Сырой IP адрес", prob=100.0)
            return

    if is_whitelisted(url, domain):
        return

    raw_features = extract_advanced_features(url)
    features_reshaped = raw_features.reshape(1, -1)
    features_scaled = scaler.transform(features_reshaped)
    
    probability = model.predict_proba(features_scaled)[0][1] * 100

    if probability >= 55.0:
        block_request(flow, url, method="Проверка ссылки", prob=probability)
    elif probability >= 40.0:
        print(f"🟡 [Подозрительно] {url[:60]}... | Опасность: {probability:.2f}%")
    else:
        print(f"🟢 [Разрешено] {url[:60]}... | Опасность: {probability:.2f}%")


def response(flow: http.HTTPFlow) -> None:
    if not flow.response or flow.response.status_code != 200:
        return

    content_type = flow.response.headers.get("Content-Type", "").lower()
    if "image/" in content_type:
        url = flow.request.pretty_url
        
        clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
        domain = clean_url.split('/')[0].split(':')[0].lower()
        if is_whitelisted(url, domain) and not (url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png')):
            return

        try:
            image_bytes = flow.response.content
            if not image_bytes:
                return

            files = {"file": ("intercepted.jpg", image_bytes, content_type)}
            res = requests.post(AI_SERVER_URL, files=files, timeout=1.5)
            
            if res.status_code == 200:
                result = res.json()
                
                if result.get("verdict") == "NSFW_BLOCKED":
                    print(f"🛑 [Блок картинки] URL: {url[:70]}... | Вероятность: {result.get('nsfw_probability')}%")
                    
                    transparent_1x1_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
                    
                    flow.response.content = transparent_1x1_png
                    flow.response.headers["Content-Type"] = "image/png"
                    
        except Exception as e:
            print(f"⚠️ [Ошибка проверки картинки]: {e}")


def block_request(flow, url, method, prob):
    print(f"🛑 [Блокировка сайта] [{method}] Ссылка: {url[:70]}... | Опасность: {prob:.2f}%")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Система безопасности</title>
        <style>
            body {{ background-color: #1a1a1a; color: #ffffff; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 10%; }}
            .card {{ background: #2d2d2d; border-radius: 8px; padding: 40px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.5); max-width: 600px; }}
            <h1>ДОСТУП ОГРАНИЧЕН</h1>
            .url-box {{ background: #111; padding: 15px; border-radius: 4px; font-family: monospace; word-break: break-all; color: #ff9999; margin: 20px 0; }}
            .info {{ color: #aaaaaa; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>ДОСТУП ОГРАНИЧЕН</h1>
            <p>Внимание! Система безопасности заблокировала переход.</p>
            <div class="url-box">{url}</div>
            <p><strong>Способ обружения:</strong> {method}<br>
            <strong>Вероятность угрозы:</strong> {prob:.2f}%</p>
            <p class="info">Запрос заблокирован фильтром безопасности.</p>
        </div>
    </body>
    </html>
    """
    
    flow.response = http.Response.make(
        403, 
        html_content.encode('utf-8'), 
        {"Content-Type": "text/html; charset=utf-8"}
    )