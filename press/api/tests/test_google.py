# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from __future__ import annotations

import base64
import json
import time

import frappe
from frappe.tests.utils import FrappeTestCase

from press.api.google import id_token_claims

CLIENT_ID = "client.apps.googleusercontent.com"


def unsigned_token(**claims) -> str:
	def part(data: dict) -> str:
		return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

	return f"{part({'alg': 'RS256', 'typ': 'JWT'})}.{part(claims)}.c2lnbmF0dXJl"


def google_claims(**overrides) -> dict:
	claims = {
		"iss": "https://accounts.google.com",
		"aud": CLIENT_ID,
		"exp": int(time.time()) + 300,
		"email": "jane@example.com",
		"email_verified": True,
	}
	return {**claims, **overrides}


class TestGoogleIdTokenClaims(FrappeTestCase):
	def test_claims_are_returned_without_fetching_google_certificates(self):
		claims = id_token_claims(unsigned_token(**google_claims()), CLIENT_ID)
		self.assertEqual(claims["email"], "jane@example.com")

	def test_token_for_another_client_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "meant for another application"):
			id_token_claims(unsigned_token(**google_claims(aud="someone-else")), CLIENT_ID)

	def test_token_from_another_issuer_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "meant for another application"):
			id_token_claims(unsigned_token(**google_claims(iss="https://evil.example")), CLIENT_ID)

	def test_expired_token_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "sign-in expired"):
			id_token_claims(unsigned_token(**google_claims(exp=int(time.time()) - 10)), CLIENT_ID)

	def test_unverified_email_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "not verified"):
			id_token_claims(unsigned_token(**google_claims(email_verified=False)), CLIENT_ID)
