# Stage 1: Build UI
FROM node:22-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ .
RUN npm run build

# Stage 2: Run API
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy API code
COPY api/ ./api/

# Copy UI build from Stage 1
COPY --from=ui-build /app/ui/dist ./ui/dist

# Expose port
EXPOSE 8000

# Run FastAPI
# Note: We run from /app so that "api.main" module resolution works
# and relative paths to ../ui/dist work as expected
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
