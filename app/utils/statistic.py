import datetime
import pandas as pd
from database import models, db_utils


def get_stat():
    # Нужна функция для вывода всех мастеров массивом или списком
    masters = db_utils.get_masters()
    stats = {
        'Мастер': masters,
        'Количество записей': [],
        'Отмены': [],
        'Выручка': [],
        'Активность мастера (%)': []
    }
    for master in masters:
        appointments = master.appointments
        stats['Количество записей'] += [len(appointments)]
        stats['Отмены'] += [0]
        stats['Выручка'] += [0]
        for appointment in appointments:
            if appointment.status == 'cancelled':
                stats['Отмены'][-1] += 1
            elif appointment.status == 'confirmed' and appointment.start_time >= datetime.time:
                stats['Выручка'][-1] += db_utils.get_service_by_appointment(appointment).price
        stats['Активность мастера (%)'] += [
            (stats['Количество записей'][-1] - stats['Отмены'][-1]) / stats['Количество записей'][-1] * 100]
    return pd.DataFrame(stats)

def get_stat_to_xlsx():
    return get_stat().to_excel('stat.xlsx', index=False)

def get_stat_to_csv():
    return get_stat().to_cvs('stat.cvs', index=False)