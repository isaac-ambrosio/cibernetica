import os
from PIL import Image

# Caminho da pasta de entrada (onde estão as imagens originais)
pasta_origem = "/content/drive/MyDrive/cibernetica/Proj2/imagens_buriti"  # Substitua pelo caminho correto

# Caminho da pasta de saída (onde serão salvas as imagens redimensionadas)
pasta_saida = "/content/drive/MyDrive/cibernetica/Proj2/imagens_buriti_red"
os.makedirs(pasta_saida, exist_ok=True)

# Dimensão desejada
nova_largura = 640
nova_altura = 640

# Processa todas as imagens na pasta de origem
for arquivo in os.listdir(pasta_origem):
    caminho_completo = os.path.join(pasta_origem, arquivo)

    # Verifica se é uma imagem (extensões comuns)
    if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
        try:
            # Abre a imagem
            img = Image.open(caminho_completo)

            # Redimensiona mantendo proporção e preenchendo para 640x640
            img = img.resize((nova_largura, nova_altura), Image.LANCZOS)

            # Salva na pasta de saída
            novo_nome = arquivo[-9:]
            caminho_saida = os.path.join(pasta_saida, novo_nome)
            img.save(caminho_saida)

            print(f"Imagem {arquivo} redimensionada e salva!")
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")

print("Processo concluído!")


