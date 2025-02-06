from celery import Celery

def make_celery():
    celery = Celery(
        'aiogram_project', 
        broker='redis://localhost:6379/0', 
        backend='redis://localhost:6379/0'
    )
    return celery

celery_app = make_celery()
