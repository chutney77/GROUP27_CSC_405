from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import AccountForm, StudentBasicForm, PastCourseFormSet, CurrentCourseFormSet
from .models import Accounts
from .ml.predictor import predict_academic_risk

# ---------------------------
# Registration
# ---------------------------
def register_view(request):
    form = AccountForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect(reverse('uniguide:login'))
    context = {'form': form}
    return render(request, "uniguide_register.html", context)

# ---------------------------
# Login
# ---------------------------
def login_view(request):
    error = None
    if request.method == "POST":
        matric = request.POST.get("matric_number")
        try:
            student = Accounts.objects.get(matric_number=matric)
            request.session["student_id"] = student.id
            request.session["matric_number"] = student.matric_number
            return redirect(reverse('uniguide:dashboard'))
        except Accounts.DoesNotExist:
            error = "Matric number not registered"
    return render(request, "uniguide_login.html", {"error": error})

# ---------------------------
# Logout
# ---------------------------
def logout_view(request):
    request.session.flush()
    return redirect(reverse('uniguide:login'))

# ---------------------------
# Dashboard & Analysis
# ---------------------------
def analyse_student(data):
    # Your existing analyse_student code unchanged
    # ...
    return {
        'risk_level': "Low",
        'cgpa_trend': "Stable",
        'suggestions': [],
        'cautions': [],
        'explanation': "Analysis done."
    }, 200

def dashboard_view(request):
    if 'student_id' not in request.session:
        return redirect(reverse('uniguide:login'))

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
                    for f in past_formset.forms if f.has_changed() and f.cleaned_data.get('course')
                ],
                'current_courses': [
                    {'course': f.cleaned_data['course'], 'status': f.cleaned_data['status']}
                    for f in current_formset.forms if f.has_changed() and f.cleaned_data.get('course')
                ]
            }

            result_dict, status_code = analyse_student(cleaned_data)

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

            return render(request, 'uniguide_dashboard.html', {
                'basic_form': basic_form,
                'past_formset': past_formset,
                'current_formset': current_formset,
                'result': result_dict,
                'show_result': True,
                'matric_number': request.session.get('matric_number')
            })
    else:
        basic_form = StudentBasicForm()
        past_formset = PastCourseFormSet(prefix='past')
        current_formset = CurrentCourseFormSet(prefix='current')

    return render(request, 'uniguide_dashboard.html', {
        'basic_form': basic_form,
        'past_formset': past_formset,
        'current_formset': current_formset,
        'show_result': False,
        'matric_number': request.session.get('matric_number')
    })
