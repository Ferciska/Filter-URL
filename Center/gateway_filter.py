import joblib
import numpy as np
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import requests

# 1. Загружаем твой продвинутый мозг и скалер
try:
    model = joblib.load('micro_net.pkl')
    scaler = joblib.load('scaler.pkl')
    print("🧠 Нейросеть успешно подключена к шлюзу трафика!")
except FileNotFoundError:
    print("❌ Ошибка: Файлы 'micro_net.pkl' или 'scaler.pkl' не найдены в этой папке!")
    exit()

# IP-адрес главного компьютера в локальной сети, где запущена заглушка stub.py
STUB_SERVER_URL = "http://127.0.0.1:8080" 

# БЕЛЫЙ СПИСОК: Системные домены, фоновый спам от которых мы НЕ выводим в консоль
# БЕЛЫЙ СПИСОК: Сюда добавляем всё, что генерирует фоновый шум (Android, Windows, iOS)
SYSTEM_WHITELIST = [
    "connectivitycheck.gstatic.com",  # Google / Android
    "play.googleapis.com",            # Google Play
    "www.google.com/gen_204",         # Google фоновый тест
    "generate_204",                   # Общий паттерн для Android
    "msftconnecttest.com",            # Windows тест сети (IPv4 и IPv6)
    "msftncsi.com"                    # Старый тип проверки Windows NCSI
]

def check_url_with_ai(url):
    """ Наша продвинутая функция извлечения текстовых фич """
    features = np.zeros(111)
    clean_url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    
    features[0] = len(url)
    features[1] = url.count('.')
    features[2] = url.count('-')
    features[3] = url.count('/')
    
    domain = clean_url.split('/')[0]
    features[18] = len(domain)
    features[19] = domain.count('.')
    features[20] = domain.count('-')
    
    if url.startswith("https"):
        features[104] = 1
        
    features_reshaped = features.reshape(1, -1)
    features_scaled = scaler.transform(features_reshaped)
    
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1] * 100
    return prediction, probability


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    """ Обработчик прокси-запросов, проходящих через главный комп """
    
    def log_message(self, format, *args):
        """ 🔇 ПЕРЕОПРЕДЕЛЕНИЕ: Полностью глушим стандартный текстовый спам Python в консоли """
        pass

    def do_GET(self):
        url = self.path
        
        # 1. Игнорируем запросы к нашей же заглушке, чтобы не зациклиться
        if "8080" in url or "127.0.0.1" in url:
            self.proxy_forward(url)
            return

        # 2. Проверяем, есть ли URL в белом списке системного трафика
        if any(domain in url for domain in SYSTEM_WHITELIST):
            # Пропускаем его абсолютно молча, не нагружая консоль и нейросеть
            self.proxy_forward(url)
            return

        # 3. А вот оригинальные запросы пользователя выводим и анализируем!
        print(f"🔍 Шлюз перехватил запрос: {url}")
        
        # Проверяем нейросетью
        is_phishing, prob = check_url_with_ai(url)
        
        if is_phishing == 1 and prob > 75.0: # Порог срабатывания 75%
            print(f"🛑 КРИТИЧЕСКИЙ СИГНАЛ: Фишинг обнаружен ({prob:.2f}%)! Блокируем: {url}")
            # Перенаправляем на страницу-затычку
            self.send_response(302)
            self.send_header('Location', STUB_SERVER_URL)
            self.end_headers()
        else:
            print(f"🟢 Ссылка чистая ({prob:.2f}% угрозы). Пропускаем.")
            self.proxy_forward(url)

    def proxy_forward(self, url):
        """ Пересылка легитимного запроса дальше в интернет """
        try:
            headers = {key: self.headers[key] for key in self.headers}
            response = requests.get(url, headers=headers, stream=True, timeout=5)
            
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ['transfer-encoding', 'content-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            
            self.wfile.write(response.content)
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

if __name__ == "__main__":
    server = ThreadingHTTPServer(('0.0.0.0', 8888), ProxyHTTPRequestHandler)
    print("🚀 Центральный ИИ-фильтр трафика запущен на порту 8888...")
    print("Ожидаю трафик со всей сети через DHCP шлюз...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nШлюз остановлен.")