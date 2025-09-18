from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
import base64
import re
import logging
import os
from .forms import RetinopathyTestForm
from .models import RetinopathyTest, DietaryRecommendation, Country
from .ai_model import detector
from django.views.decorators.csrf import ensure_csrf_cookie

def home(request):
    return render(request, 'home.html')
@ensure_csrf_cookie
def detect_retinopathy(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Handle file upload from AJAX
            if is_ajax and request.FILES.get('image'):
                form = RetinopathyTestForm(request.POST, request.FILES)
                if form.is_valid():
                    country = form.cleaned_data['country']
                    image_file = request.FILES['image']
                    
                    # Process image and get result
                    result, confidence = detector.predict(image_file.read())
                    
                    # Get stage info (number and description)
                    stage_info = get_dr_stage_info(result)
                    
                    # Save test record
                    test = RetinopathyTest(
                        image=image_file,
                        result=stage_info['key'],
                        confidence=confidence
                    )
                    test.save()
                    
                    # Get dietary recommendation for this specific stage
                    diet_recommendation = DietaryRecommendation.objects.filter(
                        condition=stage_info['key'],
                        country=country
                    ).first()
                    
                    if not diet_recommendation:
                        diet_recommendation = DietaryRecommendation.objects.filter(
                            condition=stage_info['key'],
                            is_default=True
                        ).first()
                    
                    return JsonResponse({
                        'success': True,
                        'result': stage_info['stage'],
                        'stage_description': stage_info['description'],
                        'stage_number': stage_info['number'],
                        'stage_key': stage_info['key'],
                        'test_id': test.id,
                        'country_id': country.id
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid form data. Please check your inputs.'
                    }, status=400)
            
            # Handle base64 image from camera
            elif is_ajax and request.POST.get('image_data'):
                image_data = request.POST['image_data']
                country_id = request.POST.get('country')
                
                if not country_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'Country selection is required'
                    }, status=400)
                
                try:
                    country = Country.objects.get(id=country_id)
                except Country.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid country selected'
                    }, status=400)
                
                # Clean and decode base64 image
                image_data = re.sub(r'^data:image/.+;base64,', '', image_data)
                image_data = base64.b64decode(image_data)
                
                # Process image and get result
                result, confidence = detector.predict(image_data)
                
                # Get stage info (number and description)
                stage_info = get_dr_stage_info(result)
                
                # Save test record
                test = RetinopathyTest(
                    result=stage_info['key'],
                    confidence=confidence
                )
                test.save()
                
                return JsonResponse({
                    'success': True,
                    'result': stage_info['stage'],
                    'stage_description': stage_info['description'],
                    'stage_number': stage_info['number'],
                    'stage_key': stage_info['key'],
                    'test_id': test.id,
                    'country_id': country.id,
                    
                })
            
            # Handle regular form submission (non-AJAX)
            else:
                form = RetinopathyTestForm(request.POST, request.FILES)
                if form.is_valid():
                    country = form.cleaned_data['country']
                    image_file = request.FILES['image']
                    
                    # Process image and get result
                    result, confidence = detector.predict(image_file.read())
                    
                    # Get stage info (number and description)
                    stage_info = get_dr_stage_info(result)
                    
                    # Save test record
                    test = RetinopathyTest(
                        image=image_file,
                        result=stage_info['key'],
                        confidence=confidence
                    )
                    test.save()
                    
                    # Get dietary recommendation for this specific stage
                    diet_recommendation = DietaryRecommendation.objects.filter(
                        condition=stage_info['key'],
                        country=country
                    ).first()
                    
                    if not diet_recommendation:
                        diet_recommendation = DietaryRecommendation.objects.filter(
                            condition=stage_info['key'],
                            is_default=True
                        ).first()
                    
                    return render(request, 'detection_result.html', {
                        'test': test,
                        'diet_recommendation': diet_recommendation,
                        'selected_country': country,
                        'stage_info': stage_info
                    })
                
                return render(request, 'detect_retinopathy.html', {'form': form})
                
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in detect_retinopathy: {str(e)}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Server error: {str(e)}'
                }, status=500)
            else:
                form = RetinopathyTestForm()
                return render(request, 'detect_retinopathy.html', {
                    'form': form,
                    'error_message': f'An error occurred: {str(e)}'
                })
    
    else:
        form = RetinopathyTestForm()
    
    return render(request, 'detect_retinopathy.html', {'form': form})

