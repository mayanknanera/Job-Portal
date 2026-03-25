from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User, EmployerProfile
from jobs.models import Job, JobCategory, Industry


class Command(BaseCommand):
    help = 'Seeds the database with sample jobs'

    def handle(self, *args, **kwargs):
        # Create or get sample employer
        employer_user, created = User.objects.get_or_create(
            email='employer@example.com',
            defaults={
                'role': 'EMPLOYER',
                'is_role_confirmed': True
            }
        )
        if created:
            employer_user.set_password('password123')
            employer_user.save()
            self.stdout.write(self.style.SUCCESS('Created sample employer user'))

        employer_profile, created = EmployerProfile.objects.get_or_create(
            user=employer_user,
            defaults={
                'company_name': 'Tech Solutions Inc',
                'company_description': 'Leading technology solutions provider',
                'location': 'San Francisco, CA',
                'website': 'https://techsolutions.example.com'
            }
        )

        # Get or create categories and industries
        tech_category, _ = JobCategory.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Technology and IT related jobs'}
        )
        
        marketing_category, _ = JobCategory.objects.get_or_create(
            name='Marketing',
            defaults={'description': 'Marketing and advertising jobs'}
        )
        
        it_industry, _ = Industry.objects.get_or_create(
            name='Information Technology',
            defaults={'description': 'IT and software industry'}
        )

        # Sample jobs data
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team. You will work on building scalable APIs and microservices.',
                'location': 'San Francisco, CA',
                'skills_required': 'Python, Django, REST API, PostgreSQL, Docker',
                'experience_required': 5,
                'salary_min': 120000,
                'salary_max': 160000,
                'salary_display': '$120k - $160k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Frontend React Developer',
                'description': 'Join our frontend team to build modern, responsive web applications using React and TypeScript.',
                'location': 'Remote',
                'skills_required': 'React, TypeScript, JavaScript, CSS, HTML, Redux',
                'experience_required': 3,
                'salary_min': 90000,
                'salary_max': 130000,
                'salary_display': '$90k - $130k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'REMOTE',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'DevOps Engineer',
                'description': 'We need a DevOps engineer to manage our cloud infrastructure and CI/CD pipelines.',
                'location': 'New York, NY',
                'skills_required': 'AWS, Kubernetes, Docker, Jenkins, Terraform, Linux',
                'experience_required': 4,
                'salary_min': 110000,
                'salary_max': 150000,
                'salary_display': '$110k - $150k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Full Stack Developer',
                'description': 'Looking for a versatile full stack developer comfortable with both frontend and backend technologies.',
                'location': 'Austin, TX',
                'skills_required': 'JavaScript, Node.js, React, MongoDB, Express',
                'experience_required': 2,
                'salary_min': 80000,
                'salary_max': 110000,
                'salary_display': '$80k - $110k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Data Scientist',
                'description': 'Join our data team to build machine learning models and extract insights from large datasets.',
                'location': 'Boston, MA',
                'skills_required': 'Python, Machine Learning, TensorFlow, Pandas, SQL',
                'experience_required': 3,
                'salary_min': 100000,
                'salary_max': 140000,
                'salary_display': '$100k - $140k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Mobile App Developer (iOS)',
                'description': 'Develop native iOS applications using Swift and SwiftUI for our mobile platform.',
                'location': 'Seattle, WA',
                'skills_required': 'Swift, SwiftUI, iOS, Xcode, REST API',
                'experience_required': 3,
                'salary_min': 95000,
                'salary_max': 135000,
                'salary_display': '$95k - $135k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'REMOTE',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'UI/UX Designer',
                'description': 'Create beautiful and intuitive user interfaces for our web and mobile applications.',
                'location': 'Los Angeles, CA',
                'skills_required': 'Figma, Adobe XD, Sketch, Prototyping, User Research',
                'experience_required': 2,
                'salary_min': 70000,
                'salary_max': 100000,
                'salary_display': '$70k - $100k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Digital Marketing Specialist',
                'description': 'Plan and execute digital marketing campaigns across multiple channels.',
                'location': 'Chicago, IL',
                'skills_required': 'SEO, Google Ads, Social Media, Content Marketing, Analytics',
                'experience_required': 2,
                'salary_min': 60000,
                'salary_max': 85000,
                'salary_display': '$60k - $85k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': marketing_category,
                'industry': it_industry,
            },
            {
                'title': 'QA Automation Engineer',
                'description': 'Build and maintain automated testing frameworks for our applications.',
                'location': 'Remote',
                'skills_required': 'Selenium, Python, Jest, Cypress, Test Automation',
                'experience_required': 3,
                'salary_min': 85000,
                'salary_max': 115000,
                'salary_display': '$85k - $115k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'REMOTE',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'title': 'Junior Software Engineer',
                'description': 'Entry-level position for recent graduates. Learn and grow with our engineering team.',
                'location': 'Denver, CO',
                'skills_required': 'Python, JavaScript, Git, Problem Solving',
                'experience_required': 0,
                'salary_min': 65000,
                'salary_max': 85000,
                'salary_display': '$65k - $85k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': it_industry,
            },
        ]

        # Create jobs
        created_count = 0
        for job_data in jobs_data:
            slug = slugify(f"{job_data['title']}-{employer_profile.company_name}")
            
            job, created = Job.objects.get_or_create(
                slug=slug,
                defaults={
                    **job_data,
                    'employer': employer_profile,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created job: {job.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Job already exists: {job.title}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} new jobs!'))
