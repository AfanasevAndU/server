import pandas as pd
from yandex_reviews_parser.utils import YandexParser
import datetime
from transformers import pipeline
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate
from database.db import SessionLocal, init_db
from sqlalchemy.orm import Session

# Загрузка модели для анализа тональности
sentiment_analysis = pipeline(model="seara/rubert-tiny2-russian-sentiment")

id_ya = 236936151183  # ID Компании Yandex карты
parser = YandexParser(id_ya)

all_data = parser.parse()  

if not all_data or "company_reviews" not in all_data:
    print("Отзывы не найдены")
else:
    company_info = all_data.get("company_info", {})
    company_name = company_info.get("name", "Неизвестная компания")
    reviews = all_data.get("company_reviews", [])
    
    if not reviews:
        print("Нет отзывов для обработки.")
    else:
        # Форматирование отзывов
        formatted_reviews = []
        for review in reviews:
            formatted_reviews.append({
                "Компания": company_name,
                "Автор": review.get("name", "Аноним"),
                "Дата": datetime.datetime.fromtimestamp(review.get("date", 0)).strftime('%Y-%m-%d %H:%M:%S'),
                "Оценка": review.get("stars", "Нет оценки"),
                "Комментарий": review.get("text", "Нет комментария")
            })

        df = pd.DataFrame(formatted_reviews)

        # Функция для анализа тональности
        def analyze_sentiment(text):
            result = sentiment_analysis(text, truncation=True, padding=True)
            
            print(f"Текст: {text}")
            print(f"Результат модели: {result}")
            
            sentiment_label = result[0]['label']

            if sentiment_label == "neutral":  
                return 'Нейтральный'
            elif sentiment_label == "positive":  
                return 'Положительный'
            elif sentiment_label == "negative":  
                return 'Отрицательный'
            else:
                return 'Неопределено'

        # Добавление столбца с тональностью
        df['Тональность'] = df['Комментарий'].apply(analyze_sentiment)

        print(df)

        # Сохранение данных в CSV
        df.to_csv("reviewBERT2.csv", index=False)

        # Инициализация базы данных
        init_db()

        # Генератор для получения сессии базы данных
        def get_db():
            db = SessionLocal()  # Здесь создаем сессию через SessionLocal
            try:
                yield db
            finally:
                db.close()  # Закрытие сессии после выполнения всех операций

        # Функция для сохранения отзывов в БД
        def save_reviews_to_db(reviews, db: Session):
            for _, row in reviews.iterrows():
                review_data = FeedbackCreate(
                    company=row["Компания"],
                    author=row["Автор"],
                    date=datetime.datetime.strptime(row["Дата"], '%Y-%m-%d %H:%M:%S'),
                    text=row["Комментарий"],
                    rate=row["Тональность"]
                )
                # Используем model_dump() для сериализации данных в Pydantic V2
                db_review = Feedback(**review_data.model_dump())  
                db.add(db_review)  # Добавление отзыва в сессию
            db.commit()  # Подтверждение изменений в базе данных

        # Получение сессии и сохранение данных в БД
        db = next(get_db())
        save_reviews_to_db(df, db)
        print("Данные успешно загружены в базу данных.")
