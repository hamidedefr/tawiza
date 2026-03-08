# Docker ROCm 7.1 Training - Guide Rapide

## 🚀 Lancement Rapide

```bash
# Lancer le fine-tuning complet (build + train)
./scripts/train_docker_rocm.sh
```

C'est tout ! Le script va :
1. ✅ Vérifier Docker et GPU
2. ✅ Construire l'image Docker avec ROCm 7.1
3. ✅ Démarrer le conteneur
4. ✅ Vérifier l'accès GPU
5. ✅ Lancer le fine-tuning

## 🆕 Nouveautés ROCm 7.1

- **Performance**: 3.5x meilleure performance d'inférence vs ROCm 6
- **PyTorch 2.7**: Support PyTorch 2.7 avec optimisations ROCm
- **Support GPU**: Radeon RX 7900 XTX (gfx1100) entièrement supporté
- **Nouveaux types de données**: FP4, FP6, FP8 pour l'optimisation

---

## 📦 Structure

```
docker/
├── Dockerfile.rocm-training          # Image ROCm + PyTorch + LLaMA-Factory
├── docker-compose.rocm-training.yml  # Configuration du conteneur
├── training_logs/                    # Logs d'entraînement
└── README_DOCKER_ROCM.md            # Ce fichier
```

---

## 🔧 Commandes Utiles

### Gestion du Conteneur

```bash
cd docker/

# Démarrer
docker-compose -f docker-compose.rocm-training.yml up -d

# Arrêter
docker-compose -f docker-compose.rocm-training.yml down

# Voir logs
docker-compose -f docker-compose.rocm-training.yml logs -f

# Accéder au shell
docker-compose -f docker-compose.rocm-training.yml exec mptoo-training bash
```

### Monitoring GPU

```bash
# Dans le conteneur
docker-compose -f docker-compose.rocm-training.yml exec mptoo-training rocm-smi

# Host
watch -n 1 'docker exec mptoo-training-rocm rocm-smi'
```

### Vérifier PyTorch + GPU

```bash
docker-compose -f docker-compose.rocm-training.yml exec mptoo-training python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'GPU Available: {torch.cuda.is_available()}')
print(f'GPU Name: {torch.cuda.get_device_name(0)}')
"
```

---

## 📊 Fine-Tuning Manuel

```bash
# Accéder au conteneur
docker-compose -f docker-compose.rocm-training.yml exec mptoo-training bash

# Lancer l'entraînement
cd /workspace
llamafactory-cli train configs/finetune_mptoo_assistant_qwen_amd.yaml

# Suivre les logs
tail -f output/mptoo_assistant_qwen_lora/trainer_log.jsonl
```

---

## 📤 Exporter le Modèle

```bash
# Dans le conteneur
docker-compose -f docker-compose.rocm-training.yml exec mptoo-training \
  llamafactory-cli export output/mptoo_assistant_qwen_lora \
  --export_dir /workspace/exported_model

# Copier vers l'hôte
docker cp mptoo-training-rocm:/workspace/exported_model ./exported_model

# Créer le modèle Ollama (sur l'hôte)
cat > Modelfile << 'EOF'
FROM ./exported_model
PARAMETER temperature 0.7
SYSTEM """Vous êtes l'assistant MPtoO expert."""
EOF

ollama create mptoo-assistant -f Modelfile
```

---

## 🐛 Troubleshooting

### GPU Non Détecté

```bash
# Vérifier les devices
ls -la /dev/kfd /dev/dri/render*

# Vérifier les groupes
groups
# Doit contenir: video, render

# Ajouter au groupe si nécessaire
sudo usermod -aG video,render $USER
# Puis déconnexion/reconnexion
```

### Rebuild de l'Image

```bash
# Rebuild complet
docker-compose -f docker-compose.rocm-training.yml build --no-cache

# Rebuild et redémarrer
docker-compose -f docker-compose.rocm-training.yml up -d --build
```

### Espace Disque

```bash
# Nettoyer les images inutilisées
docker system prune -a

# Voir l'espace utilisé
docker system df
```

---

## 📝 Configuration GPU

Pour votre **RX 7900 XTX** (gfx1100), la configuration est déjà correcte dans :
- `Dockerfile.rocm-training`: `ENV HSA_OVERRIDE_GFX_VERSION=11.0.0`
- `docker-compose.rocm-training.yml`: `HSA_OVERRIDE_GFX_VERSION=11.0.0`

Si vous avez un autre GPU:
| GPU | GFX Version | HSA_OVERRIDE |
|-----|-------------|--------------|
| RX 6700 XT | gfx1031 | 10.3.1 |
| RX 6800/6900 XT | gfx1030 | 10.3.0 |
| RX 7900 XTX | gfx1100 | 11.0.0 |

---

## 🎯 Flux Complet

```bash
# 1. Lancer le training
./scripts/train_docker_rocm.sh

# 2. Attendre la fin (~10-15 min)
# Surveiller avec: docker-compose -f docker/docker-compose.rocm-training.yml logs -f

# 3. Exporter
docker-compose -f docker/docker-compose.rocm-training.yml exec mptoo-training \
  llamafactory-cli export output/mptoo_assistant_qwen_lora --export_dir /workspace/exported_model

# 4. Copier
docker cp mptoo-training-rocm:/workspace/exported_model ./exported_model

# 5. Créer Ollama
ollama create mptoo-assistant -f Modelfile

# 6. Tester
mptoo assistant start --model mptoo-assistant

# 7. Nettoyer (optionnel)
docker-compose -f docker/docker-compose.rocm-training.yml down
```

---

## 📈 Avantages Docker

✅ **Isolation**: Pas de conflit avec l'environnement hôte
✅ **ROCm pré-configuré**: Tout fonctionne out-of-the-box
✅ **Reproductible**: Même environnement partout
✅ **Facile à nettoyer**: `docker-compose down`
✅ **Accès GPU**: Automatiquement configuré

---

## 🔗 Resources

- **ROCm Version**: 7.1.0 (stable)
- **PyTorch**: 2.7.0 with ROCm 6.3 backend
- **Base Image**: Ubuntu 24.04 LTS
- **Python**: 3.12
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory
- ROCm 7.1 Docs: https://rocm.docs.amd.com/
- ROCm 7.0 Release Notes: https://www.amd.com/en/developer/resources/technical-articles/2025/amd-rocm-7-built-for-developers-ready-for-enterprises.html

## 🔧 Version Details

| Component | Version | Notes |
|-----------|---------|-------|
| ROCm | 7.1.0 | Latest stable release |
| PyTorch | 2.7.0 | With ROCm support |
| Python | 3.12 | Ubuntu 24.04 default |
| CUDA API | HIP 7.1 | ROCm's CUDA compatibility layer |
| GPU | RX 7900 XTX | gfx1100 architecture |

## 🚀 Performance Improvements (ROCm 7.1 vs 6.2)

- **3.5x faster inference** for LLM workloads
- **3x faster training** compared to ROCm 6
- Better memory efficiency with FP8 support
- Improved PyTorch integration
