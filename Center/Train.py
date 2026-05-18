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

    X = df.drop(columns=['phishing']).values
    y = df['phishing'].values

    print("📊 Шаг 2: Масштабирование признаков...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # РЕШЕНИЕ ПРОБЛЕМЫ: Сохраняем средние значения фич из датасета
    dataset_means = scaler.mean_
    joblib.dump(dataset_means, 'dataset_means.pkl')
    print("💾 Средние значения фич сохранены в 'dataset_means.pkl'")

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🧠 Шаг 3: Конфигурация и обучение продвинутой нейросети...")
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
    
    print("\n🎯 Шаг 4: Оценка качества модели...")
    y_pred = mlp.predict(X_test)
    accuracy = mlp.score(X_test, y_test) * 100
    print(f"🥇 Финальная точность модели на неизвестных данных: {accuracy:.2f}%")

    print("💾 Шаг 5: Сохранение компонентов...")
    joblib.dump(mlp, 'micro_net.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("✅ Все файлы успешно обновлены и готовы к работе.")