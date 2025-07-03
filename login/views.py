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
    print("--- [auth_receiver] A view foi chamada. ---")
    try:
        token = request.POST.get('credential')
        if not token:
            print("ERRO: Credencial não encontrada no POST.")
            return HttpResponse("Credential POST data not found.", status=400)
        print("--- [auth_receiver] Token recebido com sucesso. ---")

        # PASSO CORRIGIDO: Usando .get() e verificando se a chave existe
        client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        if not client_id:
            print("ERRO CRÍTICO: GOOGLE_OAUTH_CLIENT_ID não está definido no ambiente do Render.")
            return HttpResponse("Server configuration error: Missing Client ID.", status=500)
        print("--- [auth_receiver] Client ID do ambiente lido com sucesso. ---")

        print("--- [auth_receiver] Tentando verificar o token com o Google...")
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), client_id
        )
        print("--- [auth_receiver] Token verificado com sucesso! Email:", user_data.get('email'))

        request.session['user_data'] = user_data
        print("--- [auth_receiver] Dados salvos na sessão. Redirecionando...")
        return redirect('sign_in')

    except Exception as e:
        # Pega QUALQUER exceção, imprime o erro detalhado e retorna 500
        print(f"!!!!!!!!!! ERRO INESPERADO EM AUTH_RECEIVER !!!!!!!!!!")
        print(f"Tipo do Erro: {type(e).__name__}")
        print(f"Mensagem do Erro: {e}")
        traceback.print_exc() # Imprime o traceback completo no log
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return HttpResponse("An unexpected error occurred.", status=500)

def sign_out(request):
    if 'user_data' in request.session:
        del request.session['user_data']
    return redirect('sign_in')