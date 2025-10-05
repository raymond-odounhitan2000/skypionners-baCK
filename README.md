## Comparaison des modèles de prévision PM2.5 (RandomForest vs XGBoost)

Ce projet contient deux familles de modèles entraînés pour prédire la concentration
de PM2.5 à l'horizon court : 10 minutes et 30 minutes. Les modèles et scalers
sont sauvegardés dans le dossier `models/`.

Résumé des métriques (MAE, RMSE) et artéfacts :

- Horizon 10 minutes
	- RandomForest (RF)
		- MAE: 0.2183
		- RMSE: 0.3482
		- Modèle: `models/pm25_model_h10m.joblib`
		- Scaler: `models/pm25_scaler_h10m.joblib`
	- XGBoost (XGB)
		- Best params (GridSearch): `{'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100}`
		- CV best MAE: 0.49996
		- Test MAE: 0.26737
		- Test RMSE: 0.39341
		- Modèle final: `models/pm25_xgb_h10m.joblib`
		- Scaler: `models/pm25_xgb_scaler_h10m.joblib`

- Horizon 30 minutes
	- RandomForest (RF)
		- MAE: 0.6070
		- RMSE: 0.9040
		- Modèle: `models/pm25_model_h30m.joblib`
		- Scaler: `models/pm25_scaler_h30m.joblib`
	- XGBoost (XGB)
		- Best params (GridSearch): `{'learning_rate': 0.1, 'max_depth': 6, 'n_estimators': 100}`
		- CV best MAE: 1.23620
		- Test MAE: 0.72594
		- Test RMSE: 1.02892
		- Modèle final: `models/pm25_xgb_h30m.joblib`
		- Scaler: `models/pm25_xgb_scaler_h30m.joblib`

Interprétation rapide
- Pour l'horizon très court (10 min), RandomForest obtient une erreur légèrement
	inférieure que XGBoost sur le test (MAE=0.218 vs 0.267). Cela peut venir du
	fait que RF est très robuste et que le signal horaire est fort pour 10 minutes.
- Pour l'horizon 30 min, RF a aussi une MAE inférieure que XGBoost sur le test (0.607 vs 0.726).
	Les différences suggèrent qu'avec la grille testée XGBoost n'a pas encore surpassé
	RandomForest. Il est possible que l'élargissement de la grille, l'ingénierie
	des features (ex: variables météo supplémentaires, tendances glissantes), ou
	l'usage d'un CV temporel plus fin améliore les performances de XGBoost.

Recommandations
- Étendre la grille d'hyperparamètres ou utiliser RandomizedSearchCV pour XGBoost.
- Essayer LightGBM (souvent plus rapide) et comparer.
- Ajouter des features supplémentaires (météo, vents, topographie) si disponibles.
- Mettre en place une validation temporelle (rolling-window) pour une évaluation plus robuste.

Si vous voulez, je peux :
- Générer un rapport CSV/JSON comparatif détaillé.
- Lancer une recherche d'hyperparamètres étendue (ou RandomizedSearchCV).
- Intégrer le modèle choisi dans une API FastAPI pour prédiction en temps réel.
