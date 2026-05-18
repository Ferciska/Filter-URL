import io
import cv2
import uvicorn
import numpy as np
import onnxruntime as ort
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title="SafeView ONNX AI Service")

ONNX_MODEL_PATH = "nsfw_model.onnx"

print("⏳ Загрузка фильтра картинок...")
try:
    ort_session = ort.InferenceSession(ONNX_MODEL_PATH)
    input_name = ort_session.get_inputs()[0].name
    print(f"🚀 Фильтр запущен! Входной слой: {input_name}")
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")
    print("Проверь, лежит ли файл nsfw_model.onnx в текущей папке.")
    exit()

def preprocess_image(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Не удалось прочитать картинку")
        
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
    img_normalized = img_resized.astype(np.float32) / 255.0
    img_expanded = np.expand_dims(img_normalized, axis=0)
    return img_expanded

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        blob = preprocess_image(contents)
        
        raw_prediction = ort_session.run(None, {input_name: blob})
        probabilities = raw_prediction[0][0]
        
        drawings_prob = float(probabilities[0]) * 100
        hentai_prob = float(probabilities[1]) * 100
        neutral_prob = float(probabilities[2]) * 100
        porn_prob = float(probabilities[3]) * 100
        sexy_prob = float(probabilities[4]) * 100
        
        hard_nsfw = hentai_prob + porn_prob + sexy_prob
        
        if hard_nsfw > 10.0:
            is_safe = False
            nsfw_probability = hard_nsfw
        elif neutral_prob < 45.0:
            is_safe = False
            nsfw_probability = 100.0 - neutral_prob
        else:
            is_safe = True
            nsfw_probability = hard_nsfw
            
        classes_map = {
            "drawings": round(drawings_prob, 2),
            "hentai": round(hentai_prob, 2),
            "neutral": round(neutral_prob, 2),
            "porn": round(porn_prob, 2),
            "sexy": round(sexy_prob, 2)
        }
        
        return JSONResponse({
            "status": "success",
            "nsfw_probability": round(nsfw_probability, 2),
            "verdict": "SAFE" if is_safe else "NSFW_BLOCKED",
            "analysis": classes_map
        })
        
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)