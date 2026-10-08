import io
import json
import unittest
from app import create_app
from models import db, User, TechnicianProfile, RecruiterProfile
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

class MaintTechTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_landing_page(self):
        """Test GET / renders successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MaintTech", response.data)

    def test_technician_registration_and_login(self):
        """Test registration and login flow for a maintenance technician."""
        # Register technician
        response = self.client.post('/register', data={
            'role': 'technician',
            'email': 'mehdi.test@mainttech.ma',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'full_name': 'Mehdi Test',
            'city': 'Casablanca',
            'specialty': 'Automatisme',
            'experience_years': '5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify user in database
        user = User.query.filter_by(email='mehdi.test@mainttech.ma').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'technician')
        self.assertIsNotNone(user.technician_profile)
        self.assertEqual(user.technician_profile.full_name, 'Mehdi Test')

        # Logout
        self.client.get('/logout')

        # Login
        response = self.client.post('/login', data={
            'email': 'mehdi.test@mainttech.ma',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mehdi Test", response.data)

    def test_recruiter_registration(self):
        """Test registration for an industrial recruiter."""
        response = self.client.post('/register', data={
            'role': 'recruiter',
            'email': 'rh@usine-tanger.ma',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'company_name': 'Usine Automobile Tanger',
            'industry_type': 'Automobile',
            'city': 'Tanger',
            'phone': '+212 5 39 00 00 00'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        user = User.query.filter_by(email='rh@usine-tanger.ma').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'recruiter')
        self.assertEqual(user.recruiter_profile.company_name, 'Usine Automobile Tanger')

    def test_dynamic_api_talents_filtering(self):
        """Test /api/talents endpoint with filtering by city, specialty, experience, and search."""
        # Create technicians
        u1 = User(email='tech1@test.ma', role='technician')
        u1.set_password('pass123')
        db.session.add(u1)
        db.session.flush()

        p1 = TechnicianProfile(
            user_id=u1.id,
            full_name='Karim Automatisme',
            city='Tanger',
            specialty='Automatisme',
            experience_years=8,
            mobility=True,
            bio='Expert Siemens S7-1500'
        )
        p1.set_skills(['Siemens TIA Portal', 'KUKA'])
        db.session.add(p1)

        u2 = User(email='tech2@test.ma', role='technician')
        u2.set_password('pass123')
        db.session.add(u2)
        db.session.flush()

        p2 = TechnicianProfile(
            user_id=u2.id,
            full_name='Yassine Mecanique',
            city='Casablanca',
            specialty='Maintenance Mécanique',
            experience_years=3,
            mobility=False,
            bio='Lignage laser et pompes'
        )
        p2.set_skills(['Lignage Laser', 'Pompes'])
        db.session.add(p2)
        db.session.commit()

        # Query all
        res = self.client.get('/api/talents')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)

        # Filter by city=Tanger
        res = self.client.get('/api/talents?city=Tanger')
        data = json.loads(res.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['talents'][0]['city'], 'Tanger')

        # Filter by specialty=Maintenance Mécanique
        res = self.client.get('/api/talents?specialty=Maintenance Mécanique')
        data = json.loads(res.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['talents'][0]['specialty'], 'Maintenance Mécanique')

        # Filter by min_exp=5
        res = self.client.get('/api/talents?min_exp=5')
        data = json.loads(res.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['talents'][0]['experience_years'], 8)

        # Filter by search=Siemens
        res = self.client.get('/api/talents?search=Siemens')
        data = json.loads(res.data)
        self.assertEqual(data['count'], 1)

    def test_technician_profile_update_and_cv_upload(self):
        """Test technician dashboard profile editing and CV upload."""
        # Create and login technician
        u = User(email='tech.upload@test.ma', role='technician')
        u.set_password('pass123')
        db.session.add(u)
        db.session.commit()

        self.client.post('/login', data={'email': 'tech.upload@test.ma', 'password': 'pass123'})

        # Post update with CV file
        dummy_cv = (io.BytesIO(b"%PDF-1.4 dummy pdf content"), 'test_cv.pdf')
        res = self.client.post('/dashboard/technician', data={
            'full_name': 'Omar Electromecanicien',
            'phone': '+212 6 00 11 22 33',
            'city': 'Kénitra',
            'specialty': 'Electromécanique',
            'experience_years': '6',
            'mobility': '1',
            'bio': 'Spécialiste maintenance lignes continues',
            'skills_tags': ['Siemens TIA Portal', 'Festo Pneumatique'],
            'custom_skills': 'Altivar 71',
            'cv_file': dummy_cv
        }, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(res.status_code, 200)

        profile = TechnicianProfile.query.filter_by(user_id=u.id).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.full_name, 'Omar Electromecanicien')
        self.assertIn('Altivar 71', profile.skills_list)
        self.assertIsNotNone(profile.cv_filename)

    def test_technician_photo_upload_and_delete(self):
        """Test uploading profile photo, serving it, and deleting it."""
        u = User(email='tech.photo@test.ma', role='technician')
        u.set_password('pass123')
        db.session.add(u)
        db.session.commit()

        self.client.post('/login', data={'email': 'tech.photo@test.ma', 'password': 'pass123'})

        # Upload dummy PNG image
        dummy_img = (io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR dummy image bytes"), 'avatar.png')
        res = self.client.post('/dashboard/technician', data={
            'full_name': 'Hassan Photo Test',
            'photo_file': dummy_img
        }, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(res.status_code, 200)

        profile = TechnicianProfile.query.filter_by(user_id=u.id).first()
        self.assertIsNotNone(profile.photo_filename)
        self.assertTrue(profile.photo_filename.startswith('avatar_'))

        # Verify avatar serving route
        res_img = self.client.get(f'/uploads/avatars/{profile.photo_filename}')
        self.assertEqual(res_img.status_code, 200)

        # Delete photo
        res_del = self.client.post('/dashboard/technician/delete-photo', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        db.session.refresh(profile)
        self.assertIsNone(profile.photo_filename)

    def test_health_endpoint(self):
        """Test cloud health check endpoint /health."""
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('database'), 'connected')

    def test_404_error_page(self):
        """Test custom 404 error page renders properly."""
        res = self.client.get('/route-qui-n-existe-pas-404')
        self.assertEqual(res.status_code, 404)
        self.assertIn(b"404", response_data := res.data)
        self.assertIn(b"non identifi", response_data)

    def test_api_talents_sorting(self):
        """Test API sorting by experience ascending and descending."""
        u1 = User(email='sort1@test.ma', role='technician')
        u1.set_password('pass123')
        db.session.add(u1)
        db.session.flush()

        p1 = TechnicianProfile(user_id=u1.id, full_name='Junior Tech', experience_years=2, city='Casablanca')
        db.session.add(p1)

        u2 = User(email='sort2@test.ma', role='technician')
        u2.set_password('pass123')
        db.session.add(u2)
        db.session.flush()

        p2 = TechnicianProfile(user_id=u2.id, full_name='Senior Tech', experience_years=10, city='Tanger')
        db.session.add(p2)
        db.session.commit()

        # Ascending sort
        res_asc = self.client.get('/api/talents?sort=exp_asc')
        data_asc = json.loads(res_asc.data)['talents']
        self.assertEqual(data_asc[0]['experience_years'], 2)

        # Descending sort
        res_desc = self.client.get('/api/talents?sort=exp_desc')
        data_desc = json.loads(res_desc.data)['talents']
        self.assertEqual(data_desc[0]['experience_years'], 10)

if __name__ == '__main__':
    unittest.main()
