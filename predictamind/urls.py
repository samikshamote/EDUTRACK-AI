from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.predict_view, name="predict"),
    path("generate-pdf/", views.generate_pdf, name="generate_pdf"),
    path("result/", views.auto_result, name="auto_result"),


]
