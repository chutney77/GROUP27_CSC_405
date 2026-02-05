from django import forms
from django.forms import formset_factory, BaseFormSet
from .models import Accounts

# ───────────────────────────────────────────────
# Choices
# ───────────────────────────────────────────────
LEVEL_CHOICES = [
    ('', 'Select Level'),
    ('100', '100 Level'),
    ('200', '200 Level'),
    ('300', '300 Level'),
    ('400', '400 Level'),
    ('500', '500 Level'),
]

DEPARTMENT_CHOICES = [
    ('', 'Select Department'),
    ('Computer Science', 'Computer Science'),
    ('Cyber Security', 'Cyber Security'),
    ('Software Engineering', 'Software Engineering'),
    ('Microbiology', 'Microbiology'),
    ('Biochemistry', 'Biochemistry'),
    ('Industrial Chemistry', 'Industrial Chemistry'),
]

GRADE_CHOICES = [
    ('A', 'A'), ('B', 'B'), ('C', 'C'),
    ('D', 'D'), ('E', 'E'), ('F', 'F'),
]

STATUS_CHOICES = [
    ('Registered', 'Registered'),
    ('In Progress', 'In Progress'),
    ('Re-enrolled', 'Re-enrolled'),
]


# ───────────────────────────────────────────────
# Registration Form
# ───────────────────────────────────────────────
class AccountForm(forms.ModelForm):
    fullname = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Full Name"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Email"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone Number"}))
    matric_number = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Matric Number"}))

    class Meta:
        model = Accounts
        fields = "__all__"

    def clean_matric_number(self):
        matric = self.cleaned_data.get("matric_number")
        if Accounts.objects.filter(matric_number=matric).exists():
            raise forms.ValidationError("Matric number already registered.")
        return matric


# ───────────────────────────────────────────────
# Student Basic Info Form
# ───────────────────────────────────────────────
class StudentBasicForm(forms.Form):
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,  # ← fixed: use constant
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Department",
        error_messages={'required': 'Please select your department.'}
    )

    cgpa = forms.FloatField(
        min_value=0.0,
        max_value=5.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'e.g. 3.45'
        })
    )
    
    cgpa_trend = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 3.1, 3.45, 2.98 (optional)'
        })
    )


# ───────────────────────────────────────────────
# Course Forms & FormSets
# ───────────────────────────────────────────────
class PastCourseForm(forms.Form):
    course = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. CSC101'
        }),
        required=False
    )
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )


class CurrentCourseForm(forms.Form):
    course = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. CSC201'
        }),
        required=False
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )


PastCourseFormSet = formset_factory(
    PastCourseForm,
    formset=BaseFormSet,
    extra=6,
    min_num=6,
    validate_min=True,
    can_delete=True
)

CurrentCourseFormSet = formset_factory(
    CurrentCourseForm,
    formset=BaseFormSet,
    extra=6,
    min_num=6,
    validate_min=True,
    can_delete=True
)