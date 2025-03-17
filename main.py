import pandas as pd
from yandex_reviews_parser.utils import YandexParser
import datetime
from transformers import pipeline

# Используем нужную модель
sentiment_analysis = pipeline(model="seara/rubert-tiny2-russian-sentiment")

id_ya = 236936151183  # ID Компании Yandex карты
parser = YandexParser(id_ya)

# Парсим данные с Yandex
all_data = parser.parse()  

# Проверяем, что отзывы были найдены
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

        # Создаем DataFrame из отформатированных данных
        df = pd.DataFrame(formatted_reviews)

        # Функция для анализа тональности текста
        def analyze_sentiment(text):
            result = sentiment_analysis(text, truncation=True, padding=True)
            
            # Печатаем результат, чтобы посмотреть, что возвращает модель
            print(f"Текст: {text}")
            print(f"Результат модели: {result}")
            
            # Если результат вернулся в числовом формате
            if isinstance(result[0]['label'], int):
                sentiment_label = result[0]['label']
            else:
                sentiment_label = result[0]['label']

            # Маппинг меток модели в понятные категории
            if sentiment_label == "neutral":  # Нейтральный
                return 'Нейтральный'
            elif sentiment_label == "positive":  # Положительный
                return 'Положительный'
            elif sentiment_label == "negative":  # Отрицательный
                return 'Отрицательный'
            else:
                return 'Неопределено'

        # Применяем функцию для получения тональности
        df['Тональность'] = df['Комментарий'].apply(analyze_sentiment)

        # Выводим результат
        print(df)

        # Сохраняем результат в CSV файл
        df.to_csv("reviewBERT2.csv", index=False)
