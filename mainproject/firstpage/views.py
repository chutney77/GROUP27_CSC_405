from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse
from .forms import AccountForm
from django.contrib import messages
from .models import Accounts
import json
from .ml.predictor import predict_academic_risk


# Create your views here.
def register_view(request):
    form = AccountForm(request.POST or None)
    if form.is_valid():
        form.save()
        #form = AccountForm(request.POST or None)
        #Account_object = form.save()
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('/Uniguide/login/')
    context = { 'form' : form }
    return render(request, "uniguide_register.html", context)#product/detail.html is the directory of the detail.html it is still a template
    
def login_view(request):
    error = None

    if request.method == "POST":
        matric = request.POST.get("matric_number")

        try:
            student = Accounts.objects.get(matric_number=matric)
            request.session["student_id"] = student.id
            request.session["matric_number"] = student.matric_number
            return redirect("/Uniguide/dashboard/")
        except Accounts.DoesNotExist:
            error = "Matric number not registered"

    return render(request, "uniguide_login.html", {"error": error})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('/firstpage/login/')
    return render(request,'firstpage_logout.html',{} )

def analyse_student(data):
    # ───────────────────────────────────────────────
    # Validation
    # ───────────────────────────────────────────────
    gpa = data.get('gpa_cgpa', -1)
    if not isinstance(gpa, (int, float)) or gpa < 0 or gpa > 5.0:
        return {'error': 'GPA/CGPA must be between 0.0 and 5.0'}, 400

    past = data.get('past_courses', [])
    if not isinstance(past, list) or len(past) < 6 or len(past) > 9:
        return {'error': 'Must provide 6–9 past courses'}, 400

    current = data.get('current_courses', [])
    if not isinstance(current, list) or len(current) < 6 or len(current) > 9:
        return {'error': 'Must provide 6–9 current courses'}, 400

    # ───────────────────────────────────────────────
    # Parse CGPA trend (comma string or list)
    # ───────────────────────────────────────────────
    trend_input = data.get('cgpa_trend', '')
    trend_list = []
    if isinstance(trend_input, str):
        parts = [p.strip() for p in trend_input.split(',') if p.strip()]
        for p in parts:
            try:
                trend_list.append(float(p))
            except ValueError:
                pass

    # ───────────────────────────────────────────────
    # Past grades processing
    # ───────────────────────────────────────────────
    num_poor = 0
    num_severe = 0
    past_grades = {}  # course.lower() -> grade.upper()
    for c in past:
        course = str(c.get('course', '')).strip().lower()
        grade = str(c.get('grade', '')).strip().upper()
        if course and grade in ['A','B','C','D','E','F']:
            past_grades[course] = grade
            if grade in {'D','E','F'}:
                num_poor += 1
            if grade in {'E','F'}:
                num_severe += 1

    # ───────────────────────────────────────────────
    # Infer repeated poor / retakes
    # ───────────────────────────────────────────────
    repeated_courses = []
    num_repeated = 0
    for c in current:
        course = str(c.get('course', '')).strip().lower()
        status = str(c.get('status', '')).strip().lower()
        if not course:
            continue
        prev_grade = past_grades.get(course)
        is_repeat = (prev_grade in {'D','E','F'}) or (status == 're-enrolled')
        if is_repeat:
            num_repeated += 1
            repeated_courses.append(c.get('course', '').strip())

    # ───────────────────────────────────────────────
    # Base risk level
    # ───────────────────────────────────────────────
    risk = "Low"
    if gpa <= 2.49:
        risk = "High"
    elif gpa <= 3.49:
        risk = "Medium"

    # ───────────────────────────────────────────────
    # Trend
    # ───────────────────────────────────────────────
    trend_text = "Not enough data"
    if len(trend_list) >= 2:
        last, prev = trend_list[-1], trend_list[-2]
        if gpa >= 4.50:
            trend_text = "Stable"
        elif last > prev:
            trend_text = "Improving"
        elif last < prev:
            trend_text = "Declining"
        else:
            trend_text = "Stable"

    # ───────────────────────────────────────────────
    # Risk bumps
    # ───────────────────────────────────────────────
    if num_severe >= 3 or num_repeated >= 2:
        risk = "High"
    elif num_poor >= 3 or num_repeated >= 1:
        if risk == "Low":
            risk = "Medium"
        elif risk == "Medium":
            risk = "High"

    # ───────────────────────────────────────────────
    # Messages (longer, motivational + urgent where needed)
    # ───────────────────────────────────────────────
    suggestions = []
    cautions = []

    if gpa >= 4.50 and risk == "Low":
        suggestions.append(
            "Outstanding academic performance. You are doing excellently well — maintain consistency, discipline, and healthy study habits. "
            "You've got this; keep pushing for even greater achievements."
        )
    else:
        if risk == "High":
            cautions.append(
                "High academic risk detected. Your performance needs immediate attention this semester — don't wait, as this could lead to bigger setbacks like probation or extra years. "
                "Act now by consulting an academic adviser and focusing on recovery strategies."
            )
            suggestions.append(
                "Reduce course load where possible, focus on core courses, and consult an academic adviser immediately. "
                "You've got this turnaround in you — create a strict study plan and stick to it for real results."
            )
        elif risk == "Medium" and trend_text == "Declining":
            cautions.append(
                "Your academic performance shows signs of decline. This trend can worsen if not addressed right away — don't let it slide further. "
                "This needs your attention this semester to get back on track."
            )
            suggestions.append(
                "Increase study time, review weak subjects, and seek academic support early. "
                "You can reverse this — stay motivated and consistent, and you'll see improvement soon."
            )

        if num_severe > 0:
            cautions.append(
                f"You have {num_severe} failing grades (E or F) in past courses, which increases your risk. These can drag your CGPA down if patterns continue — act now to break the cycle. "
                "Don't wait; this is a key area for improvement this semester."
            )
        if num_poor > num_severe:
            num_ds = num_poor - num_severe
            cautions.append(
                f"You have {num_ds} weak grades (D) in past courses. While not fails, they signal areas needing stronger effort — focus here to avoid escalation. "
                "You've got the potential; make it count."
            )

        if num_repeated > 0:
            courses_str = ", ".join(repeated_courses[:3]) if repeated_courses else "some courses"
            cautions.append(
                f"Repeated poor performance detected in {num_repeated} courses like {courses_str}. Retakes add pressure and can delay progress — this needs urgent attention this semester. "
                "Don't wait to tackle these; failing again would compound the issue."
            )
            suggestions.append(
                f"Focus on upcoming courses with weak past grades like {courses_str}. You've got this — dedicate extra time, seek tutoring or resources, and aim high to clear them strongly. "
                "Prioritize these retakes; success here will boost your standing significantly."
            )

        suggestions.append(
            "Maintain a balanced study routine and prioritize core departmental courses. Keep pushing forward — discipline now leads to success later."
        )

    explanation = "This analysis considers GPA/CGPA level, CGPA trend progression, past course grades, inferred retakes, and standard university advising principles."

    return {
        'risk_level': risk,
        'cgpa_trend': trend_text,
        'suggestions': suggestions,
        'cautions': cautions,
        'explanation': explanation
    }, 200


