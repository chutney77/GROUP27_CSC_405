from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Uniguide/', include('uniguide.urls', namespace='uniguide')),  # our app URLs
]
