import csv
import os
from django.core.management.base import BaseCommand
from core.models import Personnel, Country, Institution, JobTitle, ExpertiseType

class Command(BaseCommand):
    help = 'CSV dosyasından personelleri içe aktarır. (Noktalı Virgül Destekli)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Yüklenecek CSV dosyasının yolu')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'Dosya bulunamadı: {csv_file_path}'))
            return

        # 1. MEVCUT ÜLKELERİ HAFIZAYA AL
        existing_countries = {c.name.upper(): c for c in Country.objects.all()}

        # 2. ÜLKE EŞLEŞTİRME LİSTESİ
        country_mapping = {
            "TURCHIA": "Türkiye",
            "TURKEY": "Türkiye",
            "TR": "Türkiye",
            "BELGIUM": "Belgium",
            "BULGARIA": "Bulgaria",
            "CROATIA": "Croatia",
            "CYPRUS": "Cyprus",
            "CZECH REPUBLIC": "Czech Republic",
            "DENMARK": "Denmark",
            "FRANCE": "France",
            "GERMANY": "Germany",
            "GREECE": "Greece",
            "ICELAND": "Iceland",
            "ITALY": "Italy",
            "LATVIA": "Latvia",
            "MOLDOVA": "Moldova",
            "NETHERLANDS": "Netherlands",
            "POLAND": "Poland",
            "PORTUGAL": "Portugal",
            "ROMANIA": "Romania",
            "SERBIA": "Serbia",
            "SPAIN": "Spain",
            "SWEDEN": "Sweden",
            "UNITED KINGDOM": "United Kingdom",
            "UK": "United Kingdom",
            "USA": "United States",
            "BOSNIA AND HERZEGOVINA": "Bosnia and Herzegovina",
            "NORTH MACEDONIA": "North Macedonia",
        }

        self.stdout.write("İçe aktarım başlıyor (Delimiter: Noktalı Virgül)...")

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            # ÖNEMLİ DÜZELTME: delimiter=';' eklendi
            reader = csv.DictReader(csvfile, delimiter=';')
            
            count_created = 0
            count_updated = 0
            
            for row in reader:
                try:
                    # --- A. İSİM AYRIŞTIRMA ---
                    full_name = row.get('NAME', '').strip()
                    if not full_name: # İsim yoksa satırı atla
                        continue

                    if ' ' in full_name:
                        parts = full_name.rsplit(' ', 1)
                        first_name = parts[0]
                        last_name = parts[1]
                    else:
                        first_name = full_name
                        last_name = ""

                    # --- B. ÜLKE EŞLEŞTİRME ---
                    raw_country = row.get('COUNTRY', '').strip().upper()
                    country_obj = None

                    if raw_country in country_mapping:
                        target_db_name = country_mapping[raw_country]
                        country_obj = existing_countries.get(target_db_name.upper())
                        if not country_obj:
                            country_obj, _ = Country.objects.get_or_create(name=target_db_name)
                            existing_countries[target_db_name.upper()] = country_obj
                    else:
                        if raw_country in existing_countries:
                            country_obj = existing_countries[raw_country]
                        else:
                            clean_name = raw_country.title()
                            # Boş ülke gelirse oluşturma
                            if clean_name: 
                                country_obj, _ = Country.objects.get_or_create(name=clean_name)
                                existing_countries[clean_name.upper()] = country_obj

                    # --- C. KURUM ---
                    inst_name = row.get('INSTITUTION', '').strip()
                    institution_obj = None
                    if inst_name:
                        institution_obj, _ = Institution.objects.get_or_create(name=inst_name)

                    # --- D. UZMANLIK ---
                    exp_code = row.get('EXPERTISE', '').strip()
                    primary_expertise_obj = None
                    if exp_code:
                        primary_expertise_obj, _ = ExpertiseType.objects.get_or_create(code=exp_code)

                    # --- E. E-MAIL KONTROLÜ ---
                    email = row.get('E-MAIL', '').strip()
                    if not email:
                        self.stdout.write(self.style.WARNING(f"E-mail eksik, satır atlandı: {full_name}"))
                        continue

                    # --- F. KAYIT İŞLEMİ ---
                    personnel, created = Personnel.objects.update_or_create(
                        email=email,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'gender': row.get('MALE/FEMALE', 'M').strip()[0].upper(),
                            'sq_number': row.get('SQ', '').strip(),
                            'country': country_obj,
                            'institution': institution_obj,
                            'primary_expertise': primary_expertise_obj,
                            'professional_profile': row.get('PROFESSIONAL PROFILE', ''),
                            # CSV'de iki tane SPECIFIC EXPERTISE sütunu var, DictReader sonuncusunu alır.
                            'specific_expertise_details': row.get('SPECIFIC EXPERTISE', ''),
                            'mobile': row.get('MOBILE', ''),
                            'insurance_code': row.get('CODE FOR INSURANCE', ''),
                            'notes': row.get('NOTES', ''),
                            'private_notes': row.get('private e-mail/other notes', '')
                        }
                    )

                    # --- G. JOB TITLE ---
                    job_title_str = row.get('JOB TITLE', '').strip()
                    if job_title_str:
                        jt_obj, _ = JobTitle.objects.get_or_create(title=job_title_str)
                        personnel.job_titles.add(jt_obj)

                    if created:
                        count_created += 1
                        self.stdout.write(f"Eklendi: {full_name} ({country_obj.name if country_obj else '-'})")
                    else:
                        count_updated += 1
                        # self.stdout.write(f"Güncellendi: {full_name}") 

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Hata ({full_name}): {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f'\nİŞLEM TAMAMLANDI:\n- {count_created} yeni personel eklendi.\n- {count_updated} mevcut personel güncellendi.'))