# Runbook: Xử lý và Kiểm tra Xoay vòng Secret (ESO)

Tài liệu này hướng dẫn cách kiểm tra, xác thực và xử lý sự cố liên quan đến cơ chế tự động xoay vòng (rotation) Secret từ AWS Secrets Manager về Kubernetes thông qua External Secrets Operator (ESO).

## 1. Quy trình kiểm tra hoạt động bình thường
Để kiểm tra xem Secret có được đồng bộ chính xác và tự động cập nhật hay không:
1. Đăng nhập vào AWS Console -> Secrets Manager -> Tìm secret `demo-w10`.
2. Thực hiện chỉnh sửa giá trị của key `DATABASE_PASSWORD`.
3. Trên terminal EC2, kiểm tra xem K8s Secret đã nhận giá trị mới chưa (đã được giải mã base64):
   ```bash
   kubectl get secret db-secret -n demo -o jsonpath='{.data.password}' | base64 -d
   ```
4. Kiểm tra xem Pod API có nhận cấu hình mới mà không bị khởi động lại hay không:
   * Xem tuổi thọ của Pod (không được thay đổi):
     ```bash
     kubectl get pods -n demo -l app=api
     ```
   * Truy cập giao diện Web Dashboard `http://<EC2_Public_IP>` -> F5 trình duyệt để xem mật khẩu mới hiển thị trên giao diện.

---

## 2. Các sự cố thường gặp và cách xử lý

### Sự cố 1: K8s Secret `db-secret` không tự động cập nhật giá trị mới
* **Triệu chứng**: Đã đổi mật khẩu trên AWS nhưng kiểm tra K8s Secret vẫn là giá trị cũ sau 30 giây.
* **Cách kiểm tra**:
  1. Kiểm tra trạng thái của `ExternalSecret`:
     ```bash
     kubectl get externalsecret db-creds -n demo
     ```
  2. Xem chi tiết lỗi bằng lệnh `describe`:
     ```bash
     kubectl describe externalsecret db-creds -n demo
     ```
* **Lỗi phổ biến & Khắc phục**:
  * `Secret does not exist`: Tên key trên AWS viết sai chính tả hoặc sai kiểu chữ hoa/thường (ví dụ `demo-W10` so với `demo-w10`). Sửa lại trường `key` trong file `external-secret.yaml`.
  * `the desired SecretStore aws-store is not ready`: Xem sự cố 2 bên dưới.

---

### Sự cố 2: SecretStore `aws-store` báo lỗi không sẵn sàng (Not Ready)
* **Triệu chứng**: `ExternalSecret` báo lỗi phụ thuộc vào `aws-store`.
* **Cách kiểm tra**:
  ```bash
  kubectl describe secretstore aws-store -n demo
  ```
* **Lỗi phổ biến & Khắc phục**:
  * Lỗi phân quyền IAM (AccessDenied): EC2 Instance Profile bị gỡ bỏ hoặc IAM Role gắn kèm EC2 không có quyền `secretsmanager:GetSecretValue` cho tài nguyên `demo-w10`. Cần kiểm tra lại IAM Policy gắn trên EC2.
  * Lỗi kết nối mạng: Cụm K3s không thể phân giải tên miền hoặc kết nối tới AWS Secrets Manager API endpoint. Kiểm tra CoreDNS và kết nối mạng ngoài của EC2.
