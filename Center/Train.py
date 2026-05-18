import pandas as pd
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

if __name__ == "__main__":
    print("📦 Шаг 1: Загрузка локального датасета (111 признаков)...")
    try:
        df = pd.read_csv('dataset_full.csv')
        print(f"✅ Датасет успешно загружен! Строк: {df.shape[0]}, Фич: {df.shape[1] - 1}")
    except FileNotFoundError:
        print("❌ Ошибка: Помести файл 'dataset_full.csv' в одну папку с этим скриптом!")
        exit()

    # Разделяем фичи (X) и целевую метку фишинга (y)
    X = df.drop(columns=['phishing']).values
    y = df['phishing'].values

    print("📊 Шаг 2: Масштабирование признаков...")
    # Нейросети требуют, чтобы все числа были в одном масштабе (от -1 до 1 или от 0 до 1)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Разделяем на обучающую (80%) и тестовую (20%) выборки с сохранением баланса классов
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🧠 Шаг 3: Конфигурация и обучение продвинутой нейросети...")
    # Делаем сеть глубокой: два скрытых слоя из 64 и 32 нейронов.
    # Добавляем early_stopping, чтобы сеть не переобучалась (не зазубривала базу)
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32), 
        max_iter=500, 
        activation='relu',
        solver='adam',
        early_stopping=True,
        validation_fraction=0.1,
        random_state=42,
        verbose=True # Покажет процесс снижения ошибки на каждой эпохе
    )
    
    mlp.fit(X_train, y_train)
    
    print("\n🎯 Шаг 4: Оценка качества модели...")
    y_pred = mlp.predict(X_test)
    accuracy = mlp.score(X_test, y_test) * 100
    print(f"🥇 Финальная точность модели на неизвестных данных: {accuracy:.2f}%")
    print("\n📋 Детальный отчет:")
    print(classification_report(y_test, y_pred, target_names=['Легитимный (0)', 'Фишинг (1)']))

    print("💾 Шаг 5: Сохранение компонентов...")
    # Для работы test.py нам критически важно сохранить и модель, и скалер!
    joblib.dump(mlp, 'micro_net.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("✅ Файлы 'micro_net.pkl' и 'scaler.pkl' успешно обновлены.")