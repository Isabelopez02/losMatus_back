import uvicorn
import os

if __name__ == '__main__':
    # Azure inyecta la variable PORT, usamos 8000 por defecto
    port = int(os.environ.get("PORT", 8000))
    # reload=False para producción
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
