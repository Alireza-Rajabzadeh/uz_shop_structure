# Plan: Create Vendor Domain

## Goal

Create a new `domains/vendor/` domain mirroring the `domains/customer/` structure, with:
- Custom user model (AbstractBaseUser) with phone-based authentication
- `national_id` field on the Vendor model
- VendorStatus model (reference table)
- VendorPreference model (one-to-one)
- **No** address model
- Full auth flows (register, login, phone verification, password reset)
- Admin API (list, detail, status list)
- JWT authentication with `user_type='vendor'`

## Directory Structure

```
back/domains/vendor/
├── __init__.py
├── apps.py
├── admin.py
├── auth.py
├── urls.py
├── views.py
├── admin_views.py
├── enums/
│   └── VendorStatusEnum.py
├── models/
│   ├── __init__.py
│   ├── vendor_status.py
│   ├── vendor.py
│   └── preference.py
├── serializers/
│   ├── __init__.py
│   ├── vendor.py
│   └── admin.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   └── vendor_service.py
├── tests.py
└── migrations/
    └── __init__.py
```

---

## Step-by-Step Implementation

### 1. Domain Skeleton

**File: `domains/vendor/__init__.py`**
- Empty file.

**File: `domains/vendor/apps.py`**
```python
from django.apps import AppConfig

class VendorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.vendor'
```

---

### 2. Models

**File: `domains/vendor/enums/VendorStatusEnum.py`**
```python
from enum import Enum

class VendorStatusEnum(Enum):
    ACTIVE = 1
    INACTIVE = 2
    PENDING = 3
    BANNED = 4
```

**File: `domains/vendor/models/vendor_status.py`**
```python
from django.db import models

class VendorStatus(models.Model):
    class Meta:
        db_table = "vendor_status"
        verbose_name_plural = "vendor statuses"

    name = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

**File: `domains/vendor/models/vendor.py`**
- Fields: first_name, last_name, email, phone, national_id, status (FK), vendor_code, date_of_birth, gender, email_verified_at, phone_verified_at, last_login, created_at, updated_at
- AbstractBaseUser with phone as USERNAME_FIELD
- VendorManager (BaseUserManager) normalizing phone
- CheckConstraint on phone format
- Auto-generated vendor_code (VEN-XXXXX)
- UniqueConstraint on national_id
- Phone normalization on save()

**File: `domains/vendor/models/preference.py`**
```python
class VendorPreference(models.Model):
    class Meta:
        db_table = "vendor_preference"

    vendor = models.OneToOneField(
        "Vendor",
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    receive_order_emails = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=True)
    receive_push_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.vendor.vendor_code}"
```

**File: `domains/vendor/models/__init__.py`**
```python
from .vendor_status import VendorStatus
from .vendor import Vendor
from .preference import VendorPreference
```

---

### 3. JWT Authentication

**File: `domains/vendor/auth.py`**
```python
class VendorJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None

    def get_user(self, validated_token):
        if validated_token.get("user_type") != "vendor":
            raise AuthenticationFailed("Invalid token type.")
        user_id = validated_token["user_id"]
        try:
            vendor = Vendor.objects.select_related("status").get(id=user_id)
        except Vendor.DoesNotExist as exc:
            raise AuthenticationFailed("Vendor not found.") from exc
        if not vendor.status.is_active:
            raise AuthenticationFailed("Vendor account is inactive.")
        if api_settings.CHECK_REVOKE_TOKEN and validated_token.get(
            api_settings.REVOKE_TOKEN_CLAIM
        ) != get_md5_hash_password(vendor.password):
            raise AuthenticationFailed("The vendor's password has been changed.")
        return vendor
