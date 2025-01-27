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

from common.apiresponse import ApiResponse
from common.crypto import generate_encryption_key, store_encryption_key, encrypt_file, decrypt_file
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
    else:
        return Response(file_serializer.errors, status=HTTPStatus.BAD_REQUEST)
    return Response({'message': 'File uploaded successfully!'}, status=HTTPStatus.CREATED)

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

    # Check if the user has permission to access the file
    if not request.user.is_admin and file.owner != request.user and not SharedFile.objects.filter(file=file, user=request.user).exists():
        return ApiResponse(success=False, message='Permission denied', status=HTTPStatus.FORBIDDEN)

    shared_file = SharedFile.objects.filter(file=file, user=request.user).first()
    if not shared_file:
        # Create a new shared file entry if it doesn't exist
        shared_file = SharedFile.objects.create(
            file=file,
            user=request.user,
            share_hash=secrets.token_urlsafe(32)
        )

    share_link = shared_file.share_hash
    return ApiResponse(
        success=True,
        message='Share link generated successfully',
        data={'id': share_link},
        status_code=HTTPStatus.CREATED
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_shared_file(request, file_id):
    """Retrieve a shared file using its ID."""
    temp_dir = None
    try:
        shared_file = SharedFile.objects.get(share_hash=file_id)
        file = shared_file.file
        print("File ID:", file.id)
        
        # Create a temporary directory in media folder
        media_root = os.path.dirname(file.file.path)
        temp_dir = os.path.join(media_root, 'temp', secrets.token_hex(8))
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Copy the file to temp directory
        print("Original file path:", file.file.path)
        print("Temp file path:", temp_file_path)
        shutil.copy2(file.file.path, temp_file_path)
        
        try:
            # Decrypt the file
            print("Decrypting with ID:", str(file.id))
            decrypt_file(str(file.id), temp_file_path)
            
            # Open and return the decrypted file
            response = FileResponse(
                open(temp_file_path, 'rb'),
                content_type=file.mime,
                as_attachment=True,
                filename=file.filename
            )
            
            # Clean up will happen when the file is sent
            response.close_callback = lambda: shutil.rmtree(temp_dir, ignore_errors=True)
            
            return response
            
        except Exception as e:
            # Clean up on error
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            print(e)
            return ApiResponse(
                success=False,
                message='Error processing file',
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code='FILE_PROCESSING_ERROR'
            )
            
    except SharedFile.DoesNotExist:
        return ApiResponse(
            success=False,
            message='Shared file not found',
            status_code=HTTPStatus.NOT_FOUND,
            code='SHARED_FILE_NOT_FOUND'
        )
    except Exception as e:
        # Clean up if temp_dir was created
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return ApiResponse(
            success=False,
            message='Error retrieving file',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code='FILE_RETRIEVAL_ERROR'
        )