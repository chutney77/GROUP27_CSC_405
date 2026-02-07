from django.shortcuts import render, redirect
from django.contrib.auth import logout

def login_view(request):
    if request.method == "POST":
        return redirect("firstpage:dashboard")
    return render(request, "uniguide_login.html")

def register_view(request):
    if request.method == "POST":
        return redirect("firstpage:login")
    return render(request, "uniguide_register.html")

def dashboard_view(request):
    return render(request, "uniguide_dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("firstpage:login")
