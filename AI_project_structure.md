# AI suggested project structure

```txt
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── endpoints.py
│   │   └── models.py
│   ├── core
│   │   ├── __init__.py
│   │   └── security.py
│   └── services
│       ├── __init__.py
│       └── tika.py
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_endpoints.py
    └── test_tika_service.py
```