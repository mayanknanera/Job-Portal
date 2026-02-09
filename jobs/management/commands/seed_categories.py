from django.core.management.base import BaseCommand
from jobs.models import JobCategory, Industry

class Command(BaseCommand):
    help = 'Seed job categories and industries'

    def handle(self, *args, **options):
        # Categories
        categories = [
            'Software Development', 'Data Science', 'Marketing', 'Sales', 
            'Design', 'Customer Support', 'Human Resources', 'Finance',
            'Operations', 'Product Management'
        ]
        
        for cat in categories:
            JobCategory.objects.get_or_create(name=cat)
        
        # Industries
        industries = [
            'Technology', 'Healthcare', 'Finance', 'Education', 'Retail',
            'Manufacturing', 'Consulting', 'Media', 'Government', 'Non-Profit'
        ]
        
        for ind in industries:
            Industry.objects.get_or_create(name=ind)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded categories and industries'))