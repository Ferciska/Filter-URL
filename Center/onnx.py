import os
import tensorflow as tf
import tf2onnx

# Укажи точный путь к файлу модели из SafeView
h5_model_path = "mobilenetv3_nsfw_model_finetuned_best.h5"
output_onnx_path = "nsfw_model.onnx"

print("⏳ Загружаем Keras модель...")
model = tf.keras.models.load_model(h5_model_path)

print("⚡ Конвертируем в формат ONNX...")
# Указываем входной профиль для корректной сборки графа
spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)

model_proto, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=spec, 
    output_path=output_onnx_path
)

if os.path.exists(output_onnx_path):
    print(f"🎉 Готово! Модель сохранена как: {output_onnx_path}")
else:
    print("❌ Что-то пошло не так, файл не создался.")