def get_dr_stage_info(result):
    """Return DR stage information with number, description, and key (matching model choices)"""
    cleaned_result = result.strip().lower()

    stages = {
        'no dr': {
            'number': 'Stage 0',
            'stage': 'No Diabetic Retinopathy',
            'description': 'No signs of diabetic retinopathy detected...',
            'key': 'no_dr'
        },
        'mild npdr': {
            'number': 'Stage 1',
            'stage': 'Mild Non-Proliferative Diabetic Retinopathy',
            'description': 'Early stage with minor microaneurysms...',
            'key': 'mild'
        },
        'moderate npdr': {
            'number': 'Stage 2',
            'stage': 'Moderate Non-Proliferative Diabetic Retinopathy',
            'description': 'Moderate stage with blocked vessels...',
            'key': 'moderate'
        },
        'severe npdr': {
            'number': 'Stage 3',
            'stage': 'Severe Non-Proliferative Diabetic Retinopathy',
            'description': 'Advanced stage with many blocked vessels...',
            'key': 'severe'
        },
        'pdr': {
            'number': 'Stage 4',
            'stage': 'Proliferative Diabetic Retinopathy',
            'description': 'Most advanced stage with fragile new vessels...',
            'key': 'proliferative'
        },
        'proliferative dr': {
            'number': 'Stage 4',
            'stage': 'Proliferative Diabetic Retinopathy',
            'description': 'Most advanced stage with fragile new vessels...',
            'key': 'proliferative'
        },
        'proliferative diabetic retinopathy': {
            'number': 'Stage 4',
            'stage': 'Proliferative Diabetic Retinopathy',
            'description': 'Most advanced stage with fragile new vessels...',
            'key': 'proliferative'
        },
    }

    # Exact match
    if cleaned_result in stages:
        return stages[cleaned_result]

    # Partial match
    for key, stage_info in stages.items():
        if key in cleaned_result or cleaned_result in key:
            return stage_info

    # Fallbacks
    if 'proliferative' in cleaned_result:
        return stages['pdr']
    elif 'mild' in cleaned_result:
        return stages['mild npdr']
    elif 'moderate' in cleaned_result:
        return stages['moderate npdr']
    elif 'severe' in cleaned_result:
        return stages['severe npdr']
    elif 'no' in cleaned_result or 'normal' in cleaned_result:
        return stages['no dr']

    return {
        'number': 'Unknown Stage',
        'stage': result,
        'description': 'Consult with your ophthalmologist...',
        'key': cleaned_result.replace(' ', '_')
    }


def change_language(request):
    """
    Change the session language for multilingual support
    """
    if request.method == 'POST':
        language = request.POST.get('language')
        if language in [lang[0] for lang in settings.LANGUAGES]:
            request.session['django_language'] = language
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def test_history(request):
    tests = RetinopathyTest.objects.all().order_by('-created_at')[:10]
    return render(request, 'test_history.html', {'tests': tests})

def dietary_recommendations(request):
    stage = request.GET.get("stage")   # e.g., "proliferative"
    country_id = request.GET.get("country")

    recommendation = None

    if stage:
        if country_id:
            # Try country-specific recommendation
            recommendation = DietaryRecommendation.objects.filter(
                condition=stage,
                country_id=country_id
            ).first()

        if not recommendation:
            # Try default recommendation
            recommendation = DietaryRecommendation.objects.filter(
                condition=stage,
                is_default=True
            ).first()

    context = {
        "recommendation": recommendation,
        "stage": stage,
    }
    return render(request, "dietary_recommendations.html", context)


def detection_result(request, test_id):
    try:
        test = RetinopathyTest.objects.get(id=test_id)
        diet_recommendation = DietaryRecommendation.objects.filter(condition=test.result).first()
        
        return render(request, 'detection_result.html', {
            'test': test,
            'diet_recommendation': diet_recommendation
        })
    except RetinopathyTest.DoesNotExist:
        return redirect('detect_retinopathy')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def delete_test(request, test_id):
    try:
        test = RetinopathyTest.objects.get(id=test_id)
        if test.image and os.path.isfile(test.image.path):
            os.remove(test.image.path)
        test.delete()
        return redirect('test_history')
    except RetinopathyTest.DoesNotExist:
        return redirect('test_history')

def test_detail(request, test_id):
    try:
        test = RetinopathyTest.objects.get(id=test_id)
        diet_recommendation = DietaryRecommendation.objects.filter(condition=test.result).first()
        
        return render(request, 'test_detail.html', {
            'test': test,
            'diet_recommendation': diet_recommendation
        })
    except RetinopathyTest.DoesNotExist:
        return redirect('test_history')
