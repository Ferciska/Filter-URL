# C:\Users\Atomoid\Desktop\Center\run_project.py
import subprocess
import os
import sys

def main():
    print("============================================================")
    print("🛡️  ЗАПУСК ИИ-ШЛЮЗА БЕЗОПАСНОСТИ (School AI Gateway) ")
    print("============================================================")

    # Определяем рабочую директорию (папку Center)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("⏳ Инициализация mitmproxy и загрузка модели micro_net.pkl...")
    print("👉 Настройте прокси в браузере или системе на: 127.0.0.1:8080")
    print("Для остановки комплекса нажмите Ctrl+C\n" + "-"*60)

    # Запускаем твой скрипт напрямую через mitmdump
    # Опция --set term_log_verbosity=error уберет системный спам mitmproxy,
    # чтобы ты видел только свои красивые принты 🟢, 🟡 и 🛑
    cmd = ["mitmdump", "-p", "8080", "-s", "gateway_filter.py", "--set", "term_log_verbosity=error"]

    try:
        # Запуск процесса. stdout=None позволит принтам лететь прямо в твою консоль без задержек
        process = subprocess.Popen(cmd, cwd=base_dir)
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 [AI GATEWAY] Работа шлюза остановлена пользователем.")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске: {e}")

if __name__ == "__main__":
    main()