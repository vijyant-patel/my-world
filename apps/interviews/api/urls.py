from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, TagViewSet, CompanyViewSet,
    InterviewViewSet, QuestionViewSet, NoteViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'interviews', InterviewViewSet, basename='interview')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
