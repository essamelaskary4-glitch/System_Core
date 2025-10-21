from fastapi import FastAPI

# [GEU-CORE]: تم توليد هذا السكربت بواسطة نظام System_Core
app = FastAPI(title="Inventory Management API - PROJ_INV_MGMT")

@app.get("/")
def read_root():
    return {"Hello": "World", "Service": "Inventory Management API is running!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    # محاكاة لاسترجاع عنصر في المخزون
    return {"item_id": item_id, "name": f"Item {item_id}", "quantity": 100}