from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListingsView.as_view()),
    path("<slug:slug>/", views.ListingDetailView.as_view()),
]
