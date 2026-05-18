from http.server import SimpleHTTPRequestHandler, HTTPServer

class BlockerStubHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # HTML-код страницы, которую увидит пользователь
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ДОСТУП ЗАБЛОКИРОВАН</title>
            <style>
                body { background-color: #1a1a1a; color: #ff4d4d; font-family: Arial, sans-serif; text-align: center; padding-top: 100px; }
                .container { border: 2px solid #ff4d4d; display: inline-block; padding: 40px; border-radius: 10px; background-color: #262626; }
                h1 { font-size: 48px; margin-bottom: 10px; }
                p { color: #cccccc; font-size: 18px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛑 ОПАСНОСТЬ!</h1>
                <h2>Доступ заблокирован центральной нейросетью</h2>
                <p>Система защиты обнаружила, что данная ссылка ведет на фишинговый или вредоносный сайт.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    # Запускаем заглушку на порту 8080 главного компа
    server = HTTPServer(('0.0.0.0', 8080), BlockerStubHandler)
    print("🖥️ Сервер-заглушка запущен на порту 8080... Ожидание заблокированных пользователей.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")