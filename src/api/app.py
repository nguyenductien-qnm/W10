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
    <title>W10 - Enterprise Platform Security & Delivery Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            --bg-color: #f8fafc;
            --panel-bg: rgba(255, 255, 255, 0.75);
            --border-color: rgba(15, 23, 42, 0.08);
            --accent-primary: #6366f1;
            --accent-primary-glow: rgba(99, 102, 241, 0.15);
            --accent-secondary: #ec4899;
            --text-main: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.15);
            --danger: #ef4444;
            --shadow-sm: 0 2px 8px -2px rgba(15, 23, 42, 0.05);
            --shadow-md: 0 12px 24px -10px rgba(15, 23, 42, 0.08);
            --shadow-lg: 0 25px 50px -12px rgba(15, 23, 42, 0.06);
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
                radial-gradient(circle at 5% 5%, rgba(99, 102, 241, 0.06) 0%, transparent 35%),
                radial-gradient(circle at 95% 95%, rgba(236, 72, 153, 0.05) 0%, transparent 35%),
                linear-gradient(rgba(15, 23, 42, 0.012) 1px, transparent 1px),
                linear-gradient(90deg, rgba(15, 23, 42, 0.012) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 30px 30px, 30px 30px;
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 40px 20px;
            overflow-x: hidden;
            position: relative;
        }

        /* Ambient glowing orbs */
        .orb {
            position: absolute;
            width: 350px;
            height: 350px;
            border-radius: 50%;
            filter: blur(120px);
            z-index: -1;
            opacity: 0.35;
            animation: float 16s infinite alternate ease-in-out;
        }
        .orb-1 {
            background: linear-gradient(135deg, var(--accent-primary), #a78bfa);
            top: 15%;
            left: 20%;
        }
        .orb-2 {
            background: linear-gradient(135deg, var(--accent-secondary), #f472b6);
            bottom: 15%;
            right: 20%;
            animation-delay: -8s;
        }

        @keyframes float {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(40px, 30px) scale(1.15); }
        }

        .dashboard-wrapper {
            width: 100%;
            max-width: 1080px;
            background: var(--panel-bg);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border: 1px solid var(--border-color);
            border-radius: 28px;
            box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.6);
            overflow: hidden;
            display: grid;
            grid-template-columns: 1fr;
            z-index: 10;
        }

        @media (min-width: 820px) {
            .dashboard-wrapper {
                grid-template-columns: 360px 1fr;
            }
        }

        /* Left Sidebar: Hero Status & Metrics */
        .sidebar {
            background: rgba(255, 255, 255, 0.45);
            border-bottom: 1px solid var(--border-color);
            padding: 40px 30px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 40px;
        }

        @media (min-width: 820px) {
            .sidebar {
                border-bottom: none;
                border-right: 1px solid var(--border-color);
            }
        }

        .sidebar-header {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .system-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.08));
            border: 1px solid rgba(99, 102, 241, 0.15);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--accent-primary);
            align-self: flex-start;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .sidebar-title h1 {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.04em;
            background: linear-gradient(135deg, #1e1b4b 20%, #4338ca 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .sidebar-title p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* Live health stats visualizer */
        .live-stats {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .stat-item {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .stat-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .stat-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            display: flex;
            align-items: baseline;
            gap: 4px;
        }

        .stat-unit {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted);
        }

        /* Pure CSS Sparkline simulation */
        .sparkline {
            display: flex;
            align-items: flex-end;
            gap: 3px;
            height: 24px;
            width: 80px;
        }

        .sparkbar {
            width: 4px;
            background-color: var(--accent-primary);
            border-radius: 2px;
            opacity: 0.7;
        }
        .sparkbar:nth-child(odd) {
            height: 40%;
            animation: bounce-stat-1 2s infinite alternate ease-in-out;
        }
        .sparkbar:nth-child(even) {
            height: 75%;
            animation: bounce-stat-2 2.4s infinite alternate ease-in-out;
        }
        @keyframes bounce-stat-1 {
            0% { height: 35%; } 100% { height: 90%; }
        }
        @keyframes bounce-stat-2 {
            0% { height: 80%; } 100% { height: 45%; }
        }

        /* Right Panel: Content Area */
        .main-panel {
            padding: 40px;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 14px;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Secret Box Card (AWS integration) */
        .aws-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(253, 246, 227, 0.5) 100%);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 20px;
            padding: 22px;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .aws-card:hover {
            border-color: rgba(245, 158, 11, 0.45);
            box-shadow: 0 15px 30px -10px rgba(245, 158, 11, 0.1);
        }

        .aws-card::before {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(245, 158, 11, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .aws-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }

        .aws-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--warning);
        }

        .aws-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            background: var(--warning-glow);
            color: var(--warning);
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid rgba(245, 158, 11, 0.15);
        }

        .secret-input-wrapper {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 12px;
            padding: 10px 14px;
            box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.02);
        }

        .secret-field {
            flex-grow: 1;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.15rem;
            color: var(--warning);
            font-weight: 700;
            letter-spacing: 0.02em;
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
        }

        .action-button {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            margin-left: 6px;
        }

        .action-button:hover {
            color: var(--text-main);
            background: rgba(15, 23, 42, 0.05);
        }

        .action-button:active {
            transform: scale(0.92);
        }

        /* GitOps Components Grid */
        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }

        .comp-card {
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 20px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
        }

        .comp-card:hover {
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.85);
            border-color: var(--accent-primary-glow);
            box-shadow: var(--shadow-md), 0 10px 20px -10px var(--accent-primary-glow);
        }

        .comp-icon-wrapper {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 4px;
        }

        .comp-name {
            font-weight: 700;
            font-size: 0.95rem;
            color: var(--text-main);
            letter-spacing: -0.01em;
        }

        .comp-desc {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        .badge-status {
            align-self: flex-start;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 8px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .badge-indigo {
            background: rgba(99, 102, 241, 0.08);
            color: var(--accent-primary);
            border: 1px solid rgba(99, 102, 241, 0.12);
        }

        .badge-emerald {
            background: rgba(16, 185, 129, 0.08);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.12);
        }

        .badge-blue {
            background: rgba(59, 130, 246, 0.08);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.12);
        }

        .badge-rose {
            background: rgba(244, 63, 94, 0.08);
            color: #f43f5e;
            border: 1px solid rgba(244, 63, 94, 0.12);
        }

        /* Activity Console / Live Logs */
        .console-panel {
            background: #0f172a;
            border-radius: 16px;
            padding: 16px 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: #e2e8f0;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
            display: flex;
            flex-direction: column;
            gap: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            max-height: 140px;
            overflow-y: auto;
        }

        .console-line {
            display: flex;
            gap: 8px;
            line-height: 1.5;
        }

        .console-time {
            color: #64748b;
            flex-shrink: 0;
        }

        .console-prefix {
            color: #38bdf8;
            font-weight: bold;
        }

        .console-success {
            color: #4ade80;
        }

        /* Bottom Footer inside card */
        .panel-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
            margin-top: 10px;
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .indicator-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
            position: relative;
        }

        .status-dot::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--success);
            border-radius: 50%;
            animation: pulse-ring 1.8s infinite;
        }

        @keyframes pulse-ring {
            0% { transform: scale(0.95); opacity: 0.75; }
            70% { transform: scale(2.2); opacity: 0; }
            100% { transform: scale(0.95); opacity: 0; }
        }

        /* Toast Popup */
        .toast-notification {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(120px);
            background: #0f172a;
            border: 1px solid var(--accent-primary);
            color: #fff;
            padding: 12px 24px;
            border-radius: 100px;
            font-size: 0.85rem;
            font-weight: 500;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .toast-notification.show {
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>

    <div class="dashboard-wrapper">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="system-badge">
                    <i data-lucide="shield-alert" style="width: 14px; height: 14px;"></i>
                    Secured Platform
                </div>
                <div class="sidebar-title">
                    <h1>Enterprise</h1>
                    <h1>Control</h1>
                    <p>Trạng thái phân phối DevSecOps & giám sát toàn diện hạ tầng</p>
                </div>
            </div>

            <!-- Health visualizer -->
            <div class="live-stats">
                <div class="stat-item">
                    <div class="stat-meta">
                        <span>LIVE RESPONSE TIME</span>
                        <i data-lucide="activity" style="width: 14px; height: 14px; color: var(--accent-primary);"></i>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                        <span class="stat-value">42 <span class="stat-unit">ms</span></span>
                        <div class="sparkline">
                            <span class="sparkbar"></span>
                            <span class="sparkbar"></span>
                            <span class="sparkbar"></span>
                            <span class="sparkbar"></span>
                            <span class="sparkbar"></span>
                            <span class="sparkbar"></span>
                        </div>
                    </div>
                </div>

                <div class="stat-item">
                    <div class="stat-meta">
                        <span>ERROR RATE LIMIT</span>
                        <i data-lucide="zap-off" style="width: 14px; height: 14px; color: var(--danger);"></i>
                    </div>
                    <span class="stat-value" style="color: var(--success);">{{ error_rate }}</span>
                </div>
            </div>

            <div style="font-size: 0.72rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
                <i data-lucide="globe" style="width: 12px; height: 12px;"></i>
                Nodes: Kubernetes Multi-AZ Cluster
            </div>
        </div>

        <!-- Main Panel -->
        <div class="main-panel">
            <div class="section-header">
                <div class="section-title">
                    <i data-lucide="shield-check" style="color: var(--accent-primary); width: 20px; height: 20px;"></i>
                    Secrets Synchronization
                </div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 0.78rem; color: var(--text-muted);">
                    <i data-lucide="refresh-cw" class="spin-icon" style="width: 12px; height: 12px; animation: spin 8s linear infinite;"></i>
                    ESO polling 60s
                </div>
            </div>

            <!-- Secrets Manager Card -->
            <div class="aws-card">
                <div class="aws-header">
                    <div class="aws-title">
                        <i data-lucide="key-round" style="width: 16px; height: 16px;"></i>
                        AWS Secrets Manager
                    </div>
                    <span class="aws-tag">Dynamic Secret</span>
                </div>
                <div class="secret-input-wrapper">
                    <input type="password" id="secretValue" class="secret-field" value="{{ db_password }}" readonly>
                    <button class="action-button" id="toggleBtn" onclick="toggleSecret()" title="Ẩn/Hiện mật khẩu">
                        <i data-lucide="eye" id="eyeIcon" style="width: 18px; height: 18px;"></i>
                    </button>
                    <button class="action-button" onclick="copySecret()" title="Sao chép mật khẩu">
                        <i data-lucide="copy" style="width: 18px; height: 18px;"></i>
                    </button>
                </div>
            </div>

            <div class="section-header" style="margin-top: 10px;">
                <div class="section-title">
                    <i data-lucide="boxes" style="color: var(--accent-primary); width: 20px; height: 20px;"></i>
                    Platform Security Components
                </div>
            </div>

            <!-- Grid of components -->
            <div class="components-grid">
                <div class="comp-card">
                    <div>
                        <div class="comp-icon-wrapper" style="background: rgba(99, 102, 241, 0.1); color: var(--accent-primary);">
                            <i data-lucide="git-merge" style="width: 20px; height: 20px;"></i>
                        </div>
                        <h3 class="comp-name">Argo Rollouts</h3>
                        <p class="comp-desc">Hỗ trợ chiến lược Canary & Progressive delivery tự động.</p>
                    </div>
                    <span class="badge-status badge-indigo">{{ version }}</span>
                </div>

                <div class="comp-card">
                    <div>
                        <div class="comp-icon-wrapper" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">
                            <i data-lucide="fingerprint" style="width: 20px; height: 20px;"></i>
                        </div>
                        <h3 class="comp-name">OPA Gatekeeper</h3>
                        <p class="comp-desc">Đảm bảo tuân thủ tiêu chuẩn an toàn qua Admission Control.</p>
                    </div>
                    <span class="badge-status badge-emerald">Enforced</span>
                </div>

                <div class="comp-card">
                    <div>
                        <div class="comp-icon-wrapper" style="background: rgba(59, 130, 246, 0.1); color: #3b82f6;">
                            <i data-lucide="users-round" style="width: 20px; height: 20px;"></i>
                        </div>
                        <h3 class="comp-name">Cluster RBAC</h3>
                        <p class="comp-desc">Nguyên tắc đặc quyền tối thiểu (least-privilege) cho workload.</p>
                    </div>
                    <span class="badge-status badge-blue">Least Privilege</span>
                </div>

                <div class="comp-card">
                    <div>
                        <div class="comp-icon-wrapper" style="background: rgba(244, 63, 94, 0.1); color: #f43f5e;">
                            <i data-lucide="binary" style="width: 20px; height: 20px;"></i>
                        </div>
                        <h3 class="comp-name">Cosign Verification</h3>
                        <p class="comp-desc">Xác minh chữ ký số ảnh docker trước khi triển khai.</p>
                    </div>
                    <span class="badge-status badge-rose">Verified</span>
                </div>
            </div>

            <!-- Simulated live audit log feed -->
            <div class="console-panel">
                <div class="console-line">
                    <span class="console-time">[10:31:02]</span>
                    <span class="console-prefix">SYSTEM:</span>
                    <span>ArgoCD application synchronized state successfully.</span>
                </div>
                <div class="console-line">
                    <span class="console-time">[10:31:05]</span>
                    <span class="console-prefix">ESO:</span>
                    <span class="console-success">Synced secret "db-secret" from AWS Secrets Manager store.</span>
                </div>
                <div class="console-line">
                    <span class="console-time">[10:32:00]</span>
                    <span class="console-prefix">ROLLOUT:</span>
                    <span>Starting canary analysis template for "success-rate".</span>
                </div>
                <div class="console-line">
                    <span class="console-time">[10:32:45]</span>
                    <span class="console-prefix">GATEKEEPER:</span>
                    <span class="console-success">Admission request allowed: no policy violations.</span>
                </div>
            </div>

            <!-- Footer area -->
            <div class="panel-footer">
                <div class="indicator-group">
                    <div class="status-dot"></div>
                    <span>Deployment: <strong style="color: var(--success);">Online</strong></span>
                </div>
                <span>W10 Secure Platform Core v1.4</span>
            </div>
        </div>
    </div>

    <!-- Copy Toast -->
    <div id="toastNotification" class="toast-notification">
        <i data-lucide="check-circle" style="width: 18px; height: 18px; color: #34d399;"></i>
        <span>Đã sao chép mật khẩu AWS vào clipboard!</span>
    </div>

    <script>
        // Init Lucide
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
                const toast = document.getElementById('toastNotification');
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 2800);
            });
        }
    </script>
    <style>
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
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
