from django.urls import path

from apps.general import views

urlpatterns = [
    path("site-detail/", views.SiteDetailView.as_view()),
    path("subscribe/", views.SubscriberCreateView.as_view()),
    path("reviews/", views.ReviewsView.as_view()),
]
