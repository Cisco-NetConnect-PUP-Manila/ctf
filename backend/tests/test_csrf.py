from app.core.config import settings


def test_cross_origin_login_is_rejected(client):
    response = client.post('/auth/login', json={'email': 'x@example.com', 'password': 'wrong'}, headers={'Origin': 'https://attacker.example'})
    assert response.status_code == 403
    assert response.json()['code'] == 'CSRF_REJECTED'


def test_simple_browser_form_is_rejected(client):
    client.headers.pop('X-CSRF-Protection')
    assert client.post('/auth/login', json={'email': 'x@example.com', 'password': 'wrong'}).status_code == 403


def test_cookie_without_origin_is_rejected(client):
    client.headers.pop('Origin')
    client.cookies.set(settings.session_cookie_name, 'some-token')
    assert client.post('/auth/logout').json()['code'] == 'CSRF_REJECTED'


def test_public_cli_without_cookie_remains_supported(client):
    client.headers.pop('Origin')
    client.headers.pop('X-CSRF-Protection')
    assert client.post('/auth/login', json={'email': 'x@example.com', 'password': 'wrong'}).status_code == 401
