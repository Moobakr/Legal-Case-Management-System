from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import random

# Create your views here.

def index(request):
    users = Client.objects.all()
    return render(request, 'base.html')

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name_ar = request.POST.get('first_name_ar')
        last_name_ar = request.POST.get('last_name_ar')
        first_name_en = request.POST.get('first_name_en')
        last_name_en = request.POST.get('last_name_en')
        national_id = request.POST.get('national_id')
        address = request.POST.get('address')
        city = request.POST.get('city')
        gender = request.POST.get('gender')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('signup')
        
        if Client.objects.filter(national_id=national_id).exists():
            messages.error(request, 'National ID already exists.')
            return redirect('signup')

        # Create the User object
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create the Client object linked to the User
        client = Client.objects.create(
            user=user,
            username=username,
            password=password,
            email=email,
            first_name_ar=first_name_ar,
            last_name_ar=last_name_ar,
            first_name_en=first_name_en,
            last_name_en=last_name_en,
            national_id=national_id,
            address=address,
            city=city,
            gender=gender
        )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def get_client(request):
    if request.user.is_authenticated:
        return request.user.client_profile
    return None

def new_case(request):
    client = get_client(request)
    if not client:
        messages.error(request, 'Please login to file a case.')
        return redirect('login')

    if request.method == 'POST':
        title = request.POST.get('title')
        case_type = request.POST.get('case_type')
        description = request.POST.get('description')
        lawyer_id = request.POST.get('lawyer')
        court_id = request.POST.get('court')
        
        lawyer = get_object_or_404(Lawyer, id=lawyer_id)
        court = get_object_or_404(Court, id=court_id)
        
        # Generate a random hearing date between 15 and 45 days from now
        days_to_add = random.randint(15, 45)
        next_hearing_date = timezone.now().date() + timedelta(days=days_to_add)
        
        # Create the case
        case = LawsuitCase.objects.create(
            title=title,
            case_type=case_type,
            description=description,
            client=client,
            lawyer=lawyer,
            court=court,
            date_filed=timezone.now().date(),
            next_hearing_date=next_hearing_date,
            status='Open'
        )
        
        # Handle document uploads
        document_titles = request.POST.getlist('document_titles[]')
        document_types = request.POST.getlist('document_types[]')
        document_files = request.FILES.getlist('document_files[]')
        
        for title, doc_type, file in zip(document_titles, document_types, document_files):
            CaseDocument.objects.create(
                case=case,
                title=title,
                document_type=doc_type,
                file=file
            )
        
        # Handle participants
        participant_names = request.POST.getlist('participant_names[]')
        participant_roles = request.POST.getlist('participant_roles[]')
        participant_ids = request.POST.getlist('participant_ids[]')
        participant_contacts = request.POST.getlist('participant_contacts[]')
        
        for name, role, national_id, contact in zip(
            participant_names, participant_roles, participant_ids, participant_contacts
        ):
            CaseParticipant.objects.create(
                case=case,
                name=name,
                role=role,
                national_id=national_id,
                contact_info=contact
            )
        
        # Send email notification with hearing date
        send_case_notification_email(client, case)
        
        messages.success(
            request, 
            f'Case created successfully! Your hearing is scheduled for {next_hearing_date.strftime("%B %d, %Y")}. '
            'Check your email for details.'
        )
        return redirect('dashboard')
    
    # Get filter parameters
    case_type = request.GET.get('case_type', '')
    min_rating = request.GET.get('min_rating', 0)
    min_experience = request.GET.get('min_experience', 0)
    max_fee = request.GET.get('max_fee', float('inf'))
    search_query = request.GET.get('search', '')
    
    # Base query for recommended lawyers
    recommended_lawyers = Lawyer.objects.filter(
        available=True,
        location=client.city
    )
    
    # Apply filters
    if case_type:
        recommended_lawyers = recommended_lawyers.filter(specialization=case_type)
    if min_rating:
        recommended_lawyers = recommended_lawyers.filter(rating__gte=min_rating)
    if min_experience:
        recommended_lawyers = recommended_lawyers.filter(years_of_experience__gte=min_experience)
    if max_fee != float('inf'):
        recommended_lawyers = recommended_lawyers.filter(consultation_fee__lte=max_fee)
    if search_query:
        recommended_lawyers = recommended_lawyers.filter(
            Q(full_name__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(languages__icontains=search_query)
        )
    
    # Order by rating, success rate, and experience
    recommended_lawyers = recommended_lawyers.order_by('-rating', '-success_rate', '-years_of_experience')
    
    # Get recommended courts based on client's city
    recommended_courts = Court.objects.filter(
        location=client.city
    ).order_by('jurisdiction_level')
    
    return render(request, 'new_case.html', {
        'recommended_lawyers': recommended_lawyers,
        'recommended_courts': recommended_courts,
        'case_types': Lawyer.CASE_TYPES,
        'current_filters': {
            'case_type': case_type,
            'min_rating': min_rating,
            'min_experience': min_experience,
            'max_fee': max_fee,
            'search': search_query
        }
    })

def dashboard(request):
    client = get_client(request)
    if not client:
        messages.error(request, 'Please login to view your dashboard.')
        return redirect('login')

    # Get all cases for the client, ordered by date
    cases = LawsuitCase.objects.filter(client=client).order_by('-date_filed')
    
    # Calculate statistics
    total_cases = cases.count()
    active_cases = cases.filter(status='Open').count()
    upcoming_hearings = cases.filter(
        next_hearing_date__gte=timezone.now().date()
    ).count()
    
    return render(request, 'dashboard.html', {
        'cases': cases,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'upcoming_hearings': upcoming_hearings
    })

def case_details(request, case_id):
    client = get_client(request)
    if not client:
        messages.error(request, 'Please login to view case details.')
        return redirect('login')

    case = get_object_or_404(LawsuitCase, id=case_id, client=client)
    return render(request, 'case_details.html', {'case': case})

def send_case_notification_email(client, case):
    subject = f'Case Filed Successfully: {case.title}'
    message = f'''
    Dear {client.first_name_en} {client.last_name_en},

    Your case has been successfully filed. Here are the details:

    Case Title: {case.title}
    Case Type: {case.get_case_type_display()}
    Court: {case.court.name}
    Lawyer: {case.lawyer.full_name}
    Next Hearing Date: {case.next_hearing_date.strftime("%B %d, %Y")}
    Court Address: {case.court.location}

    Important Notes:
    - Please arrive at the court at least 30 minutes before the scheduled time
    - Bring all relevant documents and identification
    - Your lawyer will meet you at the court
    - If you need to reschedule, please contact your lawyer at least 48 hours before the hearing

    If you have any questions, please contact your assigned lawyer:
    Phone: {case.lawyer.phone}
    Email: {case.lawyer.email}

    Best regards,
    Legal Case Management System
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [client.email],
        fail_silently=False,
    )

@login_required
def profile(request):
    client = get_client(request)
    if not client:
        messages.error(request, 'Please login to view your profile.')
        return redirect('login')
    return render(request, 'profile.html', {'client': client})