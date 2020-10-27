from django.shortcuts import redirect
from rest_framework.permissions import (
    IsAuthenticated,
    BasePermission,
    SAFE_METHODS,
    AllowAny
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import status

from .models import (
    CustomUser,
    UserSerializer,
    PostEditHistorySerializer,
    PostsSerializer, Posts, PostEditHistory
)


def validate_bool_request(value):
    value = str(value).replace("(", "")\
        .replace(")", "")\
        .replace(" ", "").replace(",", "")

    if value in ('true', 't', 'True', '1'):
        return True
    if value in ('false', 'f', 'False', '0'):
        return False
    return bool(value)


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user


class InfoView(APIView):
    """
    /post/ for geting all user posts my posts, and create fot auth users
    /post/<id>/: for get post by id, allow for all
    /post/edit/<pk>/: Edit post by id `edit` `delete`
    /user/: get all users
    /user/?id=<id>: Filter users by params `id` `sex` `birthdate` `rating`
    /api-auth/: auth in `browser`
    /signup/::param
    """

    def get(self, request):
        """
            /post/ for geting all user posts my posts,
            and create fot auth users
            /post/<id>/: for get post by id, allow for all
            /post/edit/<pk>/: Edit post by id
            /user/: get all users
            /user/?id=<id>: Filter users by params
            /api-auth/: auth in `browser`
            /signup/::param
            """
        return Response({
            "urls": {
                "/post/": "for geting all user posts my posts,"
                          "``` and create fot auth users```",
                "/post/<id>/": "for get post by id, allow for all",
                "post/edit/<pk>/": "Edit post by id",
                "/user/": "get all users",
                "/user/?id=<id>": "Filter users by params",
                "api-auth/": "auth in browser",

            },

        }, status=status.HTTP_200_OK)


class CreateUserView(CreateAPIView):

    model = CustomUser
    permission_classes = [AllowAny]

    serializer_class = UserSerializer


class CreatePostView(APIView):

    model = Posts

    serializer_class = PostsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request_user = request.user

        if request_user:
            user_posts = Posts.objects.filter(
                author=request_user,
                is_active=True
            ).values_list(
                'id',
                'title'
            )
            return Response({"Posts": user_posts})
        else:
            return Response({"Posts": 'Not Founds'})

    def post(self, request):
        request_user = request.user
        if request_user:
            if request.data:
                request_post = request.data
                post = Posts(
                    title=request_post['title'],
                    text=request_post['text'],
                    author=request_user
                )
                post.save()

                post_edit = PostEditHistory(
                    post=post,
                    author=request_user,
                    text=f"Create post:[{post.id}] [{post.title}]"
                         f" user:[{request_user.username}]"
                )
                post_edit.save()

                serializer = PostsSerializer(post)
                return Response(
                    {"Posts": serializer.data},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"Posts": "Not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"Error": 'permission denied'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PostView(APIView):

    model = Posts

    serializer_class = PostsSerializer

    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, pk):
        request_user = request.user
        if request_user:
            try:
                user_posts = Posts.objects.get(id=pk, is_active=True)
                serializer = PostsSerializer(user_posts)
                return Response({"Post": serializer.data})
            except Posts.DoesNotExist:
                return redirect("/post/")
        else:
            return Response({"Post": 'Not Founds'})

    def post(self, request, pk):
        request_user = request.user
        if request_user.is_authenticated:
            if request.data:
                request_post = request.data
                post = Posts.objects.create(
                    title=request_post['title'],
                    text=request_post['text'],
                    author=request_user
                )
                post.save()

                serializer = PostsSerializer(post)
                return Response(
                    {"Posts": serializer.data},
                    status=status.HTTP_201_CREATED
                )

            return Response({"Posts": "Not found"})
        return Response({"Error": 'permission denied'})


class UsersProfileView(APIView):
    """
    Searching user
    use GET params for filter users
    <id: Int>
    <sex> [
    [F] as female,

    ,

            birthday_from = request.GET.get('birthday_from')

            birthday_to = request.GET.get('birthday_to')

            rating = request.GET.get('rating')
    """

    model = CustomUser

    serializer_class = UserSerializer

    permission_classes = [
        AllowAny  # Or anon users can't register
    ]

    def get(self, request):
        try:
            pk = request.GET.get('id')

            sex = request.GET.get('sex')

            birthday_from = request.GET.get('birthday_from')

            birthday_to = request.GET.get('birthday_to')

            rating = request.GET.get('rating')

            param_search = {}

            if pk:
                param_search['id'] = pk

            if sex:
                param_search['sex'] = sex

            if birthday_from:
                param_search['birth_date__gt'] = birthday_from

            if birthday_to:
                param_search['birth_date__lt'] = birthday_to

            if rating:
                param_search['rating'] = rating

            user_ = CustomUser.objects.filter(
                **param_search
            )

            user_serializer = UserSerializer(user_, many=True)

            return Response({
                "Users count": user_.count(),
                "Users": user_serializer.data
            })

        except CustomUser.DoesNotExist:
            user_ = CustomUser.objects.all()
            users_serializer = UserSerializer(user_, many=True)

            return Response({
                "Users count": user_.count(),
                "Users": users_serializer.data
            }, status=status.HTTP_200_OK)


class PostEditView(APIView):

    model = Posts

    serializer_class = PostsSerializer

    def get(self, request, pk):
        request_user = request.user
        if request_user.is_authenticated:
            try:
                user_posts = Posts.objects.get(
                    id=pk,
                    author=request_user
                )
                serializer_post = PostsSerializer(user_posts)

                post_edit_history = PostEditHistory.objects.filter(
                    post=user_posts
                ).order_by('-id')

                serializer_post_editing = PostEditHistorySerializer(
                    post_edit_history,
                    many=True
                )
                return Response(
                    {
                        "Post": serializer_post.data,
                        "Edit History": serializer_post_editing.data,
                    }
                )

            except Posts.DoesNotExist:
                return Response(
                    {"Post": 'Not Found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"Error": 'permission denied'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, pk):
        request_user = request.user
        if request_user.is_authenticated:
            if request.data:
                request_post = request.data

                title = request_post['title']
                text = request_post['text']
                is_active = validate_bool_request(request_post['is_active'])

                try:
                    post = Posts.objects.get(
                        id=pk,
                        author=request_user
                    )
                    post.title = title
                    post.text = text
                    post.is_active = is_active
                    post.save()

                    post_edit = PostEditHistory(
                        post=post,
                        author=request_user,
                        text=f"Edit post:[{post.id}] [{post.title}] "
                             f"user:[{request_user.username}] "
                             f"title:{title} "
                             f"text:{text} "
                             f"is_active:{is_active}"
                    )
                    post_edit.save()

                    post_edit_history = PostEditHistory.objects.filter(
                        post=post
                    ).order_by('-id')

                    serializer_post = PostsSerializer(post)
                    serializer_post_editing = PostEditHistorySerializer(
                        post_edit_history,
                        many=True
                    )

                    return Response(
                        {
                            "Post": serializer_post.data,
                            "Edit History": serializer_post_editing.data,
                        }
                    )

                except Posts.DoesNotExist:
                    return Response({
                        "Error": 'permission denied or '
                                 'post not found'
                    },
                        status=status.HTTP_400_BAD_REQUEST)

            return Response({"Posts": "Not found"})
        return Response({
            "Error": 'permission denied'
        },
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            post = Posts.objects.get(id=pk, author=request.user)
            post_mess = f"post:[{post.title}] id:[{post.id}] was hide"

            post.is_active = False # not delete hide only
            post.save()

            post_edit_history = PostEditHistory(
                post=post,
                author=request.user,
                text=post_mess
            )
            post_edit_history.save()

            return Response({"mess": post_mess},
                            status=status.HTTP_204_NO_CONTENT)

        except:
            return Response({"error": "permission denied"},
                            status=status.HTTP_400_BAD_REQUEST)
