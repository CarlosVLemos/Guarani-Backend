import os
import pandas as pd
import xgboost as xgb
import yfinance as yf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from joblib import dump, load
from django.conf import settings
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

DATA_DIR = os.path.join(settings.BASE_DIR, 'calculator', 'data')
CBIO_FILE_PATH = os.path.join(DATA_DIR, 'cbio_corrigido_final.csv')
AGRO_FILE_PATH = os.path.join(DATA_DIR, 'agro_final_pronto.csv')
AGRO_FALLBACK_PATH = os.path.join(DATA_DIR, 'CEPEAcsv.csv')
MODEL_FILE_PATH = os.path.join(DATA_DIR, 'cbio_prediction_model.joblib')
MODEL_FEATURES_PATH = os.path.join(DATA_DIR, 'model_features.joblib')

class DataLoader:
    """Responsável por carregar e processar dados de diferentes fontes"""
    
    def __init__(self):
        self.cbio_data = None
        self.agro_data = None
        self.macro_data = None
    
    def load_cbio(self, file_path):
        try:
            df = pd.read_csv(file_path)
            date_column, price_column = df.columns[0], df.columns[1]
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.set_index(date_column).sort_index()
            self.cbio_data = df.rename(columns={price_column: 'Preco_CBIO'})
            print(f"DEBUG: Dados CBIO carregados com sucesso. Shape: {self.cbio_data.shape}")
            return self.cbio_data
        except Exception as e:
            raise Exception(f"Erro ao carregar dados CBIO: {e}")
    
    def load_agro(self, file_path, fallback_path=None):
        try:
            df = pd.read_csv(file_path)
            date_column = df.columns[0]
            df[date_column] = pd.to_datetime(df[date_column])
            self.agro_data = df.set_index(date_column).sort_index()
            print(f"DEBUG: Dados agro carregados com sucesso. Shape: {self.agro_data.shape}")
            return self.agro_data
        except Exception as e:
            if fallback_path:
                return self._load_agro_fallback(fallback_path)
            raise Exception(f"Erro ao carregar dados de etanol: {e}")

    def _load_agro_fallback(self, file_path):
        try:
            df = pd.read_csv(file_path, skiprows=3, encoding='latin1').iloc[:, 0:2]
            df.columns = ['Data', 'Preco_Etanol']
            df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            self.agro_data = df.set_index('Data').resample('D').ffill()
            print(f"DEBUG: Dados agro fallback carregados com sucesso. Shape: {self.agro_data.shape}")
            return self.agro_data
        except Exception as e:
            raise Exception(f"Erro ao carregar dados brutos de etanol: {e}")
    
    def load_macro_data(self, tickers, start_date, end_date):
        try:
            df = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
            df.columns = ['Dolar', 'Petroleo']
            self.macro_data = df.ffill().bfill()
            print(f"DEBUG: Dados macroeconômicos carregados com sucesso. Shape: {self.macro_data.shape}")
            return self.macro_data
        except Exception as e:
            raise Exception(f"Erro ao carregar dados macroeconômicos: {e}")

class FeatureEngineering:
    """Responsável pela criação de features para o modelo"""
    
    def create_lag_features(df, target_column, lag_periods):
        for period in lag_periods:
            df[f'Lag_{period}'] = df[target_column].shift(period)
        return df
    
    def prepare_features(df, target_column, lag_periods):
        df_copy = df.copy()
        df_copy = FeatureEngineering.create_lag_features(df_copy, target_column, lag_periods)
        return df_copy.dropna()

class CBIOPredictionModel:
    """Modelo de previsão de preços de CBIO usando XGBoost"""
    
    def __init__(self, model_params=None):
        self.model_params = model_params or {}
        self.model = xgb.XGBRegressor(**self.model_params)
        self.target_column = 'Preco_CBIO'
    
    def train(self, train_data, feature_columns):
        X_train = train_data[feature_columns]
        y_train = train_data[self.target_column]
        self.model.fit(X_train, y_train)
        return self.model
    
    def predict(self, test_data, feature_columns):
        if self.model is None:
            raise Exception("Modelo não treinado.")
        
        X_test = test_data[feature_columns]
        return self.model.predict(X_test)

