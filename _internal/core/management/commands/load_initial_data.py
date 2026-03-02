"""Management command to load initial factory employee data from the C++ codebase."""
from django.core.management.base import BaseCommand
from factory.models import FactoryEmployee
from datetime import date


class Command(BaseCommand):
    help = 'Load initial factory employee data from the legacy system'

    def handle(self, *args, **options):
        employees = [
            {'name': 'Ajit', 'basic_salary': 13000, 'position': 'Worker'},
            {'name': 'Malek', 'basic_salary': 13000, 'position': 'Worker'},
            {'name': 'Mamun2', 'basic_salary': 12500, 'position': 'Worker'},
            {'name': 'Shahjahan', 'basic_salary': 12500, 'position': 'Worker'},
            {'name': 'Tutul', 'basic_salary': 11500, 'position': 'Worker'},
            {'name': 'Shajol', 'basic_salary': 9000, 'position': 'Worker'},
            {'name': 'Dulal', 'basic_salary': 12500, 'position': 'Worker'},
            {'name': 'Sabbir', 'basic_salary': 7500, 'position': 'Worker'},
            {'name': 'Imran', 'basic_salary': 12500, 'position': 'Worker'},
            {'name': 'Miraj', 'basic_salary': 12800, 'position': 'Worker'},
            {'name': 'Bachchu', 'basic_salary': 12000, 'position': 'Worker'},
            {'name': 'Zubayer', 'basic_salary': 11500, 'position': 'Worker'},
            {'name': 'Ataur', 'basic_salary': 12000, 'position': 'Worker'},
            {'name': 'Almas', 'basic_salary': 11500, 'position': 'Worker'},
            {'name': 'Shorif', 'basic_salary': 11000, 'position': 'Worker'},
            {'name': 'Tutul2', 'basic_salary': 6000, 'position': 'Helper'},
            {'name': 'Kashem', 'basic_salary': 26000, 'position': 'Senior Worker'},
            {'name': 'Shofiullah', 'basic_salary': 16000, 'position': 'Senior Worker'},
            {'name': 'Mamun', 'basic_salary': 16000, 'position': 'Senior Worker'},
            {'name': 'Rubel', 'basic_salary': 13000, 'position': 'Worker'},
            {'name': 'Biplob', 'basic_salary': 9500, 'position': 'Worker'},
            {'name': 'Masud', 'basic_salary': 7300, 'position': 'Helper'},
        ]

        created_count = 0
        for emp_data in employees:
            obj, created = FactoryEmployee.objects.get_or_create(
                name=emp_data['name'],
                defaults={
                    'basic_salary': emp_data['basic_salary'],
                    'position': emp_data['position'],
                    'join_date': date(2024, 1, 1),
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {emp_data['name']} (৳{emp_data['basic_salary']:,})")
                )
            else:
                self.stdout.write(f"  - Exists: {emp_data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count} new employees. Total: {FactoryEmployee.objects.count()}'
        ))
