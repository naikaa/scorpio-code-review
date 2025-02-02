from django.urls import path

from . import views
from .views import index,viewrepo, view_pull_request, llm_review

urlpatterns = [
    
    path('', index, name='index'),
    path('viewrepo/',viewrepo, name="viewrepo"),
    path("review/<int:pr_number>/", view_pull_request, name="view_pull_request"),
    path('llm_review/', llm_review, name="llm_review"),
]