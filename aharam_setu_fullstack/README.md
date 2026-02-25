# Aharam Setu Full-Stack Starter (Food Bridge)

A humanitarian-first food rescue platform.

## Modules

- `backend/` - FastAPI role-based API (provider / ngo / admin)
- `ngo_web/` - NGO dashboard (HTML + Bootstrap + JS)
- `provider_app_flutter/` - Provider Android app starter (Flutter)

## Workflow Logic

`Posted -> NGO Accepted -> Pickup Started -> Food Collected -> Delivered`

Rules implemented:
- Provider can create donations and view tracking.
- NGO can accept and update stages only for assigned donation.
- Admin can monitor and reassign.

## Backend Database Structure (mapped)

### donations
- donationId
- providerId
- foodType
- quantity
- category
- freshnessTime
- pickupLocation
- imageUrl
- status
- assignedNgo
- volunteerName
- createdAt
- updatedAt
- availableFrom
- availableTo
- isVeg

### users
- userId
- name
- email
- role

### impactMetrics
- mealsServed
- foodSavedKg
- ngosActive
- responseTime

## Run Backend

```powershell
cd aharam_setu_fullstack/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run NGO Dashboard

1. Open `ngo_web/index.html` in browser.
2. Set `localStorage.API_BASE_URL` to your API URL if not localhost.

## Provider App APK Build

1. Create a Flutter app and replace its `lib` + `pubspec.yaml` with `provider_app_flutter` content.
2. Build with public backend URL:

```powershell
flutter build apk --release --dart-define=BASE_URL=https://YOUR_PUBLIC_API_URL
```

## Firebase Note

Firebase Hosting cannot run FastAPI directly.
Use one of:
- Cloud Run (recommended with Firebase ecosystem)
- Render / Railway / Azure App Service

Then point both NGO web and Provider APK to that public API URL.
