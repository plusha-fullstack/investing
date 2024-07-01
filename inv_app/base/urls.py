# from django.urls import path, include
# from .views import authView, home

# urlpatterns = [
# path("", home, name="home"),
# path("signup/", authView, name="authView"),
# path("accounts/", include("django.contrib.auth.urls")),
# ]
# from django.urls import path, include
# from .views import authView, home

# urlpatterns = [
#     path("", home, name="home"),
#     path("signup/", authView, name="authView"),
#     path("accounts/", include("django.contrib.auth.urls")),
# ]
# from django.urls import path, include
# from .views import authView, home


# urlpatterns = [
#     path("", home, name="home"),
#     path("signup/", authView, name="authView"),
#     path("accounts/", include("django.contrib.auth.urls")),
# ]
# urlpatterns = [
#     path("", home, name="home"),
#     path("signup/", authView, name="authView"),
#     path("accounts/", include("django.contrib.auth.urls")),
#     path("delete/<int:pk>/", delete_portfolio_item, name="delete_portfolio_item"),
# ]
from django.urls import path, include
from .views import authView, home, delete_portfolio_item,history,analyze
app_name = 'base' 
urlpatterns = [
    path("", home, name="home"),
    path("history/", history, name="history"),
    path("signup/", authView, name="authView"),
    path("delete/<int:pk>/", delete_portfolio_item, name="delete_portfolio_item"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('analyze/', analyze, name='analyze'),
]
