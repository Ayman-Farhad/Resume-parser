from django.contrib import admin
from django.urls import path
from matcher import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",        views.upload_resume, name="upload_resume"),
    path("step2/",  views.upload_jd,     name="upload_jd"),
]
