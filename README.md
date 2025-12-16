# Sistema de Clasificación Supervisada - Tier 1

Sistema modular de clasificación jerárquica de artículos usando BERT en español, diseñado para ejecutarse en Google Colab con capacidad de reentrenamiento incremental.

## 📋 Descripción

Este sistema clasifica artículos en dos niveles jerárquicos:
- **Nivel 1**: Categoría
- **Nivel 2**: Familia

Utiliza BERT pre-entrenado en español (`dccuchile/bert-base-spanish-wwm-uncased`) con restricciones jerárquicas para garantizar predicciones consistentes.

## 🏗️ Estructura del Proyecto

```
clasificacion_supervisada_tier_1/
├── config/
│   └── config.py              # Configuración central (paths, parámetros)
├── src/
│   ├── __init__.py
│   ├── preprocessing.py       # Limpieza y preparación de datos
│   ├── encoders.py           # Codificación de labels y jerarquías
│   ├── model.py              # Arquitectura del modelo BERT
│   ├── training.py           # Lógica de entrenamiento
│   ├── inference.py          # Predicciones y filtrado
│   └── utils.py              # Utilidades (versionado, I/O)
├── notebooks/
│   ├── 01_train_model.ipynb         # Entrenamiento inicial
│   ├── 02_retrain_model.ipynb       # Reentrenamiento incremental
│   └── 03_inference_pipeline.ipynb  # Pipeline de producción
├── data/
│   ├── raw/                  # Datos crudos
│   ├── processed/            # Datos procesados
│   └── dictionaries/         # Diccionarios y artifacts
├── models/                   # Modelos entrenados (.pth)
├── outputs/                  # Resultados CSV con timestamp
└── README.md
```

## 🚀 Flujo de Trabajo

### 1. Entrenamiento Inicial (`01_train_model.ipynb`)
1. Carga datos de entrenamiento (`train_data_v1.csv`)
2. Preprocesa y limpia texto (corpus)
3. Codifica labels jerárquicos
4. Entrena modelo BERT desde cero
5. Guarda:
   - `model_base.pth`
   - `codificador_base.pkl`
   - `class_weights_base.pth`
   - `hierarchy_map_base.json`

### 2. Reentrenamiento (`02_retrain_model.ipynb`)
1. Carga nueva data validada (`data_to_retrain.csv`)
2. Carga modelo y codificador existente
3. Reentrena con nueva data
4. Guarda versión incremental:
   - `model_retrain_v1.pth`, `model_retrain_v2.pth`, etc.
   - Artifacts correspondientes versionados

### 3. Inferencia en Producción (`03_inference_pipeline.ipynb`)
1. Carga datos mensuales (`datos_importacion_mensual.csv`)
2. Preprocesa con diccionario de aranceles
3. Realiza predicciones con restricciones jerárquicas
4. Aplica threshold de confianza (86%)
5. Genera outputs versionados:
   - `clasificacion_tier_1_YYYYMMDD_HHMMSS.csv` (≥ 86% confianza)
   - `articulos_no_clasificados_YYYYMMDD_HHMMSS.csv` (< 86% confianza)

## 🔧 Configuración para Colab

### Primera Celda en cada Notebook:

```python
import sys
IS_COLAB = 'google.colab' in sys.modules

if IS_COLAB:
    from google.colab import drive
    from config.config import Config
    
    config = Config(is_colab=True)
    config.setup_colab_environment()
else:
    from config.config import Config
    config = Config(is_colab=False)
```

### Estructura en Google Drive:

```
/content/drive/MyDrive/
└── clasificacion_2_niveles/
    └── laboratory_2/
        ├── config/
        ├── src/
        ├── notebooks/
        ├── data/
        ├── models/
        └── outputs/
```

## 📦 Dependencias

```python
# Colab ya incluye la mayoría, pero verifica:
torch>=1.10.0
transformers>=4.20.0
pandas>=1.3.0
scikit-learn>=1.0.0
nltk>=3.6
tqdm>=4.62.0
```

## 🎯 Parámetros Clave

Modificables en `config/config.py`:

```python
bert_model_name = "dccuchile/bert-base-spanish-wwm-uncased"
max_seq_length = 512
batch_size = 16
learning_rate = 2e-5
num_epochs = 3
classification_threshold = 0.86  # Threshold de confianza
```

## 📊 Versionado de Outputs

Todos los CSV de salida incluyen timestamp automático:
- `clasificacion_tier_1_20231215_143025.csv`
- `articulos_no_clasificados_20231215_143025.csv`

Los modelos reentrenados usan versionado incremental:
- `model_retrain_v1.pth`, `model_retrain_v2.pth`, etc.

## 🔄 Ciclo de Mejora Continua

```
Datos Mensuales
    ↓
Inferencia (03_inference_pipeline.ipynb)
    ↓
Filtrado por Threshold 86%
    ↓
├─→ Clasificados → Producción (clasificacion_tier_1.csv)
└─→ No Clasificados → Análisis Manual + Sugerencias AI
                      ↓
                Data Validada
                      ↓
            Reentrenamiento (02_retrain_model.ipynb)
                      ↓
                Nueva Versión del Modelo
```

## 📝 Archivos de Entrada Requeridos

### data/raw/
- `train_data_v1.csv`: Datos iniciales de entrenamiento
  - Columnas: `descripcion`, `cod_arancelario`, `nombre_categoria`, `familia`
- `dicaranceles.xlsx`: Diccionario de códigos arancelarios
  - Columnas: `Codigo`, `Descripcion`
- `datos_importacion_mensual.csv`: Datos para clasificar
- `data_to_retrain.csv`: Nueva data validada para reentrenar

### data/dictionaries/
- `stopwords_spanish.json`: Lista de stopwords
- `replacement_dict.json`: Diccionario de reemplazos de texto

## 🧠 Características del Modelo

### Arquitectura Jerárquica
- **Classifier Categoria**: BERT → Linear(768, N_categorias)
- **Classifier Familia**: BERT + Categoria → Linear(768+N_cat, N_familias)
- **Constraint Enforcement**: Masking de familias inválidas durante predicción

### Training
- Loss: CrossEntropy ponderado + Penalización jerárquica
- Optimizer: AdamW
- Dropout: 0.3 en capas de clasificación
- Class Weights: Balanceo automático por frecuencia

### Inference
- Predicción con restricciones jerárquicas
- Score de confianza: promedio de probabilidades
- Threshold configurable (default: 86%)

## 📖 Uso Rápido

### En Colab:

1. Monta Drive y carga el proyecto
2. Abre el notebook deseado
3. Ejecuta todas las celdas

### Localmente (desarrollo):

```python
from config.config import Config
config = Config(is_colab=False)

# Importar módulos
from src import get_data, preprocess_data, train_model
```

## ⚠️ Notas Importantes

- **Corpus**: Concatenación de descripción + descripción de arancel
- **Tokenización**: NLTK word_tokenize
- **Limpieza**: Lowercase, sin puntuación, sin números, filtrado de stopwords
- **GPU**: Detecta automáticamente CUDA si está disponible
- **Memory**: Batch size ajustable según GPU disponible

## 🐛 Troubleshooting

### Error: Codificador no encuentra clases nuevas
- **Solución**: Usar el codificador base siempre para reentrenar

### Error: CUDA out of memory
- **Solución**: Reducir `batch_size` en config.py

### CSV sin datos clasificados
- **Solución**: Revisar threshold (quizás muy alto), verificar modelo cargado

## 📄 Licencia

Proyecto interno - Todos los derechos reservados

## 👥 Contacto

Para dudas sobre el sistema, consultar con el equipo de Data Science.
