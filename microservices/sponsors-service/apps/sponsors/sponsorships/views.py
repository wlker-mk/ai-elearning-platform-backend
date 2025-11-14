from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        # Implement list logic
        return Response({'message': 'List endpoint'})
    
    def create(self, request, *args, **kwargs):
        # Implement create logic
        return Response({'message': 'Create endpoint'}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        # Implement retrieve logic
        return Response({'message': f'Retrieve endpoint for {pk}'})
    
    def update(self, request, pk=None, *args, **kwargs):
        # Implement update logic
        return Response({'message': f'Update endpoint for {pk}'})
    
    def destroy(self, request, pk=None, *args, **kwargs):
        # Implement delete logic
        return Response(status=status.HTTP_204_NO_CONTENT)
