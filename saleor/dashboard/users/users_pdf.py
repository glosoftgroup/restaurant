from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from ..views import staff_member_required
from ...userprofile.models import User
from ...utils import render_to_pdf, image64
from datetime import date


@staff_member_required
def pdf( request ):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		group = None
		if q is not None:
			users = User.objects.filter(
				Q( fullname__icontains = q ) | Q( code__icontains = q ) |
				Q( name__icontains = q ) | Q( email__icontains = q ) |
				Q( mobile__icontains = q ) | Q(groups__id__icontains=q)).order_by('-id')

			if gid:
				users = users.filter(groups__id=gid)
				group = Group.objects.get(id=gid)

		elif gid:
			users = User.objects.all().filter(groups__id=gid)
			group = Group.objects.get(pk=gid)
			print (group.name)
		else:
			users = User.objects.all()
		img = image64()
		data = {
			'today': date.today(),
			'users': users,
			'puller': request.user,
			'image': img,
			'group':group
		}
		pdf = render_to_pdf('dashboard/users/pdf/users.html', data)
		return HttpResponse(pdf, content_type='application/pdf')
