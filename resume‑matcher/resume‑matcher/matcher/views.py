import os
from pathlib import Path
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .forms import ResumeForm, JDForm
from .utils import extract_resume, extract_jd, keyword_match_stats

# ----- step 1 -----
def upload_resume(request):
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            pdf_path = fs.save(form.cleaned_data["resume"].name, 
                               form.cleaned_data["resume"])
            resume_text = extract_resume(Path(fs.path(pdf_path)))
            # store path for later
            request.session["resume_text"] = resume_text
            return redirect("upload_jd")
    else:
        form = ResumeForm()
    return render(request, "matcher/resume_upload.html", {"form": form})

# ----- step 2 -----
def upload_jd(request):
    if request.method == "POST":
        form = JDForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            doc_path = fs.save(form.cleaned_data["jd_file"].name, 
                               form.cleaned_data["jd_file"])
            jd_text = extract_jd(Path(fs.path(doc_path)))

            # Azure call
            stats = keyword_match_stats(
                request.session["resume_text"], jd_text
            )
            jd_key   = stats["JDKey"]
            match_key = stats["MatchKey"]
            score = (match_key / jd_key) * 100 if jd_key else 0
            favorable = score >= 75

            context = {
                "job_title": form.cleaned_data["job_title"],
                "score": f"{score:.1f}",
                "favorable": favorable,
            }
            return render(request, "matcher/result.html", context)
    else:
        form = JDForm()
    return render(request, "matcher/jd_upload.html", {"form": form})
