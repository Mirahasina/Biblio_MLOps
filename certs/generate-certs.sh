#!/bin/bash
# Génère un certificat SSL auto-signé pour www.e-commerce.lcl

set -e

CERT_DIR="$(dirname "$0")"
DOMAIN="www.e-commerce.lcl"

echo "=== Génération certificat SSL pour ${DOMAIN} ==="

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "${CERT_DIR}/file.key" \
  -out "${CERT_DIR}/file.crt" \
  -subj "/C=MG/ST=Antananarivo/L=Antananarivo/O=E-Commerce/OU=DevSecOps/CN=${DOMAIN}"

echo ""
echo "Certificats générés :"
echo "  - ${CERT_DIR}/file.crt  (certificat public)"
echo "  - ${CERT_DIR}/file.key  (clé privée)"
echo ""
echo "Créer le secret K8S :"
echo "  kubectl create secret tls tls-secret \\"
echo "    --cert=${CERT_DIR}/file.crt \\"
echo "    --key=${CERT_DIR}/file.key \\"
echo "    -n ecommerce"
echo ""
echo "Ajouter dans /etc/hosts :"
echo "  127.0.0.1  www.e-commerce.lcl"
