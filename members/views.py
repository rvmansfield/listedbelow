from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.views import View

from .forms import UpdateUserForm, UpdateProfileForm

from .forms import RegisterForm

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            #return redirect('/')
            next_url = request.GET.get('next', '/')  # Default to '/' if 'next' is not present
            print (next_url)
            return redirect(next_url)
       
        else:
            messages.success(request,"There was an error logging in")
            return redirect('login')

    else:
        return render(request,'login.html')
    
@login_required(login_url='login')
def user_profile(request):
     if request.method == 'POST':
        print("POST")
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)
        
        

        
        if user_form.is_valid() and profile_form.is_valid():
            
            #save user
            user_form.save()

            

            #save profile
            profile_obj = profile_form.save(commit=False)
            
            profile_obj.save()


            
            
            messages.success(request, 'Your profile is updated successfully')
            #return redirect(to='profile')
            
        
     else:
        
        user_form = UpdateUserForm(instance=request.user)
        
        profile_form = UpdateProfileForm(instance=request.user.profile)
        
        
        

     return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form,})


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            

            messages.success(request, 'Account created!!!!')

            return redirect(to='/login')

        return render(request, self.template_name, {'form': form})