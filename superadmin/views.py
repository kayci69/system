from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from datetime import timedelta
from django.utils.timezone import now
import json
from django.http import JsonResponse
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from capstone.consumers import  broadcast_to_superusers
from superadmin.models import AdminLog

@login_required
def sa_account(request):
    return render(request, 'superadmin/sa-account.html')

@login_required
def sa_activitylog(request):
    return render(request, 'superadmin/sa-activitylog.html')

@login_required
def sa_index(request):
    return render(request, 'superadmin/sa-index.html')

@login_required
def sa_dashboard(request):
    users = CustomUser.objects.filter(account_type='admin').count() or 0
    online_admins = CustomUser.objects.filter(
        account_type='admin', last_login__gte=now() - timedelta(hours=24)
    ).count() or 0
    server_uptime_percentage = 98

    last_ten_logs = AdminLog.objects.order_by('-id')[:5]
    last_activities = []
    for log in last_ten_logs:
        last_activities.append({
            'username': log.user.username,
            'type': log.type,
            'message': log.message,
            'timestamp': log.timestamp
        })

    context = {
        'total_admins': users,
        'online_admins': online_admins,
        'offline_admins': users - online_admins,
        'server_uptime': server_uptime_percentage,
        'last_activity': last_activities
    }
    return render(request, 'superadmin/sa-dashboard.html', context)

@login_required
def sa_logout(request):
    return render(request, 'superadmin/sa-logout.html')

@login_required
def sa_reports(request):
    return render(request, 'superadmin/sa-reports.html')

@login_required
def sa_usermanagement(request):
    # Filter by 'admin' in account_type
    users = CustomUser.objects.filter(account_type='admin')
    return render(request, 'superadmin/sa-usermanagement.html', {'users': users})

#MINE: DO NOT USE THIS
# @login_required
# def sa_logout(request):
#     logout(request)
#     return redirect('login')

@login_required
def sa_delete_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        try:
            user = CustomUser.objects.get(id=id)
            user.delete()
            broadcast_to_superusers({
                "username": request.user.username,
                "type": "deleted user",
                "message": f"{user.username} has been deleted."
            })
            return JsonResponse({'success': True})
        except Exception as e:
            logout(request)
            return redirect('login')
        
@login_required
def sa_edit_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')

        try:
            user = CustomUser.objects.get(id=id)
            print(id, name, email, role)
            print(user.first_name, user.last_name, user.email, user.account_type)
            name = name.split(' ')
            user.first_name = name[0]
            if len(name) == 2:
                user.last_name = name[1]
            user.email = email
            user.account_type = role
            user.save()
            user = CustomUser.objects.get(id=id)
            print(user.first_name, user.last_name, user.email, user.account_type)

            return JsonResponse({'success': True})
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e):
                return JsonResponse({'success': False, 'error': "Email already exist"})
            else:
                return JsonResponse({'success': False})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
def sa_create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        account_type = data.get('account_type')
        print(username, email, password, account_type)

        user = CustomUser()
        user.username = username
        user.email = email
        user.set_password(password)

        if account_type == 'admin':
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.gender = data.get('gender')
            user.contact_number = data.get('contact_number')
            user.account_type = "admin"
        elif account_type == 'superadmin':
            user.account_type = "superadmin"
        else:
            return JsonResponse({'success': False})

        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})