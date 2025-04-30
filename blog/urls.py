from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('editor/upload/', views.editor_upload_handler, name="editor-upload-handler"),
]