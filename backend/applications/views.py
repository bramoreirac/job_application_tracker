from rest_framework import generics
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        # Return only applications owned by the current user.

        queryset = Application.objects.filter(owner=self.request.user)

        return queryset

    def perform_create(self, serializer):

        serializer.save(owner=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(owner=self.request.user)