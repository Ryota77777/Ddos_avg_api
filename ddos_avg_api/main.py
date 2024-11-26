from fastapi import FastAPI, File, UploadFile, HTTPException
from database import create_tables, get_connection
import csv
from io import StringIO
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Создаем таблицы при запуске
create_tables()

@app.post("/upload/")
async def upload_csv(file: UploadFile = File(...)):
    # Логируем запрос
    print(f"Received file: {file.filename}, content_type: {file.content_type}")

    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file format, expected CSV.")

    # Читаем и декодируем файл
    content = await file.read()
    decoded = content.decode("utf-8")
    csv_reader = csv.DictReader(StringIO(decoded), delimiter=",")

    with get_connection() as conn:
        for row in csv_reader:
            saddr = row["saddr"]
            dur = float(row["dur"])

            # Проверяем, существует ли запись
            existing = conn.execute("SELECT total_dur, count FROM ddos_data WHERE saddr = ?", (saddr,)).fetchone()
            if existing:
                total_dur, count = existing
                conn.execute(
                    "UPDATE ddos_data SET total_dur = ?, count = ? WHERE saddr = ?",
                    (total_dur + dur, count + 1, saddr)
                )
            else:
                conn.execute(
                    "INSERT INTO ddos_data (saddr, total_dur, count) VALUES (?, ?, ?)",
                    (saddr, dur, 1)
                )

        # Извлекаем обновленные данные для ответа
        results = conn.execute("SELECT saddr, total_dur, count FROM ddos_data").fetchall()

    # Формируем JSON-ответ
    response = [
        {"saddr": row["saddr"], "avgDur": row["total_dur"] / row["count"]}
        for row in results
    ]

    return jsonable_encoder(response)


