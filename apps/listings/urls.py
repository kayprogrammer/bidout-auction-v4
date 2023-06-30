from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListingsView.as_view()),
    path("watchlist/", views.ListingsByWatchListView.as_view()),
    path("categories/", views.CategoriesView.as_view()),
    path("categories/<slug:slug>/", views.CategoryListingsView.as_view()),
    path("<slug:slug>/", views.ListingDetailView.as_view()),
    path("<slug:slug>/bids/", views.BidsView.as_view()),
]
