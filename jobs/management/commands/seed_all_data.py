from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User, EmployerProfile, JobSeekerProfile
from jobs.models import Job, JobCategory, Industry


class Command(BaseCommand):
    help = 'Seeds the database with sample employers, job seekers, and jobs'

    def handle(self, *args, **kwargs):
        credentials = []
        
        # Create categories and industries
        self.stdout.write('Creating categories and industries...')
        tech_category, _ = JobCategory.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Technology and IT related jobs'}
        )
        marketing_category, _ = JobCategory.objects.get_or_create(
            name='Marketing',
            defaults={'description': 'Marketing and advertising jobs'}
        )
        finance_category, _ = JobCategory.objects.get_or_create(
            name='Finance',
            defaults={'description': 'Finance and accounting jobs'}
        )
        design_category, _ = JobCategory.objects.get_or_create(
            name='Design',
            defaults={'description': 'Design and creative jobs'}
        )
        
        it_industry, _ = Industry.objects.get_or_create(
            name='Information Technology',
            defaults={'description': 'IT and software industry'}
        )
        finance_industry, _ = Industry.objects.get_or_create(
            name='Finance',
            defaults={'description': 'Financial services industry'}
        )
        healthcare_industry, _ = Industry.objects.get_or_create(
            name='Healthcare',
            defaults={'description': 'Healthcare and medical industry'}
        )

        # Create employers
        self.stdout.write('Creating employers...')
        employers_data = [
            {
                'email': 'employer1@techcorp.com',
                'password': 'tech123',
                'company_name': 'TechCorp Solutions',
                'company_description': 'Leading software development company specializing in cloud solutions',
                'location': 'San Francisco, CA',
                'website': 'https://techcorp.example.com'
            },
            {
                'email': 'employer2@innovate.com',
                'password': 'innovate123',
                'company_name': 'Innovate Labs',
                'company_description': 'Startup focused on AI and machine learning products',
                'location': 'New York, NY',
                'website': 'https://innovatelabs.example.com'
            },
            {
                'email': 'employer3@digitalwave.com',
                'password': 'digital123',
                'company_name': 'Digital Wave Agency',
                'company_description': 'Full-service digital marketing and design agency',
                'location': 'Los Angeles, CA',
                'website': 'https://digitalwave.example.com'
            },
            {
                'email': 'employer4@fintech.com',
                'password': 'fintech123',
                'company_name': 'FinTech Pro',
                'company_description': 'Financial technology solutions for modern businesses',
                'location': 'Chicago, IL',
                'website': 'https://fintechpro.example.com'
            },
            {
                'email': 'employer5@cloudnine.com',
                'password': 'cloud123',
                'company_name': 'Cloud Nine Systems',
                'company_description': 'Enterprise cloud infrastructure and DevOps services',
                'location': 'Seattle, WA',
                'website': 'https://cloudnine.example.com'
            },
        ]

        employer_profiles = []
        for emp_data in employers_data:
            user, created = User.objects.get_or_create(
                email=emp_data['email'],
                defaults={
                    'role': 'EMPLOYER',
                    'is_role_confirmed': True
                }
            )
            if created:
                user.set_password(emp_data['password'])
                user.save()
                credentials.append({
                    'type': 'Employer',
                    'email': emp_data['email'],
                    'password': emp_data['password'],
                    'company': emp_data['company_name']
                })
                self.stdout.write(self.style.SUCCESS(f"Created employer: {emp_data['email']}"))

            profile, _ = EmployerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': emp_data['company_name'],
                    'company_description': emp_data['company_description'],
                    'location': emp_data['location'],
                    'website': emp_data['website']
                }
            )
            employer_profiles.append(profile)

        # Create job seekers
        self.stdout.write('\nCreating job seekers...')
        seekers_data = [
            {
                'email': 'john.doe@email.com',
                'password': 'john123',
                'full_name': 'John Doe',
                'phone': '+1-555-0101',
                'skills': 'Python, Django, REST API, PostgreSQL, Docker',
                'experience': '5'
            },
            {
                'email': 'jane.smith@email.com',
                'password': 'jane123',
                'full_name': 'Jane Smith',
                'phone': '+1-555-0102',
                'skills': 'React, TypeScript, JavaScript, CSS, HTML',
                'experience': '3'
            },
            {
                'email': 'mike.johnson@email.com',
                'password': 'mike123',
                'full_name': 'Mike Johnson',
                'phone': '+1-555-0103',
                'skills': 'AWS, Kubernetes, Docker, Jenkins, Terraform',
                'experience': '4'
            },
            {
                'email': 'sarah.williams@email.com',
                'password': 'sarah123',
                'full_name': 'Sarah Williams',
                'phone': '+1-555-0104',
                'skills': 'UI/UX Design, Figma, Adobe XD, Prototyping',
                'experience': '2'
            },
            {
                'email': 'david.brown@email.com',
                'password': 'david123',
                'full_name': 'David Brown',
                'phone': '+1-555-0105',
                'skills': 'Node.js, Express, MongoDB, React, JavaScript',
                'experience': '3'
            },
            {
                'email': 'emily.davis@email.com',
                'password': 'emily123',
                'full_name': 'Emily Davis',
                'phone': '+1-555-0106',
                'skills': 'Python, Machine Learning, TensorFlow, Data Analysis',
                'experience': '4'
            },
            {
                'email': 'alex.wilson@email.com',
                'password': 'alex123',
                'full_name': 'Alex Wilson',
                'phone': '+1-555-0107',
                'skills': 'Swift, iOS, SwiftUI, Xcode, Mobile Development',
                'experience': '3'
            },
            {
                'email': 'lisa.martinez@email.com',
                'password': 'lisa123',
                'full_name': 'Lisa Martinez',
                'phone': '+1-555-0108',
                'skills': 'SEO, Google Ads, Social Media Marketing, Analytics',
                'experience': '2'
            },
        ]

        for seeker_data in seekers_data:
            user, created = User.objects.get_or_create(
                email=seeker_data['email'],
                defaults={
                    'role': 'JOB_SEEKER',
                    'is_role_confirmed': True
                }
            )
            if created:
                user.set_password(seeker_data['password'])
                user.save()
                credentials.append({
                    'type': 'Job Seeker',
                    'email': seeker_data['email'],
                    'password': seeker_data['password'],
                    'name': seeker_data['full_name']
                })
                self.stdout.write(self.style.SUCCESS(f"Created job seeker: {seeker_data['email']}"))

            JobSeekerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': seeker_data['full_name'],
                    'phone': seeker_data['phone'],
                    'skills': seeker_data['skills'],
                    'experience': seeker_data['experience']
                }
            )

        # Create jobs for each employer
        self.stdout.write('\nCreating jobs...')
        jobs_data = [
            # TechCorp Solutions jobs
            {
                'employer_index': 0,
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team. You will work on building scalable APIs and microservices using Django and FastAPI.',
                'location': 'San Francisco, CA',
                'skills_required': 'Python, Django, REST API, PostgreSQL, Docker, Redis',
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
                'employer_index': 0,
                'title': 'DevOps Engineer',
                'description': 'Manage our cloud infrastructure and CI/CD pipelines. Experience with AWS and Kubernetes required.',
                'location': 'San Francisco, CA',
                'skills_required': 'AWS, Kubernetes, Docker, Jenkins, Terraform, Linux',
                'experience_required': 4,
                'salary_min': 110000,
                'salary_max': 150000,
                'salary_display': '$110k - $150k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'REMOTE',
                'category': tech_category,
                'industry': it_industry,
            },
            # Innovate Labs jobs
            {
                'employer_index': 1,
                'title': 'Machine Learning Engineer',
                'description': 'Build and deploy ML models for our AI-powered products. Work with cutting-edge technologies.',
                'location': 'New York, NY',
                'skills_required': 'Python, TensorFlow, PyTorch, Machine Learning, Deep Learning',
                'experience_required': 3,
                'salary_min': 130000,
                'salary_max': 170000,
                'salary_display': '$130k - $170k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'employer_index': 1,
                'title': 'Data Scientist',
                'description': 'Extract insights from large datasets and build predictive models to drive business decisions.',
                'location': 'New York, NY',
                'skills_required': 'Python, SQL, Pandas, Scikit-learn, Statistics, Data Visualization',
                'experience_required': 2,
                'salary_min': 100000,
                'salary_max': 140000,
                'salary_display': '$100k - $140k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': it_industry,
            },
            # Digital Wave Agency jobs
            {
                'employer_index': 2,
                'title': 'Frontend React Developer',
                'description': 'Build modern, responsive web applications using React and TypeScript for our clients.',
                'location': 'Los Angeles, CA',
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
                'employer_index': 2,
                'title': 'UI/UX Designer',
                'description': 'Create beautiful and intuitive user interfaces for web and mobile applications.',
                'location': 'Los Angeles, CA',
                'skills_required': 'Figma, Adobe XD, Sketch, Prototyping, User Research',
                'experience_required': 2,
                'salary_min': 70000,
                'salary_max': 100000,
                'salary_display': '$70k - $100k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': design_category,
                'industry': it_industry,
            },
            {
                'employer_index': 2,
                'title': 'Digital Marketing Manager',
                'description': 'Lead digital marketing campaigns across multiple channels for diverse clients.',
                'location': 'Los Angeles, CA',
                'skills_required': 'SEO, Google Ads, Social Media, Content Marketing, Analytics',
                'experience_required': 4,
                'salary_min': 80000,
                'salary_max': 110000,
                'salary_display': '$80k - $110k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': marketing_category,
                'industry': it_industry,
            },
            # FinTech Pro jobs
            {
                'employer_index': 3,
                'title': 'Full Stack Developer',
                'description': 'Work on both frontend and backend of our financial applications. Node.js and React experience required.',
                'location': 'Chicago, IL',
                'skills_required': 'JavaScript, Node.js, React, MongoDB, Express, TypeScript',
                'experience_required': 3,
                'salary_min': 95000,
                'salary_max': 125000,
                'salary_display': '$95k - $125k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': finance_industry,
            },
            {
                'employer_index': 3,
                'title': 'Backend Java Developer',
                'description': 'Build robust backend services for our financial platform using Java and Spring Boot.',
                'location': 'Chicago, IL',
                'skills_required': 'Java, Spring Boot, Microservices, SQL, REST API',
                'experience_required': 4,
                'salary_min': 105000,
                'salary_max': 140000,
                'salary_display': '$105k - $140k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': finance_industry,
            },
            # Cloud Nine Systems jobs
            {
                'employer_index': 4,
                'title': 'Cloud Solutions Architect',
                'description': 'Design and implement cloud infrastructure solutions for enterprise clients.',
                'location': 'Seattle, WA',
                'skills_required': 'AWS, Azure, Cloud Architecture, Terraform, Kubernetes',
                'experience_required': 6,
                'salary_min': 140000,
                'salary_max': 180000,
                'salary_display': '$140k - $180k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'REMOTE',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'employer_index': 4,
                'title': 'Site Reliability Engineer',
                'description': 'Ensure high availability and performance of our cloud infrastructure.',
                'location': 'Seattle, WA',
                'skills_required': 'Linux, Python, Kubernetes, Monitoring, Automation',
                'experience_required': 4,
                'salary_min': 115000,
                'salary_max': 155000,
                'salary_display': '$115k - $155k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'employer_index': 4,
                'title': 'Junior DevOps Engineer',
                'description': 'Entry-level position for recent graduates interested in DevOps and cloud technologies.',
                'location': 'Seattle, WA',
                'skills_required': 'Linux, Git, Docker, Basic AWS, Python or Bash',
                'experience_required': 0,
                'salary_min': 70000,
                'salary_max': 90000,
                'salary_display': '$70k - $90k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': it_industry,
            },
            # Additional jobs across employers
            {
                'employer_index': 0,
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
                'employer_index': 1,
                'title': 'Mobile App Developer (iOS)',
                'description': 'Develop native iOS applications using Swift and SwiftUI.',
                'location': 'New York, NY',
                'skills_required': 'Swift, SwiftUI, iOS, Xcode, REST API',
                'experience_required': 3,
                'salary_min': 95000,
                'salary_max': 135000,
                'salary_display': '$95k - $135k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'HYBRID',
                'category': tech_category,
                'industry': it_industry,
            },
            {
                'employer_index': 3,
                'title': 'Security Engineer',
                'description': 'Protect our financial systems and ensure compliance with security standards.',
                'location': 'Chicago, IL',
                'skills_required': 'Security, Penetration Testing, OWASP, Cryptography, Compliance',
                'experience_required': 5,
                'salary_min': 120000,
                'salary_max': 160000,
                'salary_display': '$120k - $160k',
                'job_type': 'FULL_TIME',
                'work_location_type': 'ONSITE',
                'category': tech_category,
                'industry': finance_industry,
            },
        ]

        created_count = 0
        for job_data in jobs_data:
            employer = employer_profiles[job_data.pop('employer_index')]
            slug = slugify(f"{job_data['title']}-{employer.company_name}")
            
            job, created = Job.objects.get_or_create(
                slug=slug,
                defaults={
                    **job_data,
                    'employer': employer,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created job: {job.title} at {employer.company_name}'))

        # Write credentials to file
        self.stdout.write('\nWriting credentials to file...')
        with open('test_credentials.txt', 'w') as f:
            f.write('=' * 80 + '\n')
            f.write('TEST CREDENTIALS FOR JOB PORTAL\n')
            f.write('=' * 80 + '\n\n')
            
            f.write('EMPLOYERS:\n')
            f.write('-' * 80 + '\n')
            for cred in credentials:
                if cred['type'] == 'Employer':
                    f.write(f"Company: {cred['company']}\n")
                    f.write(f"Email: {cred['email']}\n")
                    f.write(f"Password: {cred['password']}\n")
                    f.write('-' * 80 + '\n')
            
            f.write('\nJOB SEEKERS:\n')
            f.write('-' * 80 + '\n')
            for cred in credentials:
                if cred['type'] == 'Job Seeker':
                    f.write(f"Name: {cred['name']}\n")
                    f.write(f"Email: {cred['email']}\n")
                    f.write(f"Password: {cred['password']}\n")
                    f.write('-' * 80 + '\n')

        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {len([c for c in credentials if c["type"] == "Employer"])} employers'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len([c for c in credentials if c["type"] == "Job Seeker"])} job seekers'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} jobs'))
        self.stdout.write(self.style.SUCCESS(f'✓ Credentials saved to test_credentials.txt'))
