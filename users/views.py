
# views.py/users
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser
import logging
# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from superadmin.models import AdminLog
from capstone.consumers import broadcast_to_superusers

logger = logging.getLogger(__name__)

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if user.account_type == 'superadmin':
                return redirect('superadmin_dashboard')
            elif user.account_type == 'admin':
                type = "Logged in"
                msg = f"{user.username} has logged in."
                time = timezone.now()

                AdminLog.objects.create(user=user,type= type, message=msg, timestamp=time)
                broadcast_to_superusers({"username": user.username, "type": type, "message": msg, "timestamp": time.isoformat()})
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have access.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'users/login.html')

# Register View
@csrf_exempt
def register(request):
    if request.method == 'POST':
   
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confrim_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        contact_number = request.POST.get('contact_number')
        

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/register.html')

        if not all([email, username, password, first_name, last_name, gender, contact_number]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'users/register.html')

        try:
            user = CustomUser()
            user.email=email
            user.username=username
            user.first_name=first_name
            user.last_name=last_name
            user.gender=gender
            user.contact_number=contact_number
            user.password=make_password(password) 
            user.save()
            return render(request, 'users/register.html',{'login':True})


        except Exception as e:

            return render(request, 'users/register.html',{'already_exist':True})
    else:
        return render(request, 'users/register.html')

# Forgot Password View
def forgot_pass(request):
    return render(request, 'users/forgot-pass.html')

# Reset Password View
def reset_pass(request):
    return render(request, 'users/reset-pass.html')

# Admin Dashboard View
@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/index.html')

# Superadmin Dashboard View
@login_required
def superadmin_dashboard(request):
    return render(request, 'superadmin/sa_index.html')




def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        password=request.POST['password']
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email__exact=email)
            user.set_password(password)
            user.save()

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Changed Your Password'
            message = render_to_string('users/password_change.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            print('password chanaged sucessfully')

            return render(request, 'users/forgot-pass.html',{'password_chanaged':True})
        else:
            return render(request, 'users/forgot-pass.html',{'account':True})
        
    else:    
        return render(request, 'users/forgot-pass.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confrim_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = CustomUser.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            email=user.email
            # sucessfully chanaged password email
            current_site = get_current_site(request)
            mail_subject = 'Sucessfully Your Password is Chanaged'
            message = render_to_string('users/password_change.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetpassword')
    else:
        return render(request, 'users/reset-pass.html')

