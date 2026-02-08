from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from .forms import AccountForm, StudentBasicForm, PastCourseFormSet, CurrentCourseFormSet
from .models import Accounts
from .ml.predictor import predict_academic_risk
from .ml.analyzer import analyse_student  # 👈 Import the analysis logic


# ──────────────────────────────
# Registration View
# ──────────────────────────────
def register_view(request):
    form = AccountForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('uniguide:login')
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
            return redirect('uniguide:dashboard')
        except Accounts.DoesNotExist:
            error = "Matric number not registered"
    return render(request, "uniguide_login.html", {"error": error})


# ──────────────────────────────
# Logout View
# ──────────────────────────────
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('uniguide:login')
    return render(request, 'firstpage_logout.html')


# ──────────────────────────────
# Dashboard View
# ──────────────────────────────
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
                    for f in past_formset.forms
                    if f.has_changed() and f.cleaned_data.get('course')
                ],
                'current_courses': [
                    {'course': f.cleaned_data['course'], 'status': f.cleaned_data['status']}
                    for f in current_formset.forms
                    if f.has_changed() and f.cleaned_data.get('course')
                ]
            }

            # ═══════════════════════════════════════════════════════
            # PRIMARY ANALYSIS: Logic-based recommendation system
            # ═══════════════════════════════════════════════════════
            result_dict, status_code = analyse_student(cleaned_data)

            # ═══════════════════════════════════════════════════════
            # SECONDARY SUPPORT: ML prediction (adds extra insight)
            # ═══════════════════════════════════════════════════════
            try:
                ml_result = predict_academic_risk(
                    cleaned_data["gpa_cgpa"],
                    basic_form.cleaned_data.get("level"),
                    len(cleaned_data["past_courses"]) + len(cleaned_data["current_courses"]),
                    cleaned_data["cgpa_trend"]
                )
                # ML returns a dict like {'mlRiskLevel': 'Low', 'mlConfidence': 0.85}
                if isinstance(ml_result, dict):
                    result_dict['ml_risk_level'] = ml_result.get('mlRiskLevel', 'Unknown')
                    result_dict['ml_confidence'] = ml_result.get('mlConfidence', 0)
                else:
                    result_dict['ml_risk_level'] = str(ml_result)
                    result_dict['ml_confidence'] = None
            except Exception as e:
                result_dict['ml_risk_level'] = "Unavailable"
                result_dict['ml_confidence'] = None
                print(f"ML Prediction Error: {e}")  # For debugging

            # ═══════════════════════════════════════════════════════
            # RENDER RESULTS
            # ═══════════════════════════════════════════════════════
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
                # Analysis failed
                return render(request, 'uniguide_dashboard.html', {
                    'basic_form': basic_form,
                    'past_formset': past_formset,
                    'current_formset': current_formset,
                    'error_message': result_dict.get('error', 'Analysis failed'),
                    'show_result': False
                })

    else:
        # GET request - show empty form
        basic_form = StudentBasicForm()
        past_formset = PastCourseFormSet(prefix='past')
        current_formset = CurrentCourseFormSet(prefix='current')

    return render(request, 'uniguide_dashboard.html', {
        'basic_form': basic_form,
        'past_formset': past_formset,
        'current_formset': current_formset,
        'show_result': False
    })
