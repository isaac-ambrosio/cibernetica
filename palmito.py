########### Redimensionar somente as imagens que foram rotuladas ######################

import os
from PIL import Image

# Caminho da pasta de entrada (onde estão as imagens originais)
pasta_origem = "/content/drive/MyDrive/cibernetica/Proj2/Palmito"  # Substitua pelo caminho correto

# Caminho da pasta de saída (onde serão salvas as imagens redimensionadas)
pasta_saida = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/imagens_red"

# Caminho da pasta com os labels
pasta_labels = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/labels"

os.makedirs(pasta_saida, exist_ok=True)


# 📝 Obter lista de arquivos .txt (sem extensão)
arquivos_rotulados = {
    os.path.splitext(arquivo)[0] for arquivo in os.listdir(pasta_labels) if arquivo.endswith(".txt")
}


# Dimensão desejada
nova_largura = 640
nova_altura = 640

# 📷 Processar imagens correspondentes
for arquivo in os.listdir(pasta_origem):
    if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
        nome_base = os.path.splitext(arquivo)[0]

        # 📌 Processar apenas se houver rótulo correspondente
        if nome_base in arquivos_rotulados:
            try:
                img = Image.open(os.path.join(pasta_origem, arquivo))
                img = img.resize((nova_largura, nova_altura), Image.LANCZOS)

                caminho_saida = os.path.join(pasta_saida, arquivo[-9:])
                img.save(caminho_saida)

                print(f"Imagem {arquivo[-9:]} redimensionada e salva!")
            except Exception as e:
                print(f"Imagem {arquivo} não rotulada")

print("Processo concluído!")

################# Distribuir as imagens para treinamento e teste ######################

import os
import random

# 📌 Defina o caminho da pasta e o arquivo de saída
pasta_origem = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/imagens_red"  # Altere para o caminho correto
arquivo_saida = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/img_list/lista_arquivos.txt"  # Nome do arquivo de saída

train = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/img_list/train.txt"
val = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/img_list/val.txt"
test = "/content/drive/MyDrive/cibernetica/Proj2/Palmito/img_list/test.txt"


# 📌 Obter a lista de arquivos na pasta
arquivos = os.listdir(pasta_origem)

# 🔄 Embaralhar a lista de arquivos aleatoriamente
random.shuffle(arquivos)

# 📌 Salvar a lista embaralhada em um arquivo .txt
with open(arquivo_saida, "w") as f:
    for arquivo in arquivos:
        f.write(arquivo + "\n")


# 📊 Definir os índices para divisão, 60% para train, 20% para val e 20% test
total = len(arquivos)
train_limite = int(total * 0.6)
val_limite = int(total * 0.8)

train_files = arquivos[:train_limite]
val_files = arquivos[train_limite:val_limite]
test_files = arquivos[val_limite:]


# 💾 Função para salvar arquivos
def salvar_lista(caminho, lista):
    with open(caminho, "w") as f:
        for arquivo in lista:
            f.write(arquivo + "\n")

# 📂 Salvar em train, val e test
salvar_lista(train, train_files)
salvar_lista(val, val_files)
salvar_lista(test, test_files)


print(f"✅ Lista de arquivos aleatória salva em: {arquivo_saida}")

########################## Converter os dados de YOLO para COCO #####################################

import os
import shutil
import json
from PIL import Image

# Caminhos das pastas
base_dir = '/content/drive/MyDrive/cibernetica/Proj2/Palmito'
images_dir = os.path.join(base_dir, 'imagens_red')
annotations_dir = os.path.join(base_dir, 'labels_coco')
img_list_dir = os.path.join(base_dir, 'img_list')

# Novos diretórios
output_dir = '/content/drive/MyDrive/cibernetica/RT-DETR/rtdetr_pytorch/configs/dataset'
output_images_dir = os.path.join(output_dir, 'images')
output_annotations_dir = os.path.join(output_dir, 'annotations')

# Garantir que os diretórios de saída existem
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_annotations_dir, exist_ok=True)

