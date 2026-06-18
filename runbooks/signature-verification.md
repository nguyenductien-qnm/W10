# Runbook: Xử lý Lỗi Xác thực Chữ ký Ảnh (Sigstore Policy Controller)

Tài liệu này hướng dẫn cách kiểm tra và khắc phục sự cố khi ảnh container bị Sigstore Policy Controller chặn, không cho phép deploy vào cụm.

## 1. Dấu hiệu nhận biết lỗi
Khi deploy một workload (Deployment/Rollout/Pod) vào namespace đã kích hoạt xác thực (`policy.sigstore.dev/include=true`), yêu cầu deploy bị từ chối với lỗi:
```text
Error from server (BadRequest): admission webhook "policy.sigstore.dev" denied the request: validation failed: no matching policies...
```
Hoặc đối với ReplicaSet/Deployment: Pod mới không thể tạo được, kiểm tra `kubectl describe replicaset <name>` thấy lỗi tạo Pod do bị Webhook của Sigstore từ chối.

---

## 2. Quy trình gỡ lỗi từng bước

### Bước 1: Kiểm tra xem ảnh đã được ký số chưa
Chạy lệnh kiểm tra chữ ký của ảnh trên Registry sử dụng khóa công khai `cosign.pub`:
```bash
cosign verify --key signing/cosign.pub <TÊN_IMAGE>:<TAG>
```
* **Nếu lệnh báo lỗi `no matching signatures`**: Ảnh chưa hề được ký số. Kiểm tra lại pipeline CI/CD ở bước ký Cosign xem có bị lỗi hoặc bị bỏ qua không.
* **Nếu lệnh thành công**: Chữ ký hợp lệ, chuyển sang Bước 2.

### Bước 2: Kiểm tra cấu hình ClusterImagePolicy trong cụm
Lấy thông tin chính sách đang áp dụng:
```bash
kubectl get clusterimagepolicy -o yaml
```
* Đảm bảo khóa công khai (`key.data`) trong cấu hình `ClusterImagePolicy` trùng khớp hoàn toàn với nội dung của file `signing/cosign.pub`.
* Đảm bảo trường `images.glob` khớp với định dạng tên ảnh của bạn (ví dụ `730335441285.dkr.ecr.ap-southeast-1.amazonaws.com/w10*`).

### Bước 3: Xem log của Policy Controller
Nếu cấu hình đúng nhưng vẫn bị chặn, kiểm tra trực tiếp log của bộ điều khiển để xem lý do chi tiết:
```bash
kubectl logs -n cosign-system -l app=policy-controller-webhook --tail=100
kubectl logs -n cosign-system -l app=policy-controller-controller --tail=100
```

---

## 3. Cách xử lý nhanh sự cố trong môi trường khẩn cấp (Emergency Bypass)
Nếu xảy ra sự cố khẩn cấp trên Production và cần bypass kiểm tra chữ ký để khôi phục dịch vụ ngay lập tức:
* **Tạm thời gỡ bỏ nhãn kích hoạt trên namespace**:
  ```bash
  kubectl label namespace demo policy.sigstore.dev/include-
  ```
  *(Lưu ý: Sau khi hệ thống ổn định, phải ký lại ảnh và gắn lại nhãn `policy.sigstore.dev/include=true` ngay lập tức).*
