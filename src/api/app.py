import os
import random
from flask import Flask, jsonify, render_template_string
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
PrometheusMetrics(app)  # Tự động xuất metrics tại /metrics

ERROR_RATE = float(os.getenv("ERROR_RATE", "0"))
VERSION = os.getenv("VERSION", "v1")

# Giao diện HTML Dashboard cao cấp
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>W10 - Platform Delivery & Security Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151b2c;
            --border-color: #222d44;
            --accent-primary: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.15);
            --gradient-text: linear-gradient(135deg, #60a5fa, #3b82f6);
            --text-main: #f8fafc;
            --text-secondary: #94a3b8;
            --success: #10b981;
            --danger: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            width: 100%;
            max-width: 900px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 100px rgba(59, 130, 246, 0.05);
            position: relative;
        }

        .container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8, transparent, transparent);
            border-radius: 24px;
            z-index: -1;
            opacity: 0.5;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            padding: 6px 16px;
            border-radius: 100px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.2);
            margin-bottom: 16px;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 8px;
            background: var(--gradient-text);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .lead {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: 0 10px 20px var(--accent-glow);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .icon-wrapper {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: rgba(59, 130, 246, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-primary);
        }

        .card h3 {
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .card p {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .status-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
        }

        .status-active {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }

        .status-version {
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent-primary);
        }

        footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }

        .mono {
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge">
                <i data-lucide="shield-check" style="width: 16px; height: 16px;"></i>
                Cluster Secure & Enforced
            </div>
            <h1>Secure API Platform</h1>
            <p class="lead">Giao diện Dashboard Giám Sát Progressive Delivery & Bảo Mật</p>
        </header>

        <div class="grid">
            <!-- Card 1: API Status -->
            <div class="card">
                <div class="card-header">
                    <div class="icon-wrapper">
                        <i data-lucide="server"></i>
                    </div>
                    <span class="status-badge status-version">{{ version }}</span>
                </div>
                <h3>API Service</h3>
                <p>Ứng dụng Flask đang hoạt động ổn định và sẵn sàng nhận tải từ Client.</p>
            </div>

            <!-- Card 2: Canary Strategy -->
            <div class="card">
                <div class="card-header">
                    <div class="icon-wrapper" style="color: #f59e0b; background: rgba(245, 158, 11, 0.1);">
                        <i data-lucide="git-pull-request"></i>
                    </div>
                    <span class="status-badge" style="background: rgba(245, 158, 11, 0.1); color: #f59e0b;">Canary Active</span>
                </div>
                <h3>Argo Rollouts</h3>
                <p>Chiến lược Progressive Delivery (10% → 50% → 100%) kèm phân tích tự động (Automated Analysis).</p>
            </div>

            <!-- Card 3: Gatekeeper Admission -->
            <div class="card">
                <div class="card-header">
                    <div class="icon-wrapper" style="color: #10b981; background: rgba(16, 185, 129, 0.1);">
                        <i data-lucide="lock"></i>
                    </div>
                    <span class="status-badge status-active">Enforcing</span>
                </div>
                <h3>OPA Gatekeeper</h3>
                <p>Áp dụng 4 quy tắc an toàn và chính sách giới hạn bản sao (Replicas) cho tài nguyên Deployment.</p>
            </div>

            <!-- Card 4: Error Rate Injected -->
            <div class="card">
                <div class="card-header">
                    <div class="icon-wrapper" style="color: #ef4444; background: rgba(239, 68, 68, 0.1);">
                        <i data-lucide="alert-triangle"></i>
                    </div>
                    <span class="status-badge" style="background: rgba(239, 68, 68, 0.1); color: #ef4444;">Rate: {{ error_rate }}</span>
                </div>
                <h3>Mô phỏng lỗi</h3>
                <p>Tỷ lệ lỗi mô phỏng (Error Injection Rate) để kiểm thử cơ chế tự động rollback của Argo Rollouts.</p>
            </div>
        </div>

        <footer>
            <span>Trạng thái: <strong style="color: var(--success);">Running</strong></span>
            <span class="mono">W10 - Secure & Operate</span>
        </footer>
    </div>

    <script>
        // Khởi tạo các icon từ thư viện Lucide
        lucide.createIcons();
    </script>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(HTML_TEMPLATE, version=VERSION, error_rate=f"{int(ERROR_RATE * 100)}%")

@app.get("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
