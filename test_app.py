import unittest
import json
import io
from app import app, DB_PATH
from PIL import Image

class TestSiTugas(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SiTugas", response.data)

    def test_get_tasks(self):
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_get_stats(self):
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        stats = json.loads(response.data)
        self.assertIn("total_tasks", stats)
        self.assertIn("percent_saved", stats)
        self.assertIn("by_role", stats)

    def test_create_task_with_image_compression(self):
        # Buat dummy image 1600x1200
        img = Image.new('RGB', (1600, 1200), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        raw_size = img_bytes.tell()
        img_bytes.seek(0)

        data = {
            'role': 'satpam',
            'task_title': 'Uji Coba Patroli Pos 1',
            'officer_name': 'Test Officer',
            'shift': 'Shift 1 (Pagi 07:00-15:00)',
            'location': 'Pos 1 Depan',
            'status': 'selesai',
            'description': 'Tes deskripsi tugas satpam',
            'task_time': '2026-10-23T08:00',
            'original_size': str(raw_size),
            'photo': (img_bytes, 'test_camera.jpg')
        }

        response = self.client.post("/api/tasks", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
        res_data = json.loads(response.data)
        self.assertIn("task_id", res_data)
        
        # Bersihkan data test
        task_id = res_data["task_id"]
        del_resp = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(del_resp.status_code, 200)

if __name__ == "__main__":
    unittest.main()
