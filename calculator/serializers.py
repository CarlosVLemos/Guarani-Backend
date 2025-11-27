from rest_framework import serializers

class MetricsSerializer(serializers.Serializer):
    test_mae = serializers.FloatField()
    test_rmse = serializers.FloatField()
    test_mape = serializers.FloatField()
    test_r2 = serializers.FloatField()
    train_mae = serializers.FloatField()

class ChartDataSerializer(serializers.Serializer):
    test_dates = serializers.ListField(child=serializers.CharField())
    actual_prices = serializers.ListField(child=serializers.FloatField())
    predicted_prices = serializers.ListField(child=serializers.FloatField())

class TrainModelResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    metrics = MetricsSerializer()
    analysis = serializers.CharField()
    chart_data = ChartDataSerializer()

class PredictionSerializer(serializers.Serializer):
    date = serializers.CharField()
    predicted_price = serializers.FloatField()

class PredictPricesResponseSerializer(serializers.Serializer):
    predictions = serializers.ListField(child=PredictionSerializer())