from core.models import SiteConfig
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    cfg = SiteConfig.objects.first()
    return render(request, "landing.html", {"site_config": cfg})

