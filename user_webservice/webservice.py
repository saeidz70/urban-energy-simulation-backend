# views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user_webservice.helper import ProjectDataHelper
from user_webservice.serializers import ProjectDataSerializer


class ProjectDataView(APIView):
    def post(self, request):
        serializer = ProjectDataSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Pass data to the helper class
            helper = ProjectDataHelper()
            helper.process_data(data)

            return Response({"message": "Data processed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