# Função para processar um conjunto (train, val ou test)
def process_set(set_name, verbose=True):
    # Criar diretório para as imagens do conjunto
    set_images_dir = os.path.join(output_images_dir, set_name)
    os.makedirs(set_images_dir, exist_ok=True)

    # Ler a lista de imagens
    set_list_file = os.path.join(img_list_dir, f'{set_name}.txt')
    if verbose:
        print(f"Processando conjunto '{set_name}'...")

    with open(set_list_file, 'r') as f:
        image_files = [line.strip() for line in f.readlines()]

    images = []
    annotations = []
    annotation_id = 1  # ID único para cada anotação
    for image_id, image_file in enumerate(image_files, 1):
        # Copiar a imagem para o diretório correspondente
        src_image_path = os.path.join(images_dir, image_file)
        dst_image_path = os.path.join(set_images_dir, image_file)
        shutil.copyfile(src_image_path, dst_image_path)
        if verbose:
            print(f"Copiando imagem '{image_file}': de {src_image_path} para {dst_image_path} ...")

        # Obter as dimensões da imagem
        with Image.open(src_image_path) as img:
            width, height = img.size
            if verbose:
                print(f"Dimensões da imagem '{image_file}': {width}x{height}")

        # Adicionar entrada para a imagem
        images.append({
            'id': image_id,
            'file_name': image_file,
            'width': width,
            'height': height
        })

        # Ler o arquivo de anotações correspondente
        annotation_file = os.path.splitext(image_file)[0] + '.txt'
        annotation_path = os.path.join(annotations_dir, annotation_file)
        if os.path.exists(annotation_path):
            with open(annotation_path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) != 5:
                    print(f"Aviso: Formato inválido na linha '{line}' do arquivo '{annotation_path}'.")
                    continue

                try:
                    x_centro, y_centro, w, h = map(float, parts[1:])

                except ValueError:
                    print(f"Aviso: Valores não numéricos na linha '{line}' do arquivo '{annotation_path}'.")
                    continue
                # Converter para coordenadas absolutas em pixels
                x_min = int((x_centro - w / 2) * width)
                y_min = int((y_centro - h / 2) * height)
                x_max = int((x_centro + w / 2) * width)
                y_max = int((y_centro + h / 2) * height)

                # Garantir que as coordenadas estão dentro dos limites da imagem
                x_min = max(0, min(x_min, width - 1))
                y_min = max(0, min(y_min, height - 1))
                x_max = max(0, min(x_max, width - 1))
                y_max = max(0, min(y_max, height - 1))

                bbox_width = x_max - x_min
                bbox_height = y_max - y_min

                if bbox_width <= 0 or bbox_height <= 0:
                    print(f"Aviso: BBox com largura ou altura zero na imagem '{image_file}'.")
                    continue


                annotations.append({
                    'id': annotation_id,
                    'image_id': image_id,
                    'category_id': 0,  # ID da categoria (apenas uma classe)
                    'bbox': [x_min, y_min, bbox_width, bbox_height],
                    'area': bbox_width * bbox_height,
                    'iscrowd': 0

                })
                annotation_id += 1
        else:
            print(f"Aviso: Arquivo de anotação '{annotation_path}' não encontrado.")

    # Criar a estrutura final do JSON
    coco_format = {
        'images': images,
        'annotations': annotations,
        'categories': [
            {
                'id': 0,
                'name': 'Copa de Arvore',  # Nome da classe
                'supercategory': 'none'
            }
        ]
    }

    # Salvar o arquivo JSON
    json_file = os.path.join(output_annotations_dir, f'instances_{set_name}.json')
    with open(json_file, 'w') as f:
        json.dump(coco_format, f, indent=4)

    print(f"Processamento do conjunto '{set_name}' concluído. {len(images)} imagens e {len(annotations)} anotações processadas.")

# Processar os conjuntos de dados
for set_name in ['train', 'val', 'test']:
    process_set(set_name, verbose=False)


#### Requirements do RT DETR #####################


!pip install torch==2.0.1
!pip install torchvision==0.15.2
!pip install onnx==1.14.0
!pip install onnxruntime==1.15.1
!pip install pycocotools
!pip install PyYAML
!pip install scipy
