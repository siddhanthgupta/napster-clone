from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from napster.models import User, File, UserFileMap
from napster.serializers import UserSerializer, FileSerializer, UserFileMapSerializer


@api_view(http_method_names=['GET', 'POST', 'DELETE'])
def user_list(request, format=None):
    '''
        Performs one of 3 actions: 
            GET: Returns list of all users
            POST: Adds a new user to the system
            DELETE: Deletes a user from the system (all the files registered
                        under the user are automatically removed by cascade
                        effect of the foreign key relation to User)
    '''
    if(request.method == 'GET'):
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)
    elif(request.method == 'POST'):
        print(request.data)
        user_serializer = UserSerializer(data=request.data)
        if(user_serializer.is_valid()):
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif(request.method == 'DELETE'):
        try:
            ip_address = request.data['ip_address']
            port = request.data['port']
            user = User.objects.get(ip_address=ip_address, port=port)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data='User does not exist')
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Invalid data format received')
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['GET', 'DELETE'])
def user_details(request, user_id, format=None):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if(request.method == 'GET'):
        user_serializer = UserSerializer(user)
        return Response(data=user_serializer.data)
    elif(request.method == 'DELETE'):
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(http_method_names=['GET'])
def file_list(request, format=None):
    if(request.method == 'GET'):
        file_list = File.objects.all()
        file_serializer = FileSerializer(file_list, many=True)
        return Response(file_serializer.data)


@api_view(http_method_names=['GET', 'POST'])
def users_for_file(request, filename, format=None):
    if(request.method == 'GET'):
        try:
            file = File.objects.get(filename=filename)
        except File.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid filename'})
        if(UserFileMap.objects.filter(file=file).exists()):
            file_user_map = UserFileMap.objects.filter(file=file)
            res_dict = {'filehash': file.filehash}
            res_dict['users'] = []
            for item in file_user_map:
                user_serializer = UserSerializer(item.user)
                res_dict['users'].append(user_serializer.data)
            return Response(res_dict)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'No users found'})
    elif(request.method == 'POST'):
        try:
            ip_address = request.data['ip_address']
            port = request.data['port']
            filehash = request.data['filehash']
            user = User.objects.get(ip_address=ip_address, port=port)
        except KeyError:
            # This is in the event that our request.data does not have
            # the correct key-value pairs
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid request data'})
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Unable to find user record'})
        try:
            file = File.objects.get(pk=filename)
        except File.DoesNotExist:
            file = File(filename=filename, filehash=filehash)
            file_serializer = FileSerializer(
                data={'filename': filename, 'filehash': filehash})
            if(file_serializer.is_valid()):
                file_serializer.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unable to save file'})

        if(file.filehash != filehash):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'File hash is not valid'})
        user_file_map = UserFileMapSerializer(
            data={'user': user.pk, 'file': file.filename})
        if(user_file_map.is_valid()):
            user_file_map.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=user_file_map.errors)

# Create your views here.
