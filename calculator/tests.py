import json
from django.test import SimpleTestCase
from django.urls import reverse
from unittest.mock import patch

class CalculatorViewsTest(SimpleTestCase):
    @patch('calculator.services.train_and_save_model')
    def test_train_model_view_success(self, mock_train):
        mock_train.return_value = {
            "status": "success",
            "metrics": {
                "test_mae": 1.5,
                "test_rmse": 2.0,
                "test_mape": 1.2,
                "test_r2": 0.85,
                "train_mae": 1.0
            },
            "analysis": "Modelo treinado com sucesso. R² alto indica bom ajuste aos dados. MAPE baixo indica previsões precisas. Modelo bem balanceado.",
            "chart_data": {
                "test_dates": ["2023-01-01", "2023-01-02"],
                "actual_prices": [100.0, 101.0],
                "predicted_prices": [101.5, 102.0]
            }
        }

        response = self.client.post(reverse('train_model'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Train Model Success Response: {data}")
        self.assertEqual(data['status'], 'success')
        self.assertIn('metrics', data)
        self.assertIn('analysis', data)
        self.assertIn('chart_data', data)
        self.assertEqual(data['metrics']['test_mae'], 1.5)

    @patch('calculator.views.train_and_save_model')
    def test_train_model_view_error(self, mock_train):
        mock_train.side_effect = Exception("Erro de teste")

        response = self.client.post(reverse('train_model'))
        self.assertEqual(response.status_code, 500)
        data = response.json()
        print(f"Train Model Error Response: {data}")
        self.assertIn('error', data)

    @patch('calculator.views.get_prediction')
    def test_predict_prices_view_success(self, mock_predict):
        mock_predict.return_value = {
            "predictions": [
                {"date": "2023-01-01", "predicted_price": 100.5},
                {"date": "2023-01-02", "predicted_price": 101.0}
            ]
        }

        response = self.client.get(reverse('predict_prices'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Predict Prices Success Response: {data}")
        self.assertIn('predictions', data)
        self.assertEqual(len(data['predictions']), 2)

    @patch('calculator.views.get_prediction')
    def test_predict_prices_view_with_days_param(self, mock_predict):
        mock_predict.return_value = {"predictions": []}

        response = self.client.get(reverse('predict_prices'), {'days': '10'})
        self.assertEqual(response.status_code, 200)
        print(f"Predict Prices with Days Response: {response.json()}")
        mock_predict.assert_called_once_with(days_to_predict=10)

    @patch('calculator.views.get_prediction')
    def test_predict_prices_view_error(self, mock_predict):
        mock_predict.side_effect = Exception("Erro na previsão")

        response = self.client.get(reverse('predict_prices'))
        self.assertEqual(response.status_code, 500)
        data = response.json()
        print(f"Predict Prices Error Response: {data}")
        self.assertIn('error', data)
