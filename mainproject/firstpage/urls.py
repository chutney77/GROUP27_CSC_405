from django.urls import path
from .views import (
                    login_view,
                    logout_view,
                    register_view,
                    dashboard_view
)

app_name = 'uniguide'

urlpatterns =[
    path('', login_view, name='home'),
    path('login/', login_view,name = 'login'),
    path('register/', register_view,name = 'register'),
    path('dashboard/', dashboard_view,name = 'dashboard' )

]
