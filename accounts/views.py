from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserLoginForm
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.role == 'JOB_SEEKER':
                return redirect('jobseeker_dashboard')
            return redirect('employer_dashboard')

    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == 'JOB_SEEKER':
                    return redirect('jobseeker_dashboard')
                else:
                    return redirect('employer_dashboard')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def jobseeker_dashboard(request):
    profile = request.user.jobseekerprofile
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/jobseeker_dashboard.html', context)

@login_required
def employer_dashboard(request):
    profile = request.user.employerprofile
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/employer_dashboard.html', context)