from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .db import get_courses_from_db
from .serializers import CourseSerializer
from .tasks import scrape_courses_and_recommend
from core.db import get_user
from django.http import JsonResponse
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

# Create your views here.

# Swagger.
@swagger_auto_schema(
    method='post',
    operation_summary="Scrape and recommend courses",
    operation_description="Triggers the scraping and recommendation process for a specific user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['search_terms'],
        properties={
            'search_terms': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="List of search terms for course scraping"),
        },
    ),
    responses={
        status.HTTP_202_ACCEPTED: "Course scraping and recommendation process initiated.",
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api View for scraping and recommend process for a specific user.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scrape_and_recommend_courses_view(request, user_id):
    if str(request.user.id) != user_id:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    search_terms = request.data.get('search_terms')
    if not search_terms or not isinstance(search_terms, list):
        return JsonResponse({"error": "Invalid or missing 'search_terms'"}, status=status.HTTP_400_BAD_REQUEST)
    scrape_courses_and_recommend.delay(user_id, search_terms)
    return Response({"message": "Course scraping and recommendation process initiated."}, status=status.HTTP_202_ACCEPTED)

# Swagger.
@swagger_auto_schema(
    method='get',
    operation_summary="Get recommended courses",
    operation_description="Retrieves recommended courses for a specific user.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: CourseSerializer(many=True),
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_404_NOT_FOUND: "User not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
    }
)

# Api view for recommend courses for a specific user.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommended_courses_view(request, user_id):
    if str(request.user.id) != user_id:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        recommended_courses = user.get('recommended_courses', [])
        serializer = CourseSerializer(recommended_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_recommended_courses_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)