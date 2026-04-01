from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class YearField(models.PositiveSmallIntegerField):
    def __init__(self, *args, min_year=1900, max_year=datetime.now().year+10, **kwargs):
        self.min_year           = min_year
        self.max_year           = max_year
        kwargs['choices']       = [(r, str(r)) for r in range(min_year, max_year)]
        kwargs['validators']    = [MinValueValidator(min_year), MaxValueValidator(max_year)]
        
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs    = super().deconstruct()
        kwargs['min_year']          = self.min_year
        kwargs['max_year']          = self.max_year

        del kwargs['choices']
        del kwargs['validators']
        
        return name, path, args, kwargs