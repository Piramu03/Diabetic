from django.contrib import admin
from .models import RetinopathyTest, DietaryRecommendation,Country

@admin.register(RetinopathyTest)
class RetinopathyTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'confidence_percentage', 'created_at', 'image_preview')
    list_filter = ('result', 'created_at')
    readonly_fields = ('created_at', 'image_preview', 'confidence_percentage')
    
    def confidence_percentage(self, obj):
        return f"{obj.confidence * 100:.2f}%"
    confidence_percentage.short_description = 'Confidence'
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />'
        return "No image"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'common_foods_preview')
    search_fields = ('name', 'code')
    list_per_page = 20
    
    def common_foods_preview(self, obj):
        return obj.common_foods[:100] + '...' if len(obj.common_foods) > 100 else obj.common_foods
    common_foods_preview.short_description = 'Common Foods'


@admin.register(DietaryRecommendation)
class DietaryRecommendationAdmin(admin.ModelAdmin):
    list_display = ('condition_display', 'country_name', 'is_default', 'get_food_count')
    list_filter = ('condition', 'country', 'is_default')
    search_fields = ('condition', 'country__name')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('condition', 'country', 'is_default', 'general_advice')
        }),
        ('Foods to Eat (Timing Based)', {
            'fields': (
                'morning_foods', 
                'midday_foods', 
                'evening_foods', 
                'snack_foods'
            )
        }),
        ('Foods to Avoid', {
            'fields': ('foods_to_avoid',)
        }),
        ('Eye Care Recommendations', {
            'fields': ('eye_care_recommendations',),
            'classes': ('collapse',)
        }),
    )
    
    def condition_display(self, obj):
        return obj.get_condition_display()
    condition_display.short_description = 'Condition'
    
    def country_name(self, obj):
        return obj.country.name if obj.country else 'Default'
    country_name.short_description = 'Country'
    
    def get_food_count(self, obj):
        foods = [
            obj.morning_foods, obj.midday_foods, 
            obj.evening_foods, obj.snack_foods
        ]
        return f"{sum(len(f.split(',')) for f in foods if f)} food items"
    get_food_count.short_description = 'Food Items'
