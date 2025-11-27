from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import train_and_save_model, get_prediction
from .serializers import TrainModelResponseSerializer, PredictPricesResponseSerializer

@api_view(['POST'])
def train_model_view(request):
    """
    Treina o modelo de previsão de preços de CBIO.
    
    Retorna métricas de performance, análise e dados para gráficos.
    """
    try:
        result = train_and_save_model()
        serializer = TrainModelResponseSerializer(data=result)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def predict_prices_view(request):
    """
    Obtém previsões de preços de CBIO.
    
    Parâmetros de query:
    - days: número de dias para prever (padrão: 30)
    """
    try:
        days = int(request.query_params.get('days', 30))
        result = get_prediction(days_to_predict=days)
        serializer = PredictPricesResponseSerializer(data=result)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