from django.shortcuts import render, redirect
from .forms import StudentBasicForm, PastCourseFormSet, CurrentCourseFormSet

def dashboard_view(request):
    if 'student_id' not in request.session:
        return redirect('/Uniguide/login/')

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
                    {
                        'course': form.cleaned_data['course'],
                        'grade': form.cleaned_data['grade']
                    }
                    for form in past_formset.forms
                    if form.has_changed() and form.cleaned_data.get('course')
                ],
                'current_courses': [
                    {
                        'course': form.cleaned_data['course'],
                        'status': form.cleaned_data['status']
                    }
                    for form in current_formset.forms
                    if form.has_changed() and form.cleaned_data.get('course')
                ]
            }


            gpa = cleaned_data["gpa_cgpa"]
            level = basic_form.cleaned_data.get("level")
            total_courses = len(cleaned_data["past_courses"]) + len(cleaned_data["current_courses"])
            cgpa_trend = cleaned_data["cgpa_trend"]




            # Call the analysis function
            result_dict, status_code = analyse_student(cleaned_data)


            # ML prediction 
            try:
                ml_risk = predict_academic_risk(
                    gpa,
                    level,
                    total_courses,
                    cgpa_trend
                )

                result_dict['ml_risk_level'] = ml_risk

            except Exception:
                ml_risk = "Unavailable"


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

        # Invalid → re-render with errors
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



    