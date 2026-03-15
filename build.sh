#!/usr/bin/env bash
set -o errexit

if [ -z "$VERCEL" ]; then
  echo "Ambiente fora da Vercel detectado. Instalando dependências..."
  pip install -r requirements.txt
fi

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_admin