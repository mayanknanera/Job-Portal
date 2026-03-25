from django.core.management.base import BaseCommand
from accounts.models import User, EmployerProfile
from jobs.models import Job


class Command(BaseCommand):
    help = 'Fix employer profiles and list all companies with their jobs'

    def handle(self, *args, **kwargs):
        # Fix employer profiles
        self.stdout.write('Fixing employer profiles...\n')
        
        employers_mapping = {
            'employer@example.com': {
                'company_name': 'Tech Solutions Inc',
                'company_description': 'Leading technology solutions provider',
                'location': 'San Francisco, CA',
                'website': 'https://techsolutions.example.com'
            },
            'employer1@techcorp.com': {
                'company_name': 'TechCorp Solutions',
                'company_description': 'Leading software development company specializing in cloud solutions',
                'location': 'San Francisco, CA',
                'website': 'https://techcorp.example.com'
            },
            'employer2@innovate.com': {
                'company_name': 'Innovate Labs',
                'company_description': 'Startup focused on AI and machine learning products',
                'location': 'New York, NY',
                'website': 'https://innovatelabs.example.com'
            },
            'employer3@digitalwave.com': {
                'company_name': 'Digital Wave Agency',
                'company_description': 'Full-service digital marketing and design agency',
                'location': 'Los Angeles, CA',
                'website': 'https://digitalwave.example.com'
            },
            'employer4@fintech.com': {
                'company_name': 'FinTech Pro',
                'company_description': 'Financial technology solutions for modern businesses',
                'location': 'Chicago, IL',
                'website': 'https://fintechpro.example.com'
            },
            'employer5@cloudnine.com': {
                'company_name': 'Cloud Nine Systems',
                'company_description': 'Enterprise cloud infrastructure and DevOps services',
                'location': 'Seattle, WA',
                'website': 'https://cloudnine.example.com'
            },
        }

        for email, data in employers_mapping.items():
            try:
                user = User.objects.get(email=email)
                profile = EmployerProfile.objects.get(user=user)
                profile.company_name = data['company_name']
                profile.company_description = data['company_description']
                profile.location = data['location']
                profile.website = data['website']
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Updated {data["company_name"]}'))
            except (User.DoesNotExist, EmployerProfile.DoesNotExist):
                self.stdout.write(self.style.WARNING(f'✗ User {email} not found'))

        # Generate comprehensive list
        self.stdout.write('\n' + '='*80)
        self.stdout.write('GENERATING COMPANIES AND JOBS LIST')
        self.stdout.write('='*80 + '\n')

        output_lines = []
        output_lines.append('='*80)
        output_lines.append('COMPANIES AND JOBS LIST')
        output_lines.append('='*80)
        output_lines.append('')

        employers = EmployerProfile.objects.all().order_by('company_name')
        
        for employer in employers:
            output_lines.append(f'\nCOMPANY: {employer.company_name}')
            output_lines.append('-'*80)
            output_lines.append(f'Location: {employer.location or "Not specified"}')
            output_lines.append(f'Website: {employer.website or "Not specified"}')
            output_lines.append(f'Description: {employer.company_description or "Not specified"}')
            output_lines.append(f'Contact Email: {employer.user.email}')
            
            jobs = Job.objects.filter(employer=employer, is_active=True).order_by('title')
            output_lines.append(f'\nJobs Posted ({jobs.count()}):')
            output_lines.append('')
            
            if jobs.exists():
                for idx, job in enumerate(jobs, 1):
                    output_lines.append(f'  {idx}. {job.title}')
                    output_lines.append(f'     Location: {job.location}')
                    output_lines.append(f'     Type: {job.get_job_type_display()} | {job.get_work_location_type_display()}')
                    output_lines.append(f'     Experience: {job.experience_required} years')
                    output_lines.append(f'     Salary: {job.salary_display or "Not specified"}')
                    output_lines.append(f'     Skills: {job.skills_required}')
                    output_lines.append(f'     Posted: {job.created_at.strftime("%Y-%m-%d")}')
                    output_lines.append('')
            else:
                output_lines.append('  No active jobs posted')
                output_lines.append('')
            
            output_lines.append('='*80)

        # Write to file
        with open('jobs_and_companies_list.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        # Print summary
        total_companies = employers.count()
        total_jobs = Job.objects.filter(is_active=True).count()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Fixed employer profiles'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total Companies: {total_companies}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total Active Jobs: {total_jobs}'))
        self.stdout.write(self.style.SUCCESS(f'✓ List saved to jobs_and_companies_list.txt'))
