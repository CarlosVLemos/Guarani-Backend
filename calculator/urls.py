from django.urls import path
from . import views

urlpatterns = [
    path('train/', views.train_model_view, name='train_model'),
    path('predict/', views.predict_prices_view, name='predict_prices'),
]