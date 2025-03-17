import pandas as pd
from yandex_reviews_parser.utils import YandexParser
import datetime
from transformers import pipeline
from models import Feedback
from schemas import FeedbackCreate
from database import SessionLocal, init_db
from sqlalchemy.orm import Session

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

        def analyze_sentiment(text):
            result = sentiment_analysis(text, truncation=True, padding=True)
            
            print(f"Текст: {text}")
            print(f"Результат модели: {result}")
            
            if isinstance(result[0]['label'], int):
                sentiment_label = result[0]['label']
            else:
                sentiment_label = result[0]['label']

            if sentiment_label == "neutral":  
                return 'Нейтральный'
            elif sentiment_label == "positive":  
                return 'Положительный'
            elif sentiment_label == "negative":  
                return 'Отрицательный'
            else:
                return 'Неопределено'

        df['Тональность'] = df['Комментарий'].apply(analyze_sentiment)

        print(df)

        df.to_csv("reviewBERT2.csv", index=False)


        init_db()

        def get_db():
            db = SessionLocal
            try:
                yield db
            finally:
                db.close()

        def save_reviews_to_db(reviews, db: Session):
            for _, row in reviews.iterrows():
                review_data = FeedbackCreate(
                    company=row["Компания"],
                    author=row["Автор"],
                    date=datetime.datetime.strptime(row["Дата"], '%Y-%m-%d %H:%M:%S'),
                    rating=row["Оценка"],
                    comment=row["Комментарий"],
                    sentiment=row["Тональность"]
                )
                db_review = Feedback(**review_data.dict())
                db.add(db_review)
            db.commit()

        # Получение сессии и сохранение данных
        db = next(get_db())
        save_reviews_to_db(df, db)
        print("Данные успешно загружены в базу данных.")
        

        
