from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProfileView.as_view()),
    path("listings/", views.AuctioneerListingsView.as_view()),
    path("listings/<slug:slug>/", views.UpdateListingView.as_view()),
    path("listings/<slug:slug>/bids/", views.AuctioneerListingBids.as_view()),
]
