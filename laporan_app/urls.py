from django.urls import path
from .views import RevenueSummaryView, DailySalesChartView
urlpatterns = [
    path('revenue-summary/', RevenueSummaryView.as_view(), name='revenue-summary'),
    path('daily-sales/', DailySalesChartView.as_view(), name='daily-sales'),
    
]
