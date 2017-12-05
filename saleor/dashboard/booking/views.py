from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

from ..views import staff_member_required
from saleor.booking.models import Book as Table
from saleor.room.models import Room
from saleor.customer.models import Customer

from ...decorators import user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

# global variables
table_name = 'Booking'


@staff_member_required
def list(request):
    global table_name
    try:
        options = Table.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(options, 10)
        try:
            options = paginator.page(page)
        except PageNotAnInteger:
            options = paginator.page(1)
        except InvalidPage:
            options = paginator.page(1)
        except EmptyPage:
            options = paginator.page(paginator.num_pages)
        data = {
            "table_name": table_name,
            "options": options,            
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed '+table_name+' List', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed '+table_name+' List Page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing payment options')


@staff_member_required
def add(request):
    global table_name
    if request.method == 'POST':
        if request.POST.get('pk'):
            instance = Table.objects.get(pk=request.POST.get('pk'))
        else:
            instance = Table()
        if request.POST.get('c_name'):
            customer_name = request.POST.get('c_name')
        if request.POST.get('mobile'):
            mobile = request.POST.get('mobile')
        try:
            customer = Customer.objects.get(mobile=mobile)
        except:
            customer = Customer.objects.create(name=customer_name, mobile=mobile)
        instance.customer = customer
        if request.POST.get('room'):
            try:
                room = Room.objects.get(pk=int(request.POST.get('room')))
                instance.room = room
            except Exception as e:
                return HttpResponse(json.dumps({'error': str(e)}), content_type="application/json")

        if request.POST.get('total_price'):
            instance.price = request.POST.get('total_price')
        if request.POST.get('check_in'):
            instance.check_in = request.POST.get('check_in')
        if request.POST.get('price_type'):
            instance.price_type = request.POST.get('price_type')
        if request.POST.get('check_out'):
            instance.check_out = request.POST.get('check_out')
        if request.POST.get('days'):
            instance.days = request.POST.get('days')
        if request.POST.get('child'):
            instance.child = request.POST.get('child')
        if request.POST.get('adult'):
            instance.adult = request.POST.get('adult')
        if request.POST.get('description'):
            instance.description = request.POST.get('description')
        instance.user = request.user
        instance.save()
        room.is_booked = True
        room.available_on = request.POST.get("check_out")
        room.save()
        data = {
                'name': instance.room.name,
                'check_out': instance.check_out,
                'room_pk': instance.room.id
                }
        return HttpResponse(json.dumps(data), content_type='application/json')
        #return HttpResponse(json.dumps({'message': 'Invalid method'}))
    else:
        if request.is_ajax():
            ctx = {'table_name': table_name}
            if request.GET.get("room_pk"):
                room = Room.objects.get(pk=int(request.GET.get("room_pk")))
                ctx['room'] = room
            return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/modal_form.html', ctx)
        ctx = {'table_name': table_name}
        return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/form.html', ctx)


@staff_member_required
def delete(request, pk=None):
    global table_name
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            option.delete()
            user_trail(request.user.name, 'deleted room : '+ str(option.name), 'delete')
            info_logger.info('deleted room: '+ str(option.name))
            return HttpResponse('success')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    global table_name
    instance = get_object_or_404(Table, pk=pk)
    if request.method == 'GET':
        ctx = {'table_name': table_name, 'instance': instance}
        return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/form.html', ctx)
    if request.method == 'POST':
        return HttpResponse('Invalid Request method')


@staff_member_required
def book(request):
    global table_name
    objects = Room.objects.all().order_by('floor')
    floors = []
    for floor in objects:
        if floor.floor not in floors:
            floors.append(floor.floor)
    print floors
    ctx = {'table_name': table_name, 'objects': objects, "floors": floors}
    return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/rooms.html', ctx)


@staff_member_required
def detail(request, pk=None):
    global table_name
    if request.method == 'GET':
        try:
            option = get_object_or_404(Table, pk=pk)
            ctx = {'option': option}
            user_trail(request.user.name, 'access Car details of: ' + str(option.name)+' ','view')
            info_logger.info('access car details of: ' + str(option.name)+'  ')
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/detail.html', {'error': e})


def searchs(request):
    global table_name
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            options = Table.objects.filter(
                Q(name__icontains=q)
            ).order_by('-id')
            paginator = Paginator(options, 10)
            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            if p2_sz:
                options = paginator.page(page)
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', {'options': options,'sz':sz})
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': sz,
                    'q': q}
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/search.html', data)


@staff_member_required
def paginate(request):
    global table_name
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Table.objects.filter(name=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/'+table_name.lower()+'/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': request.GET.get('gid')}
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/p2.html',data)

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        data = {'options': options,
                'pn': paginator.num_pages,
                'sz': 10,
                'gid': request.GET.get('gid')}
        return TemplateResponse(request,'dashboard/'+table_name.lower()+'/p2.html', data)
    else:
        try:
            options = Table.objects.all().order_by('-id')
            if list_sz:
                paginator = Paginator(options, int(list_sz))
                options = paginator.page(page)
                data = {
                    'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()


@staff_member_required
def fetch_amenities(request):
    global table_name
    search = request.GET.get('search')
    dictionary = Room.objects.all().exclude(is_booked=True).filter(name__icontains=str(search))
    l = []
    for instance in dictionary:
        # {"text": "Afghanistan", "value": "AF"},
        contact = {'text': instance.name, 'value': instance.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


@staff_member_required
def customer_token(request):
    global table_name
    if request.GET.get('customer'):
        pk = int(request.GET.get('customer'))
        instance = Customer.objects.get(pk=pk)
        l = []
        contact = {
                   "results": {
                               'text': instance.name,
                               'value': instance.id,
                               'mobile': instance.mobile
                               }
                  }
        l.append(contact)
        return HttpResponse(json.dumps(l[0]), content_type='application/json')
    search = request.GET.get('search')
    dictionary = Customer.objects.all().filter(name__icontains=str(search))
    l = []
    for instance in dictionary:
        # {"text": "Afghanistan", "value": "AF"},
        contact = {'text': instance.name, 'value': instance.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


@staff_member_required
def compute_room_price(request):
    global table_name
    days = int(request.POST.get('days'))
    price_type = request.POST.get('price_type')
    rooms = json.loads(request.POST.get('rooms'))
    total = 0
    for instance in rooms:
        room = Room.objects.get(pk=int(instance))
        total = float(total + eval('room.get_'+str(price_type)+'_price()'))
        print room.get_weekly_price()
    total *= float(int(days))
    return HttpResponse(json.dumps({"price": float(total)}), content_type='application/json')


