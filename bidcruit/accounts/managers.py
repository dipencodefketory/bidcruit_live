from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_candidate(self,first_name,ip,device_type,browser_type,browser_version,os_type,os_version,
                         last_name, email,referral_number,referred_by,password=None):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            referral_number=referral_number,
            referred_by=referred_by,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_candidate = True
        user.is_active = False
        user.save(using=self.db)
        return user

    def create_company(self, company_name, website ,ip ,device_type ,browser_type ,browser_version ,os_type ,os_version, email, password=None):
        user = self.model(
            company_name=company_name,
            website=website,
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_company = True
        user.is_active = False
        user.save(using=self.db)
        return user

    def create_internal_company(self, ip ,device_type ,browser_type ,browser_version ,os_type ,os_version,first_name,last_name, email, password=None):
        user = self.model(
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=first_name
        )
        user.set_password(password)
        user.is_company = True
        user.is_active = True
        user.save(using=self.db)
        return user

    def create_agency_freelancer(self, first_name, last_name,email, ip, device_type, browser_type, browser_version, os_type,
                      os_version, password=None):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_agency = True
        user.is_active = False
        user.save(using=self.db)
        return user
    def create_agency(self, company_name,website,email, ip, device_type, browser_type, browser_version, os_type,
                      os_version, password=None):
        user = self.model(
            
            company_name=company_name,
            website=website,
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_agency = True
        user.is_active = False
        user.save(using=self.db)
        return user
    def create_agency_user(self, first_name,last_name,email, ip, device_type, browser_type, browser_version, os_type,
                      os_version, password=None):
        user = self.model(
            
            first_name=first_name,
            last_name=last_name,
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_agency = True
        user.is_active = True
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

    def apply_candidate(self, first_name, ip, device_type, browser_type, browser_version, os_type, os_version,
                        last_name, email, referral_number, password=None):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            ip=ip,
            device_type=device_type,
            browser_type=browser_type,
            browser_version=browser_version,
            os_type=os_type,
            os_version=os_version,
            referral_number=referral_number,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_candidate = True
        user.is_active = False
        user.save(using=self.db)
        return user