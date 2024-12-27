from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .db import (
    create_resource,
    get_resource,
    update_resource,
    delete_resource,
    get_all_resources,
    search_resources
)
from .serializers import ResourceSerializer
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

# Create your views here.

# Swagger.
@swagger_auto_schema(
    method='post',
    operation_summary="Create a new resource (Admin Only)",
    operation_description="Creates a new campus resource (admin only).",
    request_body=ResourceSerializer,
    responses={
        status.HTTP_201_CREATED: ResourceSerializer,
        status.HTTP_400_BAD_REQUEST: "Invalid input",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden (not an admin)",
    }
)

# API view for creating resource only admin.
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_resource_view(request):
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        try:
            resource_data = serializer.validated_data
            resource_id = create_resource(resource_data, str(request.user.id))
            if resource_id:
                return Response({"message": "Resource created", "resource_id": resource_id}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to create resource"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error in create_resource_view: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Swagger.
@swagger_auto_schema(
    method='get',
    operation_summary="Get a resource",
    manual_parameters=[
        openapi.Parameter('resource_id', openapi.IN_PATH, description="ID of the resource to retrieve", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: ResourceSerializer,
        status.HTTP_404_NOT_FOUND: "Resource not found",
    }
)

# API view for getting resource.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resource_view(request, resource_id):
    try:
        resource = get_resource(resource_id)
        if resource:
            serializer = ResourceSerializer(resource)
            return Response(serializer.data)
        else:
            return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_resource_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Swagger.
@swagger_auto_schema(
    method='put',
    operation_summary="Update a resource (Admin Only)",
    operation_description="Updates an existing campus resource (admin only).",
    manual_parameters=[
        openapi.Parameter('resource_id', openapi.IN_PATH, description="ID of the resource to update", type=openapi.TYPE_STRING, required=True),
    ],
    request_body=ResourceSerializer,
    responses={
        status.HTTP_200_OK: "Resource updated",
        status.HTTP_400_BAD_REQUEST: "Invalid input",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden (not an admin)",
        status.HTTP_404_NOT_FOUND: "Resource not found",
    }
)

# API view for update resource only admin.
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_resource_view(request, resource_id):
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        try:
            success = update_resource(resource_id, serializer.validated_data, str(request.user.id))
            if success:
                return Response({"message": "Resource updated"})
            else:
                return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in update_resource_view: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Swagger.
@swagger_auto_schema(
    method='delete',
    operation_summary="Delete a resource (Admin Only)",
    operation_description="Deletes a campus resource (admin only).",
    manual_parameters=[
        openapi.Parameter('resource_id', openapi.IN_PATH, description="ID of the resource to delete", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_204_NO_CONTENT: "Resource deleted",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden (not an admin)",
        status.HTTP_404_NOT_FOUND: "Resource not found",
    }
)

# API view for delete resource only admin.
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_resource_view(request, resource_id):
    try:
        success = delete_resource(resource_id, str(request.user.id))
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in delete_resource_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Swagger.
@swagger_auto_schema(
    method='get',
    operation_summary="Get all resources",
    operation_description="Retrieves a list of all campus resources.",
    responses={
        status.HTTP_200_OK: ResourceSerializer(many=True),
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# API view to get all resources.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_resources_view(request):
    try:
        resources = get_all_resources()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_all_resources_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Swagger.
@swagger_auto_schema(
    method='get',
    operation_summary="Search resources",
    operation_description="Searches for campus resources based on a query string.",
    manual_parameters=[
        openapi.Parameter('query', openapi.IN_QUERY, description="Search query string", type=openapi.TYPE_STRING, required=True),
    ],
    responses={
        status.HTTP_200_OK: ResourceSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    }
)

# API view for search resources.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_resources_view(request):
    query = request.query_params.get('query', '')
    try:
        resources = search_resources(query)
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in search_resources_view: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)