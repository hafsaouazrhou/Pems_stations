# PeMSD7 Traffic Stations – Docker Application

Application complète en conteneur Docker unique qui :
1. **Charge** le dataset CSV PeMSD7 (228 stations, District 7 Californie)
2. **Sauvegarde** les localisations et métriques dans **MongoDB**
3. **Récupère** les données de la base et les **affiche sur une carte interactive** (Leaflet.js)

---

## 📁 Structure du projet

```
pemsd7-app/
├── Dockerfile            ← Image Docker (MongoDB + Flask dans un seul conteneur)
├── supervisord.conf      ← Lance mongod + flask en parallèle
├── requirements.txt      ← Flask, PyMongo
├── app.py                ← Backend Flask (API REST)
├── templates/
│   └── index.html        ← Frontend carte interactive
├── data/
│   └── PeMSD7_stations.csv  ← Dataset (228 stations)
└── README.md
```

---

## 🚀 Build & Run (Dockerfile seul, pas de docker-compose)

### 1. Build l'image
```bash
docker build -t pemsd7-app .
```

### 2. Lancer le conteneur
```bash
docker run -d -p 5000:5000 --name pemsd7 pemsd7-app
```

### 3. Ouvrir l'application
Aller sur : **http://localhost:5000**

L'application charge automatiquement le CSV dans MongoDB au démarrage.

---

## 🌐 Interface Web

| Fonctionnalité | Description |
|---|---|
| **Carte Leaflet sombre** | Affiche les 228 stations avec clustering automatique |
| **Couleur des marqueurs** | Rouge (<45 mph) · Orange (45–60) · Vert (>60) |
| **Popups** | Clic sur un marqueur → ID, autoroute, vitesse, débit, occupancy… |
| **Filtres** | Par autoroute (I-5, US-101…), direction (N/S/E/W), vitesse minimale |
| **Import CSV** | Bouton pour ré-importer le CSV dans MongoDB |
| **Stats sidebar** | Total stations, répartition par autoroute |
| **Liste stations** | Liste cliquable avec fly-to sur la carte |

---

## 🔌 API REST

| Endpoint | Méthode | Description |
|---|---|---|
| `GET /` | GET | Interface web |
| `POST /api/import` | POST | Importe le CSV dans MongoDB |
| `GET /api/stations` | GET | Récupère toutes les stations (filtres optionnels) |
| `GET /api/stats` | GET | Statistiques agrégées |
| `GET /api/freeways` | GET | Liste des autoroutes disponibles |

### Paramètres de `/api/stations` :
- `freeway` : ex. `I-405`
- `direction` : `N`, `S`, `E`, `W`
- `min_speed` : vitesse minimale en mph
- `max_speed` : vitesse maximale en mph

---

## 📊 Dataset PeMSD7

> Le dataset original PeMSD7 nécessite un compte Caltrans (https://pems.dot.ca.gov).
> Ce projet inclut un CSV **simulé réaliste** de 228 stations District 7.

### Si vous voulez utiliser le vrai dataset :
1. Créer un compte sur https://pems.dot.ca.gov
2. Aller dans **Data Clearinghouse → Station Metadata → District 7**
3. Exporter en CSV
4. Remplacer `data/PeMSD7_stations.csv` en respectant les colonnes :
   ```
   station_id, freeway, direction, abs_postmile,
   latitude, longitude, lanes, avg_speed_mph, avg_flow_vph, avg_occupancy
   ```

---

## 🛑 Arrêter / Supprimer

```bash
docker stop pemsd7
docker rm pemsd7
docker rmi pemsd7-app   # supprimer l'image
```

## 📦 Persister les données MongoDB

```bash
docker run -d -p 5000:5000 \
  -v pemsd7_data:/data/db \
  --name pemsd7 pemsd7-app
```

---

## ⚙️ Technologies

- **Backend** : Python 3.11, Flask 3.0, PyMongo 4.7
- **Base de données** : MongoDB 7 (Community)
- **Frontend** : Leaflet.js 1.9, Leaflet.MarkerCluster
- **Tiles** : CartoDB Dark Matter
- **Process manager** : Supervisord (dans le conteneur)
