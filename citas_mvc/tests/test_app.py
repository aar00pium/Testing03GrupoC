import unittest
from app import app
import model
import os

class TestCitas(unittest.TestCase):

    def setUp(self):
        if os.path.exists("citas.db"):
            os.remove("citas.db")
        model.init_db()
        self.client = app.test_client()

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)

    def test_registrar_ok(self):
        res = self.client.post("/api/citas", json={
            "nombre_cliente": "Juan",
            "fecha": "2099-12-12",
            "hora": "10:00",
            "motivo": "Test"
        })
        self.assertEqual(res.status_code, 201)

    def test_registrar_error(self):
        res = self.client.post("/api/citas", json={})
        self.assertEqual(res.status_code, 400)

    def test_listar(self):
        res = self.client.get("/api/citas")
        self.assertEqual(res.status_code, 200)

    def test_buscar(self):
        self.client.post("/api/citas", json={
            "nombre_cliente": "Ana",
            "fecha": "2099-12-12",
            "hora": "11:00",
            "motivo": "Test"
        })
        res = self.client.get("/api/citas/buscar?nombre=Ana")
        self.assertEqual(res.status_code, 200)

    def test_cancelar(self):
        self.client.post("/api/citas", json={
            "nombre_cliente": "Luis",
            "fecha": "2099-12-12",
            "hora": "12:00",
            "motivo": "Test"
        })
        res = self.client.put("/api/citas/cancelar/1")
        self.assertEqual(res.status_code, 200)

    def test_reasignar(self):
        self.client.post("/api/citas", json={
            "nombre_cliente": "Pedro",
            "fecha": "2099-12-12",
            "hora": "13:00",
            "motivo": "Test"
        })
        res = self.client.put("/api/citas/reasignar/1", json={
            "fecha": "2099-12-13",
            "hora": "14:00"
        })
        self.assertEqual(res.status_code, 200)