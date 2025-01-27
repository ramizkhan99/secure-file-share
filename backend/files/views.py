from http import HTTPStatus
import secrets
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import os
import tempfile
import shutil
from django.conf import settings

from common.apiresponse import ApiResponse
from common.crypto import generate_encryption_key, store_encryption_key, encrypt_file, decrypt_file, CryptoError
from files.models import File, SharedFile
from .serializers import FileSerializer

@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def handle_file_requests(request):
    """ Handle file requests """
    if request.method == 'GET':
        if 'id' in request.query_params:
            return get_file(request, request.query_params.get('id'))
        return get_files_handler(request)
    elif request.method == 'POST':
        return post_file_handler(request)
    elif request.method == 'DELETE':
        return delete_file_handler(request)
    return ApiResponse(success=False, message='Invalid request method', status=HTTPStatus.BAD_REQUEST)

def get_files_handler(request):
    """ Get all the files """
    user = request.user
    if user.is_admin:
        files = File.objects.all()
    else:
        files = File.objects.filter(owner=user)
    serializer = FileSerializer(files, many=True)
    return ApiResponse(
            success=True,
            message='Files retrieved successfully',
            data=serializer.data
        )

def post_file_handler(request):
    """ Upload a file """
    file_serializer = FileSerializer(context={'request': request}, data=request.data)
    if file_serializer.is_valid():
        file_instance = file_serializer.save()
        key = generate_encryption_key()
        store_encryption_key(file_instance.id, key)  # Store the unique key for the file
        encrypt_file(file_instance.id, file_instance.file.path)  # Encrypt the file after saving
        return Response({'message': 'File uploaded successfully!'}, status=HTTPStatus.CREATED)
    else:
        return Response(file_serializer.errors, status=HTTPStatus.BAD_REQUEST)

def delete_file_handler(request):
    """ Delete a file """
    file_id = request.query_params.get('id')
    file = get_object_or_404(File, id=file_id)

    # Check if the user has permission to delete the file
    if not request.user.is_admin and file.owner != request.user:
        return ApiResponse(success=False, message='Permission denied', status=HTTPStatus.FORBIDDEN)

    try:
        # Get the file path before deleting the record
        file_path = file.file.path
        
        # Delete any associated shared files
        SharedFile.objects.filter(file=file).delete()
        
        # Delete the file record from database
        file.delete()
        
        # Delete the physical file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return ApiResponse(
            success=True, 
            message='File deleted successfully'
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f'Error deleting file: {str(e)}',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

def get_file(request, file_id):
    """ Get a file by ID """
    file = get_object_or_404(File, id=file_id)

    # Check if the user has permission to access the file
    if not request.user.is_admin and file.owner != request.user:
        return ApiResponse(success=False, message='Permission denied', status=HTTPStatus.FORBIDDEN)

    try:
        decrypt_file(file.id, file.file.path)  # Decrypt the file before sending
        response = FileResponse(open(file.file.path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response
    except FileNotFoundError:
        return ApiResponse(
            success=False,
            message='File not found',
            status=HTTPStatus.NOT_FOUND
        )
    finally:
        encrypt_file(file.id, file.file.path)  # Re-encrypt the file after sending

@api_view(['GET'])
@permission_classes([AllowAny])
def get_share_link(request):
    """ Get a shareable link for a file """
    file_id = request.query_params.get('id')
    file = get_object_or_404(File, id=file_id)

    # Check if the user has permission to share the file
    if not request.user.is_admin and file.owner != request.user:
        return ApiResponse(success=False, message='Permission denied', status=HTTPStatus.FORBIDDEN)

    # Create a new shared file entry
    share_hash = secrets.token_urlsafe(16)
    shared_file = SharedFile.objects.create(
        file=file,
        user=request.user,  # Associate the link with the user who created it
        share_hash=share_hash
    )
    if shared_file is None:
        return ApiResponse(
            success=False,
            message='Failed to generate share link',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )
    
    return ApiResponse(
        success=True,
        message='Share link generated successfully',
        data={'id': share_hash},
        status_code=HTTPStatus.CREATED
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_shared_file(request, file_id):
    """Retrieve a shared file using its ID."""
    try:
        shared_file = SharedFile.objects.get(share_hash=file_id)
        file = shared_file.file

        # Decrypt to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            # Decrypt the content directly to the temporary file
            decrypt_file(file.id, file.file.path, temp_output_path=temp_file_path)

            # Serve the decrypted file from the temporary location
            response = FileResponse(open(temp_file_path, 'rb'), as_attachment=True, filename=file.filename)

            # Cleanup after file is downloaded
            def cleanup_temp_file():
                try:
                    os.remove(temp_file_path)  # Delete the temp file
                except Exception as e:
                    print(f"Error during cleanup: {e}")

            response.close_callback = cleanup_temp_file
            return response

    except SharedFile.DoesNotExist:
        return ApiResponse(success=False, message='Shared file not found', status_code=HTTPStatus.NOT_FOUND)
    except Exception as e:
        return ApiResponse(success=False, message=f'Error: {str(e)}', status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
