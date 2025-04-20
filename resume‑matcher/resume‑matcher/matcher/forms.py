from django import forms

class ResumeForm(forms.Form):
    resume = forms.FileField(
        label="Upload PDF resume", 
        widget=forms.ClearableFileInput(attrs={"accept":".pdf"})
    )

class JDForm(forms.Form):
    job_title = forms.CharField(max_length=120, label="Job title")
    jd_file   = forms.FileField(
        label="Upload Word description", 
        widget=forms.ClearableFileInput(attrs={"accept":".doc,.docx"})
    )
