import os
from dotenv import load_dotenv

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

@csrf_exempt
def sign_in(request):
    """
    Renderiza a página de login. Se o usuário já estiver logado,
    mostra as informações dele.
    """
    # Constrói a URI de callback dinamicamente para não ter um link fixo.
    login_uri = request.build_absolute_uri(reverse('auth_receiver'))
    context = {
        'login_uri': login_uri,
         'google_client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    }
    return render(request, 'login/sign_in.html', context)

@csrf_exempt
def auth_receiver(request):
    # URL chamada depois de fazer login
    
    # Pega o token enviado pelo Google via POST
    token = request.POST.get('credential')

    if not token:
        return HttpResponse(status=400, content="Credencial não encontrada.")

    try:
        # Verifica se o token é válido
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        # Se o token for inválido, retorna um erro
        return HttpResponse(status=403)

    # Se o token é válido os dados de usuário são salvos
    request.session['user_data'] = user_data

    return redirect('sign_in')

def sign_out(request):
    if 'user_data' in request.session:
        del request.session['user_data']
    return redirect('sign_in')