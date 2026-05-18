import pandas as pd
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

if __name__ == "__main__":
    print("📦 Шаг 1: Загрузка базы данных...")
    try:
        df = pd.read_csv('dataset_full.csv')
        print(f"✅ База загружена! Строк: {df.shape[0]}, Признаков: {df.shape[1] - 1}")
    except FileNotFoundError:
        print("❌ Ошибка: Файл 'dataset_full.csv' не найден!")
        exit()

    X = df.drop(columns=['phishing']).values
    y = df['phishing'].values

    print("📊 Шаг 2: Настройка нормализации...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    dataset_means = scaler.mean_
    joblib.dump(dataset_means, 'dataset_means.pkl')
    print("💾 Средние значения сохранены.")

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🧠 Шаг 3: Обучение модели...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32), 
        max_iter=500, 
        activation='relu',
        solver='adam',
        early_stopping=True,
        validation_fraction=0.1,
        random_state=42,
        verbose=True
    )
    
    mlp.fit(X_train, y_train)
    
    print("\n🎯 Шаг 4: Проверка точности...")
    y_pred = mlp.predict(X_test)
    accuracy = mlp.score(X_test, y_test) * 100
    print(f"🥇 Точность модели: {accuracy:.2f}%")

    print("💾 Шаг 5: Сохранение файлов...")
    joblib.dump(mlp, 'micro_net.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("✅ Все файлы сохранены и готовы к работе.")