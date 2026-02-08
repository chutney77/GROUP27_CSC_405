"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('firstpage.urls')),  # root points to your firstpage app
    path('admin/', admin.site.urls),
]

firstpage/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from .forms import AccountForm, StudentBasicForm, PastCourseFormSet, CurrentCourseFormSet
from .models import Accounts
from .ml.predictor import predict_academic_risk


# ──────────────────────────────
# Registration View
# ──────────────────────────────
def register_view(request):
    form = AccountForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect(reverse('login'))  # Named URL
    context = {'form': form}
    return render(request, "uniguide_register.html", context)


# ──────────────────────────────
# Login View
# ──────────────────────────────
def login_view(request):
    error = None
    if request.method == "POST":
        matric = request.POST.get("matric_number")
        try:
            student = Accounts.objects.get(matric_number=matric)
            request.session["student_id"] = student.id
            request.session["matric_number"] = student.matric_number
            return redirect(reverse('dashboard'))  # Named URL
        except Accounts.DoesNotExist:
            error = "Matric number not registered"
    return render(request, "uniguide_login.html", {"error": error})


# ──────────────────────────────
# Logout View
# ──────────────────────────────
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect(reverse('login'))  # Named URL
    return render(request, 'firstpage_logout.html')


# ──────────────────────────────
# Dashboard View
# ──────────────────────────────
def dashboard_view(request):
    if 'student_id' not in request.session:
        return redirect(reverse('login'))

    if request.method == 'POST':
        basic_form = StudentBasicForm(request.POST)
        past_formset = PastCourseFormSet(request.POST, prefix='past')
        current_formset = CurrentCourseFormSet(request.POST, prefix='current')

        if basic_form.is_valid() and past_formset.is_valid() and current_formset.is_valid():
            cleaned_data = {
                'gpa_cgpa': basic_form.cleaned_data['cgpa'],
                'cgpa_trend': basic_form.cleaned_data['cgpa_trend'],
                'department': basic_form.cleaned_data['department'],
                'past_courses': [
                    {'course': f.cleaned_data['course'], 'grade': f.cleaned_data['grade']}
                    for f in past_formset.forms
                    if f.has_changed() and f.cleaned_data.get('course')
                ],
                'current_courses': [
                    {'course': f.cleaned_data['course'], 'status': f.cleaned_data['status']}
                    for f in current_formset.forms
                    if f.has_changed() and f.cleaned_data.get('course')
                ]
            }

            # Analyse student
            result_dict, status_code = analyse_student(cleaned_data)

            # ML prediction
            try:
                ml_risk = predict_academic_risk(
                    cleaned_data["gpa_cgpa"],
                    basic_form.cleaned_data.get("level"),
                    len(cleaned_data["past_courses"]) + len(cleaned_data["current_courses"]),
                    cleaned_data["cgpa_trend"]
                )
                result_dict['ml_risk_level'] = ml_risk
            except Exception:
                result_dict['ml_risk_level'] = "Unavailable"

            if status_code == 200:
                return render(request, 'uniguide_dashboard.html', {
                    'basic_form': basic_form,
                    'past_formset': past_formset,
                    'current_formset': current_formset,
                    'result': result_dict,
                    'show_result': True,
                    'matric_number': request.session.get('matric_number')
                })
            else:
                return render(request, 'uniguide_dashboard.html', {
                    'basic_form': basic_form,
                    'past_formset': past_formset,
                    'current_formset': current_formset,
                    'error_message': result_dict.get('error', 'Analysis failed'),
                    'show_result': False
                })
    else:
        basic_form = StudentBasicForm()
        past_formset = PastCourseFormSet(prefix='past')
        current_formset = CurrentCourseForm_
