from django import forms
from .models import Issue, Ward, Department


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            'title', 'category', 'severity', 'ward', 'description',
            'photo', 'latitude', 'longitude', 'address', 'reporter_name', 'reporter_phone'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition',
                'placeholder': 'e.g. Dangerous deep crater on Road 11 Banani',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:border-blue-500 transition cursor-pointer'
            }),
            'severity': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:border-blue-500 transition cursor-pointer'
            }),
            'ward': forms.Select(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:border-blue-500 transition cursor-pointer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition',
                'rows': 3,
                'placeholder': 'Provide exact landmarks, depth/scale of hazard, or urgency details...',
                'required': True
            }),
            'photo': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'photo-file-input',
                'accept': 'image/*'
            }),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition',
                'placeholder': 'e.g. Road 11, Block D, Banani, Dhaka'
            }),
            'reporter_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition',
                'placeholder': 'Your Name or "Anonymous"'
            }),
            'reporter_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition',
                'placeholder': 'e.g. 017XXXXXXXX (optional)'
            }),
        }


class MunicipalTriageForm(forms.Form):
    """
    Form used by Ward / City Municipal Officials to triage and update issues.
    """
    STATUS_CHOICES = [
        ('In Progress', 'In Progress (Work Order Dispatched)'),
        ('Resolved', 'Resolved (Repair Complete with Proof)'),
        ('Under Review', 'Under Review / Site Inspection'),
        ('Rejected', 'Rejected (Out of Municipal Jurisdiction / Duplicate)'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-bold text-slate-800 dark:text-slate-100'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-800 dark:text-slate-100'
        })
    )
    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs font-medium text-slate-800 dark:text-slate-100',
            'rows': 3,
            'placeholder': 'Provide official update remarks, contractor name, or resolution summary...'
        }),
        required=False
    )
    resolution_proof_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'text-xs text-slate-600 dark:text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })
    )
