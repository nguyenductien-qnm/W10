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
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            --bg-color: #03000a;
            --card-bg: rgba(13, 8, 28, 0.65);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-primary: #8b5cf6;
            --accent-secondary: #ec4899;
            --accent-glow: rgba(139, 92, 246, 0.25);
            --text-main: #f3f4f6;
            --text-secondary: #9ca3af;
            --success: #10b981;
            --warning: #f59e0b;
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
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.12) 0%, transparent 40%),
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
            position: relative;
        }

        /* Ambient floating orbs */
        .orb {
            position: absolute;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            filter: blur(100px);
            z-index: -1;
            opacity: 0.6;
            animation: float 12s infinite alternate ease-in-out;
        }
        .orb-1 {
            background: var(--accent-primary);
            top: 20%;
            left: 25%;
        }
        .orb-2 {
            background: var(--accent-secondary);
            bottom: 20%;
            right: 25%;
            animation-delay: -6s;
        }

        @keyframes float {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(30px, 20px) scale(1.15); }
        }

        .container {
            width: 100%;
            max-width: 540px;
            background: var(--card-bg);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 
                0 30px 60px -15px rgba(0, 0, 0, 0.8),
                0 0 50px -10px var(--accent-glow);
            position: relative;
            z-index: 10;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        }

        header {
            text-align: center;
            margin-bottom: 25px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(139, 92, 246, 0.12);
            color: #c084fc;
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid rgba(139, 92, 246, 0.2);
            margin-bottom: 12px;
        }

        h1 {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: 4px;
            background: linear-gradient(135deg, #fff 30%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .lead {
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 400;
        }

        /* Secret Key Section */
        .secret-box {
            background: rgba(10, 5, 20, 0.8);
            border: 1px solid rgba(245, 158, 11, 0.25);
            padding: 16px;
            border-radius: 16px;
            margin-bottom: 22px;
            position: relative;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s ease;
        }
        
        .secret-box:hover {
            border-color: rgba(245, 158, 11, 0.5);
            box-shadow: 0 8px 32px 0 rgba(245, 158, 11, 0.05);
        }

        .secret-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--warning);
            margin-bottom: 8px;
            font-weight: 700;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .secret-value-container {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 8px 12px;
        }

        .secret-value {
            flex-grow: 1;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            color: #f59e0b;
            font-weight: 700;
            letter-spacing: 0.03em;
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
        }

        .action-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 6px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            margin-left: 6px;
        }

        .action-btn:hover {
            color: var(--text-main);
            background: rgba(255, 255, 255, 0.08);
        }

        .action-btn:active {
            transform: scale(0.92);
        }

        /* Features Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 22px;
        }

        .card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(139, 92, 246, 0.3);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.06);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-title {
            font-weight: 600;
            font-size: 0.8rem;
            color: var(--text-main);
        }

        .status-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 700;
            align-self: flex-start;
            text-transform: uppercase;
        }

        .status-version {
            background: rgba(139, 92, 246, 0.15);
            color: #d8b4fe;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }

        .status-active {
            background: rgba(16, 185, 129, 0.15);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        /* Toast notifications */
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(17, 12, 28, 0.9);
            border: 1px solid var(--accent-primary);
            color: var(--text-main);
            padding: 10px 20px;
            border-radius: 100px;
            font-size: 0.85rem;
            font-weight: 500;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
        }

        footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-secondary);
            font-size: 0.75rem;
            border-top: 1px solid var(--border-color);
            padding-top: 16px;
            margin-top: 10px;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse 1.6s infinite;
        }

        @keyframes pulse {
            0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }
            70% {
                transform: scale(1);
                box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
            }
            100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
            }
        }
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>

    <div class="container">
        <header>
            <div class="badge">
                <i data-lucide="shield-check" style="width: 13px; height: 13px;"></i>
                GitOps DevSecOps Platform
            </div>
            <h1>Platform Control</h1>
            <p class="lead">Trạng thái bảo mật & cấu hình tự động</p>
        </header>

        <!-- Dynamic Database Secret from AWS Secrets Manager -->
        <div class="secret-box">
            <div class="secret-header">
                <span>AWS Secrets Manager (via ESO)</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; background: rgba(245,158,11,0.15); padding: 2px 6px; border-radius: 4px;">Dynamic Refresh</span>
            </div>
            <div class="secret-value-container">
                <input type="password" id="secretValue" class="secret-value" value="{{ db_password }}" readonly>
                <button class="action-btn" id="toggleBtn" onclick="toggleSecret()" title="Hiện/Ẩn">
                    <i data-lucide="eye" id="eyeIcon" style="width: 16px; height: 16px;"></i>
                </button>
                <button class="action-btn" onclick="copySecret()" title="Sao chép">
                    <i data-lucide="copy" style="width: 16px; height: 16px;"></i>
                </button>
            </div>
        </div>

        <!-- GitOps Features Grid -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <i data-lucide="git-pull-request" style="color: #c084fc; width: 16px; height: 16px;"></i>
                    <span class="card-title">Argo Rollouts</span>
                </div>
                <span class="status-badge status-version">{{ version }}</span>
            </div>

            <div class="card">
                <div class="card-header">
                    <i data-lucide="lock" style="color: #34d399; width: 16px; height: 16px;"></i>
                    <span class="card-title">OPA Gatekeeper</span>
                </div>
                <span class="status-badge status-active">Enforced</span>
            </div>

            <div class="card">
                <div class="card-header">
                    <i data-lucide="users" style="color: #60a5fa; width: 16px; height: 16px;"></i>
                    <span class="card-title">Cluster RBAC</span>
                </div>
                <span class="status-badge" style="background: rgba(96, 165, 250, 0.15); color: #93c5fd; border: 1px solid rgba(96, 165, 250, 0.2);">Enabled</span>
            </div>

            <div class="card">
                <div class="card-header">
                    <i data-lucide="shield" style="color: #f43f5e; width: 16px; height: 16px;"></i>
                    <span class="card-title">Trivy & Cosign</span>
                </div>
                <span class="status-badge" style="background: rgba(244, 63, 94, 0.15); color: #fca5a5; border: 1px solid rgba(244, 63, 94, 0.2);">Verified</span>
            </div>
        </div>

        <footer>
            <div class="status-indicator">
                <div class="pulse-dot"></div>
                <span>Status: <strong style="color: #34d399; font-weight: 600;">Active</strong></span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; opacity: 0.7;">W10 • Secure & Operate</span>
        </footer>
    </div>

    <!-- Copy Toast -->
    <div id="toast" class="toast">
        <i data-lucide="check-circle" style="width: 16px; height: 16px; color: #34d399;"></i>
        <span>Đã sao chép mật khẩu vào bộ nhớ tạm!</span>
    </div>

    <script>
        // Khởi tạo Lucide Icons
        lucide.createIcons();

        function toggleSecret() {
            const input = document.getElementById('secretValue');
            const icon = document.getElementById('eyeIcon');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.setAttribute('data-lucide', 'eye-off');
            } else {
                input.type = 'password';
                icon.setAttribute('data-lucide', 'eye');
            }
            lucide.createIcons();
        }

        function copySecret() {
            const input = document.getElementById('secretValue');
            navigator.clipboard.writeText(input.value).then(() => {
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 2500);
            });
        }
    </script>
</body>
</html>
"""

def get_db_password():
    secret_path = "/secrets/db-secret/password"
    if os.path.exists(secret_path):
        try:
            with open(secret_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            return f"Error: {str(e)}"
    return "Secret Not Mounted"

@app.get("/")
def index():
    db_password = get_db_password()
    return render_template_string(
        HTML_TEMPLATE,
        version=VERSION,
        error_rate=f"{int(ERROR_RATE * 100)}%",
        db_password=db_password
    )

@app.get("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
