from django.db import models

class RetinopathyTest(models.Model):
    image = models.ImageField(upload_to='retinopathy_images/', null=True, blank=True)
    
    result = models.CharField(max_length=50, choices=[
        ('no_dr', 'No Diabetic Retinopathy'),
        ('mild', 'Mild Diabetic Retinopathy'),
        ('moderate', 'Moderate Diabetic Retinopathy'),
        ('severe', 'Severe Diabetic Retinopathy'),
        ('proliferative', 'Proliferative Diabetic Retinopathy'),
    ])
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test {self.id} - {self.result}"


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, unique=True)
    common_foods = models.TextField(help_text="Common traditional foods in this country")

    def __str__(self):
        return self.name


class DietaryRecommendation(models.Model):
    condition = models.CharField(max_length=50, choices=[
        ('no_dr', 'No Diabetic Retinopathy'),
        ('mild', 'Mild Diabetic Retinopathy'),
        ('moderate', 'Moderate Diabetic Retinopathy'),
        ('severe', 'Severe Diabetic Retinopathy'),
        ('proliferative', 'Proliferative Diabetic Retinopathy'),
    ])
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False, help_text="Use as default for countries without specific recommendations")

    morning_foods = models.TextField(
        help_text="Foods to eat for breakfast (7-9 AM)",
        default="Whole grain cereal, Eggs, Greek yogurt"
    )
    midday_foods = models.TextField(
        help_text="Foods to eat for lunch (12-2 PM)",
        default="Grilled chicken salad, Vegetable soup"
    )
    evening_foods = models.TextField(
        help_text="Foods to eat for dinner (7-9 PM)",
        default="Baked fish, Steamed vegetables, Quinoa"
    )
    snack_foods = models.TextField(
        help_text="Foods to eat for snacks (10-11 AM, 4-5 PM)",
        default="Apple slices, Almonds, Carrot sticks"
    )

    foods_to_avoid = models.TextField(
        help_text="Foods to avoid completely",
        default="Sugary foods, Processed snacks, White bread"
    )
    
    general_advice = models.TextField(
        help_text="General dietary advice",
        default="Maintain balanced meals with controlled carbohydrates."
    )
    eye_exercises = models.TextField(
        help_text="Specific eye exercises for this condition",
        default="Eye rolling, Palming, Focus shifting exercises."
    )
    eye_care_recommendations = models.TextField(
        help_text="Eye care recommendations based on condition stage",
        default="Limit screen time, wear sunglasses outdoors, regular eye checkups."
    )

    class Meta:
        unique_together = ['condition', 'country']
        verbose_name = "Dietary Recommendation"
        verbose_name_plural = "Dietary Recommendations"

    def __str__(self):
        if self.country:
            return f"Diet for {self.get_condition_display()} - {self.country.name}"
        return f"Default Diet for {self.get_condition_display()}"
