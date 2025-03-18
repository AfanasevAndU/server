import pandas as pd
from yandex_reviews_parser.utils import YandexParser
import datetime
from transformers import pipeline
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate
from database.db import SessionLocal, init_db
from sqlalchemy.orm import Session

sentiment_analysis = pipeline(model="seara/rubert-tiny2-russian-sentiment")

MO_dict = {
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №1"': 1049351641,
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №12"': [237065765948, 
                                            67616710886, 
                                            1065019307, 
                                            170493432728, 
                                            147681494274, 
                                            51519571897],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №13"': 236936151183,   
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №17"': [77642995869,
                                            1103995801,
                                            1007361457,
                                            1035163629,
                                            53692016486,
                                            1043579562,
                                            60809839700,
                                            57398544357,
                                            63061101972,
                                            94416711235],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №3"': [1004953025,
                                           1112134186,
                                           1126922227,
                                           61472787665,
                                           1002898179],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №4"': [1050695386,
                                           1007209444,
                                           1046824521],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №5"': [8637277890,
                                           1098505996,
                                           1177435252,
                                           1109586042,
                                           1113910320,
                                           61987139261,
                                           219171503362,
                                           1032744405,
                                           181600311637,
                                           1043467648],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №6"': [61897158289,
                                           1083284572,
                                           1052565338,
                                           191077907774],
    'ГАУЗ ТО "ГОРОДСКАЯ ПОЛИКЛИНИКА №8"': [113453550699,
                                           1081507501,
                                           1092118867,
                                           170236505408],
    'ГАУЗ ТО "МКДЦ"': 51657435717,
    'ГАУЗ ТО "ОБЛАСТНАЯ БОЛЬНИЦА №19"': 1028114223,
    'ГБУЗ ТО "ОБЛАСТНАЯ ИНФЕКЦИОННАЯ КЛИНИЧЕСКАЯ БОЛЬНИЦА"': 1036161788,
    'ГБУЗ ТО "ОБЛАСТНОЙ КЛИНИЧЕСКИЙ ФТИЗИОПУЛЬМОНОЛОГИЧЕСКИЙ ЦЕНТР"': 1123699365,
    'ГБУЗ ТО "ОКБ № 1"': [1007784444,
                         1102410722],
    'ГБУЗ ТО "ОКБ № 2"': 1032874916,
    'ГБУЗ ТО "ОКПБ"': 1347552416,
    'ГБУЗ ТО "ПЕРИНАТАЛЬНЫЙ ЦЕНТР"': 1046824521,
    'ГБУЗ ТО "РОДДОМ №2"': 1042728375,
    'ГБУЗ ТО "РОДДОМ №3"': 1014658894,
}

def analyze_sentiment(text):
    """Анализ тональности текста"""
    result = sentiment_analysis(text, truncation=True, padding=True)
    sentiment_label = result[0]['label']

    if sentiment_label == "neutral":
        return 'Нейтральный'
    elif sentiment_label == "positive":
        return 'Положительный'
    elif sentiment_label == "negative":
        return 'Отрицательный'
    return 'Неопределено'

def process_reviews():
    """Основная функция для сбора и сохранения отзывов в CSV"""
    all_reviews = []

    for company_name, ids in MO_dict.items():
        if not isinstance(ids, list):
            ids = [ids]  # Преобразуем одиночный ID в список

        for id_ya in ids:
            parser = YandexParser(id_ya)
            all_data = parser.parse()

            if not all_data or "company_reviews" not in all_data:
                print(f"Отзывы не найдены для {company_name} (ID: {id_ya})")
                continue

            reviews = all_data.get("company_reviews", [])
            if not reviews:
                print(f"Нет отзывов для {company_name} (ID: {id_ya})")
                continue

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
            df['Тональность'] = df['Комментарий'].apply(analyze_sentiment)
            all_reviews.append(df)

    if all_reviews:
        full_df = pd.concat(all_reviews, ignore_index=True)
        full_df.to_csv("all_reviews.csv", index=False)  
        print("Все отзывы успешно сохранены в all_reviews.csv")
    else:
        print("Нет данных для сохранения.")

process_reviews()