import json
from django.core.management.base import BaseCommand
from core.models import Country

class Command(BaseCommand):
    help = 'Veritabanına dünya ülkelerini ekler'

    def handle(self, *args, **kwargs):
        # Kapsamlı Ülke Listesi
        countries = [
            "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", 
            "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", 
            "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", 
            "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", 
            "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", 
            "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", 
            "Congo (Crazzaville)", "Congo (Kinshasa)", "Costa Rica", "Croatia", "Cuba", "Cyprus", 
            "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", 
            "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", 
            "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", 
            "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", 
            "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", 
            "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast", "Jamaica", 
            "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", 
            "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", 
            "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", 
            "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", 
            "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", 
            "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", 
            "Nicaragua", "Niger", "Nigeria", "North Macedonia", "North Korea", "Norway", "Oman", 
            "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", 
            "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", 
            "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", 
            "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", 
            "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", 
            "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", 
            "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", 
            "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Türkiye", 
            "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", 
            "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", 
            "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
        ]

        self.stdout.write("Ülkeler veritabanına ekleniyor...")
        
        count = 0
        for country_name in countries:
            # get_or_create kullanarak mükerrer kayıtları engelliyoruz
            obj, created = Country.objects.get_or_create(name=country_name)
            if created:
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'İşlem tamamlandı. {count} yeni ülke eklendi.'))