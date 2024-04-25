"""
URL configuration for sensors project.

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
import rest_framework.routers
import sensors.views

router = rest_framework.routers.DefaultRouter()
router.register(r"readings", sensors.views.ReadingViewSet)
router.register(r"devices", sensors.views.DeviceViewSet)

urlpatterns = [
    path("admin/", admin.site.urls, name="admin:index"),
    path("", sensors.views.Home.as_view(), name="home"),
    # path("c/", sensors.views.Chart.as_view(), name="chart"),
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
    # path("test/", sensors.views.Test.as_view(), name="test"),
]
