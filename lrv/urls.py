"""
URL configuration for lrv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from apps.users.views import register_view

def dummy_view(request):
    return HttpResponse("This module is currently inactive.")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path("api/loans/", include("apps.loans.urls")),
    path("api/repayments/", include("apps.repayments.urls")),
    path("interviews/", include("apps.interviews.urls", namespace="interviews")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("bookbrief.web_urls")),
    path("api/bookbrief/", include("bookbrief.urls", namespace="bookbrief")),
    path("cricket/", include("cricket.urls", namespace="cricket")),
    path("pm/", include("apps.project_management.urls", namespace="project_management")),
    path('todos/', include('apps.todos.urls')),
    path('money/', include('apps.money_management.urls', namespace='money_management')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
