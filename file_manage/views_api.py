from django.shortcuts import render
import os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from common.Define import RETURN_CODE
from django.core import serializers
import shutil
import json
from concurrent.futures import ThreadPoolExecutor
# Create your views here.


base_dir = settings.BASE_DIR
media_base_dir = os.path.join(base_dir,'media')


def request_file_tree(request):
    if request.method == "GET":
        GET = request.GET.get
        file_id = GET('id')
        data_list = []
        file_path = None
        if file_id == "#":
            file_path = media_base_dir
            file_list = os.listdir(media_base_dir)
            file_list.reverse()
        else:
            file_path = GET('file_path')
            file_path = file_path.replace('#',media_base_dir)
            file_list = os.listdir(file_path)
            file_list.reverse()
        for i in file_list:
            file_abs_dir = os.path.join(file_path, i)
            if os.path.isdir(file_abs_dir):
                data_list.append({'id':os.path.join(file_path, i),
                                  'text':i,
                                  "children":True,
                                  'icon':'/static/file_manage/jstree/ico/file.ico'})
        return JsonResponse(data_list,safe=False)


def create_dir(request):
    if request.method == "POST":
        POST = request.POST.get
        file_path = POST('file_path')
        file_path = file_path.replace('#',media_base_dir)
        if os.path.exists(file_path):
            file_path += '1'
        if os.path.basename(file_path) == "New node":
            file_path += '1'
        os.makedirs(file_path)
        dir_name = os.path.basename(file_path)
        return JsonResponse({'dir_name':dir_name,'id':file_path})


def rename_dir(request):
    if request.method == "POST":
        POST = request.POST.get
        file_path = POST('file_path')
        old_file_path = POST('old_file_path')
        new_file_name = POST('new_file_name')
        if new_file_name:
            file_path = os.path.join(os.path.dirname(old_file_path),new_file_name)
        if file_path and "#" in file_path:
            file_path = file_path.replace('#', media_base_dir)
        if old_file_path and "#" in old_file_path:
            old_file_path = old_file_path.replace('#', media_base_dir)
        if os.path.exists(old_file_path):
            os.renames(old_file_path,file_path)
        dir_name = os.path.basename(file_path)
        return JsonResponse({'dir_name':dir_name,'id':file_path})




def delete_dir(request):
    if request.method == "POST":
        file_path_list = request.POST.getlist('file_path[]')
        for file_path in file_path_list:
            file_path = file_path.replace('#',media_base_dir)
            if os.path.exists(file_path):
                if os.path.basename(file_path) == "root":
                    return JsonResponse({'return_code':'SUCCESS'})
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                return JsonResponse({'return_code':'SUCCESS'})



def request_file_list(request):
    file_type_dict = {
        "png": "glyphicon glyphicon-picture",
        "PNG": "glyphicon glyphicon-picture",
        "JPG" : "glyphicon glyphicon-picture",
        "jpg" : "glyphicon glyphicon-picture",
        "txt": "glyphicon glyphicon-book",
        "mp4": "glyphicon glyphicon-film",
        "ts": "glyphicon glyphicon-film",
        "dir": "glyphicon glyphicon-folder-open",
        "other" : "glyphicon glyphicon-question-sign",
    }
    file_type_image = {
        "txt": "/static/file_manage/image/file_image/text.png",
        "mp4": "/static/file_manage/image/file_image/video.png",
        "ts": "/static/file_manage/image/file_image/video.png",
        "dir": "/static/file_manage/image/file_image/file.png",
        "other" : "/static/file_manage/image/file_image/other.png",
    }
    if request.method == "GET":
        GET = request.GET.get
        file_path = GET('file_path')
        file_path = file_path.replace('/', os.sep)
        if file_path.startswith('#'):
            file_path = file_path.replace('#', media_base_dir)
        
        data = {
            'li_ele':'',
            'div_ele':'',
        }
        li_ele = """
        <li class="list-group-item file_item" file_type="{0}" file_path="{1}" file_server_path="{2}">
            <span class="{3}"></span> {4}
        </li>
        """
        div_ele = """
        <div class="col-xs-6 col-md-3 file_item" file_type="{0}" file_path="{1}" file_server_path="{2}">
            <a class="thumbnail" style="text-align: center;">
            <img src="{3}" alt="..." style="max-height: 80px;">
            {4}
            </a>
        </div>
        """
        if os.path.exists(file_path):
            file_list = os.listdir(file_path)
            for i in file_list:
                file_abs_dir = os.path.join(file_path,i)
                file_server_dir = file_abs_dir.replace(base_dir,'').replace('\\','/')
                if os.path.isdir(file_abs_dir):
                    data['li_ele'] += li_ele.format("dir", file_abs_dir, '', file_type_dict['dir'], i)
                    data['div_ele'] += div_ele.format("dir", file_abs_dir, '', file_type_image['dir'], i)
                elif '.' in i and i.split('.')[1] in file_type_dict:
                    if i.split('.')[1] in ['mp4','ts',]:
                        data['li_ele'] += li_ele.format(i.split('.')[1], file_abs_dir, file_server_dir, file_type_dict[i.split('.')[1]], i)
                        data['div_ele'] += div_ele.format(i.split('.')[1], file_abs_dir, file_server_dir, file_type_image[i.split('.')[1]], i)
                    elif i.split('.')[1] in ['png', 'JPG', 'jpg', 'PNG']:
                        data['li_ele'] += li_ele.format(i.split('.')[1], file_abs_dir, file_server_dir, file_type_dict[i.split('.')[1]], i)
                        data['div_ele'] += div_ele.format(i.split('.')[1], file_abs_dir, file_server_dir, file_server_dir, i)
                else:
                     data['li_ele'] += li_ele.format("other", file_abs_dir, file_server_dir, file_type_dict['other'], i)
                     data['div_ele'] += div_ele.format("other", file_abs_dir, file_server_dir, file_type_image['other'], i)
        return JsonResponse(data)



def write_file(file_path, file_obj):
        with open(file_path,'wb')as w:
            for chunk in file_obj.chunks():
                w.write(chunk)


def add_files(request):
    return_value = {
        'return_code':RETURN_CODE.SUCCESS,
        'return_msg':'',
        'datas':'',
    }
    try:
        FILES = request.FILES
        POST = request.POST.get
        file_dir_name = POST('file_path')
        with ThreadPoolExecutor(max_workers=10) as pool:
            for k, v in FILES.items():
                w_file_path = os.path.join(file_dir_name, k)
                pool.submit(write_file,**{'file_path':w_file_path, 'file_obj':v})
        return JsonResponse(return_value)

    except Exception as error:
        
        return_value['return_code'] = RETURN_CODE.FAIL
        return_value['return_msg'] = "服务器出错，错误：{0}".format(error)
        return JsonResponse(return_value)



def request_page_mode(request):
    page_mode = None
    if request.method == 'GET':
        with open(base_dir+'/static/file_manage/page_conf.json', 'r')as f:
            page_mode = json.load(f)
        return JsonResponse({'data':page_mode})
    else:
        mode = request.POST.get('mode')
        with open(base_dir+'/static/file_manage/page_conf.json', 'w')as f:
            json.dump({'page_mode':mode},f)
        return JsonResponse({})


def mv_dir(request):
    if request.method == 'POST':
        file_path_list = request.POST.getlist('file_path_list[]')
        new_path = request.POST.get('new_path')
        new_path = new_path.replace('#', media_base_dir)
        for i in file_path_list:
            i = i.replace('#', media_base_dir)
            if new_path == os.path.dirname(i):
                continue
            shutil.move(i,new_path)
        return JsonResponse({})


