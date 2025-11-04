from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.urls import reverse
from .models import movie_user
import urllib.parse
from django.http import HttpResponse
import random, time
from datetime import datetime, timedelta
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings



def signup(request):
    context = {
        'email': '',
        'password': '',
        'confirmPassword': '',
        'terms_check': False,
    }

    if request.method == 'POST':
        email = request.POST.get('email', '')
        raw_password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        terms = request.POST.get('termsCheck') == 'on'

        # echo back into form
        context.update({
            'email': email,
            'password': raw_password,
            'confirmPassword': confirm_password,
            'terms_check': terms,
        })

        # check for existing email
        if movie_user.objects.filter(email=email).exists():
            context['signup_error'] = "That email is already registered."
            return render(request, 'authentication/signup.html', context)

        # all front-end validation passed
        hashed = make_password(raw_password)
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')

        # 3) Generate OTP
        otp = f"{random.randint(0, 999999):06d}"
        now_ts = int(time.time())

        # 4) Store everything in session
        request.session['pending_signup'] = {
            'email': email,
            'password': hashed,
            'terms_check': terms,
            'login_ip': ip,
            'otp_code': otp,
            'otp_created_at': now_ts,
        }

        # 5) Send OTP email
        send_mail(
        subject    = "Your MovieVerse OTP Code",
        message    = f"Your 6-digit code is {otp}",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [email],
        fail_silently = False,
        )

        return redirect(reverse('email_verification'))


        
        

    return render(request, 'authentication/signup.html', context)



def email_verification(request):
    pending = request.session.get('pending_signup')
    if not pending:
        return redirect('signup')

    error = None
    resent = request.session.pop('otp_resent', False)

    if request.method == 'POST':
        entered = request.POST.get('otp','').strip()
        sent_ts = pending['otp_created_at']

        if entered == pending['otp_code'] and time.time() - sent_ts <= 600:
            # Create the real user record
            join_time = timezone.localtime(timezone.now())
            user = movie_user(
                email=pending['email'],
                password=pending['password'],
                join_time=join_time,
                login_ip=pending['login_ip'],
                terms_check=pending['terms_check']
            )
            user.save()

            del request.session['pending_signup']

            msg = urllib.parse.quote("Account created! You can now log in.")
            login_url = reverse('login') + f'?login_success={msg}'
            return redirect(login_url)
        else:
            error = "Invalid or expired code."

    return render(request, 'authentication/email_verification.html', {
        'verification_error': error,
        'resent': resent,
    })


def resend_otp(request):
    pending = request.session.get('pending_signup')
    if not pending:
        return redirect('signup')

    # Generate new OTP & timestamp
    otp = f"{random.randint(0, 999999):06d}"
    pending['otp_code'] = otp
    pending['otp_created_at'] = int(time.time())
    request.session['pending_signup'] = pending
    
    request.session['otp_resent'] = True

    
    send_mail(
        subject    = "Your MovieVerse OTP Code",
        message    = f"Your 6-digit code is {otp}",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [pending['email']],
        fail_silently = False,
    )

    return redirect('email_verification')







def login(request):
    # Already logged in?
    if request.session.get('user_id'):
        return redirect('user_profile:preferences')

    # 1) Capture the `next` param from GET (where we want to go after login)
    next_url = request.GET.get('next', '')

    context = {
        'email': '',
        'next': next_url,   # pass it into the template
    }

    # Legacy success message support
    qs_success = request.GET.get('login_success')
    if qs_success:
        context['login_success'] = urllib.parse.unquote(qs_success)

    if request.method == 'POST':
        email       = request.POST.get('email', '').strip()
        raw_password= request.POST.get('password', '')
        next_post   = request.POST.get('next', '')   # our hidden input

        context['email'] = email

        user = movie_user.objects.filter(email=email, is_active=True).first()
        if not user or not check_password(raw_password, user.password):
            context['login_error'] = "Invalid email or password."
            return render(request, 'authentication/login.html', context)

        # 2) Credentials are good — log them in
        request.session['user_id'] = user.user_id

        # 3) If we had a `next`, go there first
        if next_post:
            return redirect(next_post)

        # 4) Otherwise standard post-login landing
        return redirect('user_profile:preferences')

    # GET — render the login form
    return render(request, 'authentication/login.html', context)




def reset_password(request):
    
    context = {}
    if request.method == 'POST':
        email        = request.POST['email'].strip()
        new_pw       = request.POST['new_password']

        user = movie_user.objects.filter(email=email).first()
        if not user:
            context['reset_error'] = "No account found with that email."
            return render(request, 'authentication/reset_password.html', context)

        # build pending_reset
        otp = f"{random.randint(0,999999):06d}"
        now_ts = int(time.time())
        request.session['pending_reset'] = {
            'email': email,
            'new_password': make_password(new_pw),
            'otp_code': otp,
            'otp_created_at': now_ts
        }
        # send OTP via email
        send_mail(
            "Your MovieVerse Password Reset Code",
            f"Your OTP is {otp}",
            None,                # uses DEFAULT_FROM_EMAIL
            [email],
            fail_silently=False
        )
        return redirect(reverse('reset_password_verify'))

    return render(request, 'authentication/reset_password.html', context)


def reset_password_verify(request):

    pending = request.session.get('pending_reset')
    if not pending:
        return redirect('reset_password')

    error = None
    if request.method == 'POST':
        entered = request.POST.get('otp','').strip()
        sent_ts = pending['otp_created_at']

        if entered == pending['otp_code'] and time.time() - sent_ts <= 600:
            # commit the password change
            user = movie_user.objects.get(email=pending['email'])
            user.password = pending['new_password']
            user.save()
            del request.session['pending_reset']
            return redirect('login')
        else:
            error = "Invalid or expired OTP."

    return render(request, 'authentication/reset_password_verify.html', {
        'verification_error': error
    })


def resend_reset_otp(request):
    
    pending = request.session.get('pending_reset')
    if not pending:
        return redirect('reset_password')

    otp = f"{random.randint(0,999999):06d}"
    pending['otp_code'] = otp
    pending['otp_created_at'] = int(time.time())
    request.session['pending_reset'] = pending

    send_mail(
        "Your New MovieVerse Reset Code",
        f"Your new OTP is {otp}",
        None,
        [pending['email']],
        fail_silently=False
    )

    return redirect('reset_password_verify')
