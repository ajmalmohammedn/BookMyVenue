# accounts/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        data = sociallogin.account.data_data

        # Google data
        email = data.get("email")
        name = data.get("name")
        is_email_verified = data.get("email_verified", False)
        profile_photo = data.get("picture")

        # customize your model
        user.email = email
        user.full_name = name
        user.profile_photo = profile_photo
        user.is_email_verified = is_email_verified
                
        user.save()
        return user