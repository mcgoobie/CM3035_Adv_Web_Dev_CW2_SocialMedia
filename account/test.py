# Start od code I wrote
from account.models import *
from account.forms import *

from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

import json
import re
from rest_framework import status
from django.test import TestCase, Client


class AccountModels(TestCase):
    # Set up new test user account obj
    def setUp(self):
        self.test_user = UserAccount(
            email='testuser@gmail.com', f_name='john', l_name='doe', gender='M', dob='1999-01-01', username='john_doe'
        )
        UserAccount.objects.create(
            email="jane@gmail.com", f_name='jane', l_name='smith', gender='F', dob='1995-03-01', username='jane_smith'
        )
        self.test_post = UserPosts(
            content='My test post', user_account=self.test_user
        )

    """
    Test Case 1 : Valid User_Account Model
    """

    def test_user_account_model(self):
        self.assertEqual(self.test_user.__str__(), 'john_doe')

    """
    Test Case 2 : Fetch Test User_Account Model Object
    """

    def test_tester_user_account_model_obj(self):
        test_user = UserAccount.objects.get(f_name='jane')

        self.assertEqual(test_user.get_f_name(), 'jane')

    """
    Test Case 3 : Valid User_Post Model
    """

    def test_user_posts_model(self):
        self.assertEqual(self.test_post.__str__(), 'By: john_doe')


class AccountForms(TestCase):
    def setUp(self):
        UserAccount.objects.create(
            email="jane@gmail.com", f_name='jane', l_name='smith', gender='F', dob='1995-03-01', username='jane_smith'
        )
    """
    Test Case 1 : Valid User Registration Forms
    """

    def test_valid_reg_form(self):
        form_data = {
            'f_name': 'John',
            'l_name': 'Doe',
            'gender': 'M',
            'dob': '2000-01-01',
            'email': 'john_doe@gmail.com',
            'username': 'john_doe',
            'password1': 'Qwerty$123',
            'password2': 'Qwerty$123',
        }

        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    """
    Test Case 2 : invalid User Registration Form
    """

    def test_invalid_email_in_reg_form(self):
        form_data = self.client.post('home', data={
            'f_name': 'Jane',
            'l_name': 'Smithe',
            'gender': 'F',
            'dob': '2001-01-01',
            'email': 'jane@gmail.com',
            'username': 'jane_smith',
            'password1': 'Qwerty$123',
            'password2': 'Qwerty$123',
        },)

        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.clean_email(), None)
        self.assertEquals(form.clean_username(), None)

# End of code I wrote
