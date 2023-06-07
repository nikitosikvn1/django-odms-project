from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if username is None or password is None:
            return Response({"detail": "Username and password required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid username/password."}, status=400)

        if not user.groups.filter(name='Editor').exists():
            return Response({"detail": "Access denied. You do not have permissions to generate a token."}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

