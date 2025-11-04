from django.shortcuts import render  # без redirect для теста

def index(request):
    # ВРЕМЕННО: всегда просто рендерим публичную страницу
    return render(request, 'landing.html')
