from fastapi import FastAPI

app = FastAPI(
    title="DevOps FastAPI Project",
    version="1.0.0"
)

PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Keyboard", "price": 2000},
    {"id": 3, "name": "Mouse", "price": 1000}
]


@app.get("/")
def home():
    return {
        "application": "devops-fastapi",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/test")
def test():
    return {
        "test":"successful"
    }


@app.get("/health/live")
def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    return {"status": "ready"}


@app.get("/api/v1/products")
def get_products():
    return {
        "count": len(PRODUCTS),
        "products": PRODUCTS
    }