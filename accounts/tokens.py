from django.contrib.auth.tokens import PasswordResetTokenGenerator

# We will reuse Django's default token generator behavior
account_activation_token = PasswordResetTokenGenerator()