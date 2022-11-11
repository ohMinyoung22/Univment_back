from django.http import Http404
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import json
from django.core import serializers
# Create your views here.

class PostCreate(generics.CreateAPIView):
    permission_classes = []
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Post.objects.all()
    lookup_field = 'id'
    serializer_class = PostSerializer

class CategoryList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset1 = Category.objects.filter(isDefault = True)
        queryset2 = Category.objects.filter(generated_user = self.request.user)
        queryset = queryset1.union(queryset2)
        return queryset

    def get_permissions(self):
        if self.request.method in ['POST']:

            isDefault = self.request.data['isDefault']

            if bool(isDefault):
                self.permission_classes = [IsAdminUser,]

        return super(CategoryList, self).get_permissions()

class CategoryDetail(APIView):
    permission_classes = [IsAuthenticated,]
    lookup_field = 'category'
    serializer_class = PostSerializer

    def get(self, *args, **kwargs):
        data = serializers.serialize('json', Post.objects.all().filter(user=self.request.user.id).filter(category=self.kwargs['category']))
        return HttpResponse(data)

    def delete(self, request, *args, **kwargs):
        try:
            instance = Category.objects.all().get(id=self.kwargs['category'])
            instance.delete()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
       if self.request.method in ['DELETE']:
            category = Category.objects.all().get(id=self.kwargs['category'])

            if category.isDefault:
                self.permission_classes = [IsAdminUser,]

            return super(CategoryDetail, self).get_permissions()
                    
        
class TimeLine(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Post.objects.filter(timeline=True).order_by('event_date')
    serializer_class = PostSerializer

    # 사용자가 작성한 글만 불러오게 하기
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

class PostWithLogin(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        url = request.build_absolute_uri('/auth/') + 'login/'
        data = {'email' : request.data['email'], 'password' : request.data['password']}
        login_info = requests.post(url, data=data)

        access_token = login_info.json()['access_token']
        refresh_token = login_info.json()['refresh_token']
     
        url = request.build_absolute_uri('/post/')
        data = {"user" : login_info.json()['user']['pk'],
                "title" : request.data['title'],
                "answers" : json.dumps(request.data['answers']),
                "image" : request.data['image'],
                "event_date" : request.data['event_date'],
                "category" : request.data['category']}
        header = {"Authorization" : "JWT " + access_token, "refresh_token" : refresh_token}

        post_info = requests.post(url, headers=header, data=data)
        return HttpResponse(post_info)
        
        


