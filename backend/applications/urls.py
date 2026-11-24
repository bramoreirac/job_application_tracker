from django.urls import path

from .views import ApplicationListCreateView
from .views import ApplicationDetailView

urlpatterns = [
    path("", ApplicationListCreateView.as_view(), name="application-list-create"),
    path("<uuid:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]