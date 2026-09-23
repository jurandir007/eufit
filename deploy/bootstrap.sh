#!/usr/bin/env bash
# bootstrap.sh — prepara a VM do GCE para rodar o EUFit.
# Roda UMA vez, dentro da VM, como o usuário jurandir_fisico.
# Pré-requisito: git clone do repo já feito em ~/eufit

set -euo pipefail

PROJECT_DIR="${HOME}/eufit"
cd "${PROJECT_DIR}"

echo "▶️  Instalando pacotes base (Python, venv, pip, git)"
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git

echo "▶️  Criando venv"
if [ ! -d "${PROJECT_DIR}/.venv" ]; then
    python3 -m venv "${PROJECT_DIR}/.venv"
fi

echo "▶️  Instalando dependências"
"${PROJECT_DIR}/.venv/bin/pip" install --upgrade pip
"${PROJECT_DIR}/.venv/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"

echo "▶️  Verificando .env"
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo "⚠️  ${PROJECT_DIR}/.env não existe!"
    echo "    Crie o arquivo antes de continuar. Exemplo:"
    echo "        SECRET_KEY=cole-aqui"
    echo "        DATABASE_URL=sqlite:////home/jurandir_fisico/eufit/instance/app.db"
    exit 1
fi

echo "▶️  Aplicando migrações"
"${PROJECT_DIR}/.venv/bin/flask" --app run:app db upgrade

echo "▶️  Instalando systemd unit"
sudo cp "${PROJECT_DIR}/deploy/eufit.service" /etc/systemd/system/eufit.service
sudo systemctl daemon-reload
sudo systemctl enable eufit.service
sudo systemctl restart eufit.service

echo "▶️  Instalando config do Nginx"
sudo cp "${PROJECT_DIR}/deploy/nginx-eufit.conf" /etc/nginx/sites-available/eufit
sudo ln -sf /etc/nginx/sites-available/eufit /etc/nginx/sites-enabled/eufit
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo
echo "✅ Tudo pronto!"
echo
echo "Verifica:"
echo "  sudo systemctl status eufit"
echo "  sudo systemctl status nginx"
echo "  curl -I http://127.0.0.1:8000"
echo "  curl -I http://eufit.duckdns.org"