```

---

### 4. Services

**File: `domains/vendor/services/vendor_service.py`**
- Extends BaseService
- `search(ordering, search, **filters)` - admin search with ordering mapping
- `get_vendor(vendor_id)` - select_related status
- `update_vendor(vendor, **data)` - update fields

**File: `domains/vendor/services/auth_service.py`**
- `VendorAuthService` with methods:
  - `register(validated_data)` - create vendor, set password, create preference, return auth response
  - `request_login_confirmation(phone, password, ttl)` - authenticate, generate code, send SMS
  - `confirm_login(request_id, code)` - verify code, update last_login, return tokens
  - `request_phone_confirmation(vendor, ttl)` - generate phone verification code
  - `confirm_phone(vendor, request_id, code)` - verify phone
  - `request_password_reset(phone, ttl)` - generate reset code
  - `reset_password(request_id, code, new_password)` - reset password
  - `update_profile(vendor, validated_data)` - update profile fields
  - `change_password(vendor, current_password, new_password)` - change password
  - `get_profile(vendor)` - return profile dict
  - `_build_auth_response(vendor)` - generate JWT with user_type='vendor'
  - `_authenticate_vendor(phone, password)` - verify credentials
  - `_credential_fingerprint(vendor)` - HMAC fingerprint
  - `_mask_phone(phone)` - mask phone for display

- Custom exceptions: VendorConfirmationError, VendorConfirmationThrottled, VendorConfirmationUnavailable

---

### 5. Serializers

**File: `domains/vendor/serializers/vendor.py`**
- `VendorRegisterSerializer` - first_name, last_name, email, phone, national_id, password, password_confirmation, date_of_birth, gender
- `VendorLoginSerializer` - phone, password
- `VendorLoginConfirmationSerializer` - request_id, code
- `VendorPhoneConfirmationSerializer` - request_id, code
- `VendorPasswordForgotSerializer` - phone
- `VendorPasswordForgotConfirmationSerializer` - request_id, code, new_password, new_password_confirmation
- `VendorProfileSerializer` - ModelSerializer for read
- `VendorUpdateSerializer` - ModelSerializer for update (first_name, last_name, email, date_of_birth, gender)
- `VendorPasswordChangeSerializer` - current_password, new_password, new_password_confirmation
- `VendorPreferenceSerializer` - ModelSerializer for preference

**File: `domains/vendor/serializers/admin.py`**
- `AdminVendorListQuerySerializer` - filter fields (id, search, status_id, gender, vendor_code, first_name, last_name, email, phone, national_id, date ranges, ordering)
- `VendorStatusSerializer` - ModelSerializer
- `AdminVendorSerializer` - ModelSerializer with nested status

**File: `domains/vendor/serializers/__init__.py`**
- Re-export all serializers

---

### 6. Views

**File: `domains/vendor/views.py`**
- `VendorRegister` - AllowAny, POST
- `VendorLogin` - AllowAny, POST
- `VendorLoginConfirmation` - AllowAny, POST
- `VendorPasswordForgot` - AllowAny, POST
- `VendorPasswordForgotConfirmation` - AllowAny, POST
- `VendorPhoneConfirmationRequest` - IsAuthenticated, POST
- `VendorPhoneConfirmationVerify` - IsAuthenticated, POST
- `VendorMe` - IsAuthenticated, GET/PATCH
- `VendorChangePassword` - IsAuthenticated, POST
- `VendorPreferenceView` - IsAuthenticated, GET/PATCH

**File: `domains/vendor/admin_views.py`**
- `AdminAPIView` - base with AdminJWTAuthentication + AdminModelPermissions
- `AdminVendorList` - GET with pagination, search, filter
- `AdminVendorDetail` - GET, PATCH
- `AdminVendorStatusList` - GET

---

### 7. URLs

**File: `domains/vendor/urls.py`**
```python
urlpatterns = [
    path("register", VendorRegister.as_view()),
    path("login", VendorLogin.as_view()),
    path("login/confirmation", VendorLoginConfirmation.as_view()),
    path("password/forgot", VendorPasswordForgot.as_view()),
    path("password/forgot/confirmation", VendorPasswordForgotConfirmation.as_view()),
    path("me/phone/confirmation", VendorPhoneConfirmationRequest.as_view()),
    path("me/phone/confirmation/verify", VendorPhoneConfirmationVerify.as_view()),
    path("me", VendorMe.as_view()),
    path("me/password", VendorChangePassword.as_view()),
    path("preferences", VendorPreferenceView.as_view()),
    path("vendors", AdminVendorList.as_view()),
    path("vendors/<int:vendor_id>", AdminVendorDetail.as_view()),
    path("statuses", AdminVendorStatusList.as_view()),
]
```

---

### 8. Admin Registration

**File: `domains/vendor/admin.py`**
- Register VendorStatus, Vendor, VendorPreference with appropriate list_display, list_filter, search_fields

---

### 9. Integration

**File: `config/settings.py`**
- Add `"domains.vendor.apps.VendorConfig"` to INSTALLED_APPS

**File: `config/urls.py`**
- Add `path("api/vendor/", include("domains.vendor.urls"))`

---

### 10. Migration

- Run `python manage.py makemigrations vendor` to generate initial migration

---

## Key Design Decisions

1. **national_id** is a unique, indexed field on the Vendor model (not on Customer)
2. **No address model** - vendors don't need shipping addresses
3. **VendorCode** format: `VEN-XXXXX` (vs customer's `CUS-XXXXX`)
4. **JWT user_type**: `'vendor'` (vs customer's `'customer'`)
5. **Confirmed request purposes**: `vendor_login`, `vendor_phone_verification`, `vendor_password_reset`
6. **Phone normalization**: Reuse `core.utils.phone.normalize_phone`
7. **BaseService**: Reuse `core.services.base.BaseService` for CRUD operations
8. **Status FK**: `on_delete=models.PROTECT` (cannot delete status if vendors reference it)
9. **Preference FK**: `on_delete=models.CASCADE` (delete with vendor)

---

## Files to Create

1. `back/domains/vendor/__init__.py`
2. `back/domains/vendor/apps.py`
3. `back/domains/vendor/admin.py`
4. `back/domains/vendor/auth.py`
5. `back/domains/vendor/urls.py`
6. `back/domains/vendor/views.py`
7. `back/domains/vendor/admin_views.py`
8. `back/domains/vendor/enums/__init__.py`
9. `back/domains/vendor/enums/VendorStatusEnum.py`
10. `back/domains/vendor/models/__init__.py`
11. `back/domains/vendor/models/vendor_status.py`
12. `back/domains/vendor/models/vendor.py`
13. `back/domains/vendor/models/preference.py`
14. `back/domains/vendor/serializers/__init__.py`
15. `back/domains/vendor/serializers/vendor.py`
16. `back/domains/vendor/serializers/admin.py`
17. `back/domains/vendor/services/__init__.py`
18. `back/domains/vendor/services/auth_service.py`
19. `back/domains/vendor/services/vendor_service.py`
20. `back/domains/vendor/tests.py`
21. `back/domains/vendor/migrations/__init__.py`

## Files to Modify

1. `back/config/settings.py` - Add VendorConfig to INSTALLED_APPS
2. `back/config/urls.py` - Add /api/vendor/ route

---

## Verification

1. Run `python manage.py check` from `back/`
2. Run `python manage.py makemigrations vendor`
3. Run `python manage.py migrate`
4. Run `python manage.py test domains.vendor.tests`