def train_and_save_model():
    """
    Executa o pipeline completo de treinamento e salva o modelo treinado no disco.
    """
    print("Iniciando pipeline de treinamento do modelo CBIO...")
    
    LAG_PERIODS = [1, 5, 21]
    YAHOO_TICKERS = ['BZ=F', 'BRL=X']
    TRAIN_TEST_SPLIT_DAYS = 120
    XGBOOST_PARAMS = {'n_estimators': 1000, 'learning_rate': 0.02, 'max_depth': 5}

    data_loader = DataLoader()
    cbio_df = data_loader.load_cbio(CBIO_FILE_PATH)
    agro_df = data_loader.load_agro(AGRO_FILE_PATH, AGRO_FALLBACK_PATH)
    macro_df = data_loader.load_macro_data(YAHOO_TICKERS, cbio_df.index.min(), cbio_df.index.max())
    
    merged_data = cbio_df.join(agro_df).join(macro_df).ffill().bfill()
    print(f"DEBUG: Dados mesclados. Shape: {merged_data.shape}")
    
    processed_data = FeatureEngineering.prepare_features(merged_data, 'Preco_CBIO', LAG_PERIODS)
    print(f"DEBUG: Dados processados com features. Shape: {processed_data.shape}")
    
    train_data = processed_data.iloc[:-TRAIN_TEST_SPLIT_DAYS]
    test_data = processed_data.iloc[-TRAIN_TEST_SPLIT_DAYS:]
    
    feature_columns = [col for col in processed_data.columns if col != 'Preco_CBIO']
    
    print(f"Treinando modelo com {len(feature_columns)} variáveis...")
    prediction_model = CBIOPredictionModel(XGBOOST_PARAMS)
    trained_xgb_model = prediction_model.train(train_data, feature_columns)
    
    dump(trained_xgb_model, MODEL_FILE_PATH)
    dump(feature_columns, MODEL_FEATURES_PATH)
    print(f"Modelo salvo em: {MODEL_FILE_PATH}")
    
    predictions = prediction_model.predict(test_data, feature_columns)
    mae = mean_absolute_error(test_data['Preco_CBIO'], predictions)
    rmse = np.sqrt(mean_squared_error(test_data['Preco_CBIO'], predictions))
    mape = (mae / test_data['Preco_CBIO'].mean()) * 100
    r2 = r2_score(test_data['Preco_CBIO'], predictions)
    
    # Avaliação no conjunto de treinamento para verificar overfitting
    train_predictions = prediction_model.predict(train_data, feature_columns)
    train_mae = mean_absolute_error(train_data['Preco_CBIO'], train_predictions)
    
    print(f"Treinamento concluído.")
    print(f"Conjunto de Teste - MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%, R²: {r2:.4f}")
    print(f"Conjunto de Treino - MAE: {train_mae:.2f}")
    
    # Análise dos resultados
    analysis = "Modelo treinado com sucesso. "
    if r2 > 0.7:
        analysis += "R² alto indica bom ajuste aos dados. "
    elif r2 > 0.5:
        analysis += "R² moderado, modelo razoável. "
    else:
        analysis += "R² baixo, considere melhorar o modelo. "
    
    if mape < 10:
        analysis += "MAPE baixo indica previsões precisas. "
    else:
        analysis += "MAPE alto, previsões menos precisas. "
    
    if train_mae * 1.5 < mae:
        analysis += "Possível overfitting detectado."
    elif mae * 1.5 < train_mae:
        analysis += "Possível underfitting."
    else:
        analysis += "Modelo bem balanceado."
    
    print(f"Análise: {analysis}")
    print(f"DEBUG: Primeiras 5 previsões no teste: {predictions[:5]}")
    
    return {
        "status": "success",
        "metrics": {
            "test_mae": round(mae, 2),
            "test_rmse": round(rmse, 2),
            "test_mape": round(mape, 2),
            "test_r2": round(r2, 4),
            "train_mae": round(train_mae, 2)
        },
        "analysis": analysis,
        "chart_data": {
            "test_dates": test_data.index.strftime('%Y-%m-%d').tolist(),
            "actual_prices": test_data['Preco_CBIO'].round(2).tolist(),
            "predicted_prices": predictions.round(2).tolist()
        }
    }

def get_prediction(days_to_predict=30):
    """
    Carrega o modelo treinado e faz uma previsão para o futuro.
    """
    try:
        model = load(MODEL_FILE_PATH)
        feature_columns = load(MODEL_FEATURES_PATH)
    except FileNotFoundError:
        raise Exception("Modelo não encontrado. Execute o comando de treinamento primeiro.")

    LAG_PERIODS = [1, 5, 21]
    YAHOO_TICKERS = ['BZ=F', 'BRL=X']

    data_loader = DataLoader()
    cbio_df = data_loader.load_cbio(CBIO_FILE_PATH)
    end_date = cbio_df.index.max()
    start_date = end_date - pd.DateOffset(days=max(LAG_PERIODS) + 5)
    
    cbio_recent = cbio_df.loc[start_date:]
    agro_df = data_loader.load_agro(AGRO_FILE_PATH, AGRO_FALLBACK_PATH)
    agro_recent = agro_df.loc[start_date:]
    macro_df = data_loader.load_macro_data(YAHOO_TICKERS, start_date, end_date + pd.DateOffset(days=1))

    last_known_date = cbio_recent.index.max()
    future_dates = pd.to_datetime([last_known_date + pd.DateOffset(days=i) for i in range(1, days_to_predict + 1)])
    prediction_df = pd.DataFrame(index=future_dates)

    full_df = pd.concat([cbio_recent, prediction_df])
    full_df = full_df.join(agro_recent).join(macro_df).ffill()
    
    full_df = FeatureEngineering.prepare_features(full_df, 'Preco_CBIO', LAG_PERIODS)
    
    data_to_predict = full_df.loc[future_dates].dropna()

    if data_to_predict.empty:
        return {"error": "Não foi possível gerar dados suficientes para a previsão. Verifique as fontes de dados."}

    predicted_prices = model.predict(data_to_predict[feature_columns])
    
    result = {
        "predictions": [
            {"date": date.strftime('%Y-%m-%d'), "predicted_price": round(price, 2)}
            for date, price in zip(data_to_predict.index, predicted_prices)
        ]
    }
    
    print(f"DEBUG: Previsões geradas: {len(result['predictions'])} dias")
    print(f"DEBUG: Primeiras 5 previsões: {result['predictions'][:5]}")
    
    return result