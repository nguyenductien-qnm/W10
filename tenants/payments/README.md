# Tenant Payments: Multi-tenant Isolation

This directory contains the manifests to set up multi-tenant isolation for Team B (payments).

## Challenge Questions

### 1. Vì sao guardrail cũ (các Gatekeeper policy) tự động áp dụng cho team B (payments) mà không cần viết luật mới?
Do các Constraint của Gatekeeper (ví dụ: `check-latest-tag`, `require-resources-limits`, `restrict-root-user`, `restrict-host-network`) được cấu hình để đối khớp với các tài nguyên `Pod` và `Deployment` trên toàn bộ cluster (khai báo dưới dạng `kinds`), trừ một số namespace hệ thống được loại trừ rõ ràng (như `kube-system`, `argocd`, `gatekeeper-system`). 

Khi namespace `payments` mới được tạo ra, nó đi qua Admission Webhook của Gatekeeper. Vì namespace này không nằm trong danh sách loại trừ (`excludedNamespaces`), mọi tài nguyên deploy vào `payments` sẽ tự động bị các policy cũ kiểm tra và áp dụng chế độ thực thi (`deny`).

### 2. Sự khác biệt giữa Role/RoleBinding và ClusterRoleBinding trong việc giữ tính cô lập?
- **Role & RoleBinding**: Được định nghĩa và áp dụng trong phạm vi của một **namespace duy nhất** (ở đây là namespace `payments`). Khi gắn quyền cho `payments-dev` qua RoleBinding, user hoặc ServiceAccount này chỉ có quyền tương tác với các tài nguyên nằm trong namespace `payments`. Họ không thể truy cập, sửa đổi, hay xóa bất cứ thứ gì trong namespace khác (như `demo` hay `default`), từ đó đảm bảo tính cô lập hoàn toàn giữa các tenant.
- **ClusterRoleBinding**: Dùng để gắn quyền trên phạm vi **toàn cụm** (cluster-wide) cho một ClusterRole. Nếu sử dụng ClusterRoleBinding, đối tượng được phân quyền sẽ có quyền tương tác với tài nguyên trên mọi namespace của cụm Kubernetes (vượt qua ranh giới của namespace `payments`). Điều này phá vỡ nguyên lý cô lập đa người dùng (multi-tenancy) và tạo ra rủi ro bảo mật lớn.
