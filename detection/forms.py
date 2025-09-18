from django import forms
from .models import Country

class RetinopathyTestForm(forms.Form):
    image = forms.ImageField(
        required=False,
        label="Retina Image",
        help_text="Upload an image of the retina for analysis",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        })
    )
    
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by('name'),
        required=True,
        label="Select Your Country",
        help_text="Choose your country for personalized dietary recommendations",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Country --"
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 10MB )")
            
            valid_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
            extension = image.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload JPG, PNG, or BMP.")
        return image
