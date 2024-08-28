from sqlalchemy.orm import Session
from sqlalchemy import func, subquery, case, desc
from app.models.models import Analysis, Metric, Model, Image
from collections import Counter

class ReportService:
    @staticmethod
    def generate_report(db: Session):
        # Subconsulta para contar la frecuencia de emociones y géneros por fecha y modelo
        subquery = db.query(
            func.date_trunc('day', Analysis.analysis_time).label('date'),
            Model.name.label('model'),
            Metric.metric_name,
            Metric.value,
            func.count(Metric.value).label('value_count')
        ).join(Model, Model.model_id == Analysis.model_id)\
         .join(Metric, Metric.analysis_id == Analysis.analysis_id)\
         .filter(Metric.metric_name.in_(['dominant_emotion', 'gender']))\
         .group_by('date', 'model', Metric.metric_name, Metric.value)\
         .subquery()

        # Consulta principal para seleccionar la emoción y el género más repetidos por fecha y modelo
        emotion_query = db.query(
            subquery.c.date,
            subquery.c.model,
            subquery.c.value.label('most_repeated_emotion')
        ).filter(subquery.c.metric_name == 'dominant_emotion')\
         .order_by(subquery.c.date, subquery.c.model, desc(subquery.c.value_count))\
         .distinct(subquery.c.date, subquery.c.model).subquery()

        gender_query = db.query(
            subquery.c.date,
            subquery.c.model,
            subquery.c.value.label('most_repeated_gender')
        ).filter(subquery.c.metric_name == 'gender')\
         .order_by(subquery.c.date, subquery.c.model, desc(subquery.c.value_count))\
         .distinct(subquery.c.date, subquery.c.model).subquery()

        # Combinar las subconsultas para obtener el resumen final
        summary_query = db.query(
            subquery.c.date,
            subquery.c.model,
            func.sum(subquery.c.value_count).label('total_analysis'),
            emotion_query.c.most_repeated_emotion,
            gender_query.c.most_repeated_gender
        ).join(emotion_query, (subquery.c.date == emotion_query.c.date) & (subquery.c.model == emotion_query.c.model))\
         .join(gender_query, (subquery.c.date == gender_query.c.date) & (subquery.c.model == gender_query.c.model))\
         .group_by(subquery.c.date, subquery.c.model, emotion_query.c.most_repeated_emotion, gender_query.c.most_repeated_gender)\
         .all()

        # Preparar los datos para la tabla de resumen
        summary_table = []
        for row in summary_query:
            summary_table.append({
                'date': row.date.strftime('%Y-%m-%d'),
                'model': row.model,
                'total_analysis': row.total_analysis,
                'most_repeated_emotion': row.most_repeated_emotion,
                'most_repeated_gender': row.most_repeated_gender
            })

        return summary_table

    @staticmethod
    def generate_detailed_report(db: Session):
        detailed_data = db.query(
            Analysis.analysis_time.label('date'),
            Image.file_path.label('image'),
            Model.name.label('model'),
            func.max(case([(Metric.metric_name == 'age_range_high', Metric.value)])).label('age'),
            func.max(case([(Metric.metric_name == 'gender', Metric.value)])).label('gender'),
            func.max(case([(Metric.metric_name == 'dominant_emotion', Metric.value)])).label('emotion')
        ).join(Model, Model.model_id == Analysis.model_id)\
         .join(Metric, Metric.analysis_id == Analysis.analysis_id)\
         .join(Image, Image.image_id == Analysis.image_id)\
         .group_by(Analysis.analysis_time, Image.file_path, Model.name)\
         .all()

        # Preparar los datos para la tabla de detalles
        detail_table = []
        for row in detailed_data:
            detail_table.append({
                'date': row.date,
                'image': row.image,
                'model': row.model,
                'age': row.age,
                'gender': row.gender,
                'emotion': row.emotion
            })

        return detail_table
