from django.test import TestCase

from accounts.admin import UserChangeForm, UserCreationForm
from accounts.models import User


class UserAdminFormTests(TestCase):
    def test_user_creation_form_hashes_password(self):
        form = UserCreationForm(
            data={
                "email": "admin@example.com",
                "full_name": "Admin User",
                "phone_number": "+447700900123",
                "role": "admin",
                "city": "London",
                "state": "England",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=False)

        self.assertNotEqual(user.password, "StrongPassword123!")
        self.assertTrue(user.check_password("StrongPassword123!"))

    def test_user_change_form_keeps_existing_hashed_password(self):
        user = User(
            email="owner@example.com",
            full_name="Venue Owner",
            phone_number="+447700900124",
            role="venue_owner",
            city="London",
            state="England",
        )
        user.set_password("OwnerPassword123!")
        form = UserChangeForm(instance=user)

        self.assertEqual(form.clean_password(), user.password)
