# README - Odoo Addon Development với GitHub Copilot

## 🚀 Tổng quan
Workspace này được thiết lập để phát triển addon Odoo 18.0 với sự hỗ trợ của GitHub Copilot. Tất cả các addon tùy chỉnh sẽ được phát triển trong thư mục `my-addon/`.

## 📁 Cấu trúc Thư mục
```
d:\Training\airlogistic-odoo\
├── docker-compose.yml          # Cấu hình Docker
├── odoo.conf                   # Cấu hình Odoo
├── .copilot-instructions.md    # Hướng dẫn cho GitHub Copilot
├── addons/                     # Community addons (helpdesk, etc.)
├── my-addon/                   # 🎯 THƯC MỤC ADDON TÙY CHỈNH
│   └── sample_addon/           # Addon mẫu
└── README.md                   # File này
```

## 🎯 Cách sử dụng GitHub Copilot Instructions

### 1. GitHub Copilot đã được cấu hình để:
- ✅ Hiểu cấu trúc addon Odoo 18.0
- ✅ Tuân theo coding conventions của Odoo
- ✅ Tạo code theo best practices
- ✅ Hỗ trợ phát triển trong thư mục `my-addon/`

### 2. Tạo addon mới:
```bash
# Trong VS Code, sử dụng Copilot Chat:
"Tạo addon mới tên 'my_custom_addon' trong thư mục my-addon với model quản lý sản phẩm"
```

### 3. Các prompt hữu ích với Copilot:

#### Tạo Model mới:
```
"Tạo model 'product.management' với các field: name, description, price, category_id, state với workflow draft->confirmed->done"
```

#### Tạo View:
```
"Tạo form view cho model product.management với statusbar và notebook layout"
```

#### Tạo Wizard:
```
"Tạo wizard để bulk update price cho multiple products"
```

#### Tạo Report:
```
"Tạo PDF report cho model product.management với template đẹp"
```

#### Tạo Controller/API:
```
"Tạo REST API endpoint để get/post data cho model product.management"
```

## 🛠️ Quy trình phát triển

### Bước 1: Khởi tạo addon
1. Tạo thư mục addon trong `my-addon/`
2. Sử dụng Copilot để tạo cấu trúc cơ bản
3. Cập nhật `__manifest__.py`

### Bước 2: Phát triển Model
1. Định nghĩa model trong `models/`
2. Tạo security rules
3. Tạo data/demo files

### Bước 3: Tạo Views
1. Tạo form, tree, kanban views
2. Tạo menu structure
3. Cấu hình actions

### Bước 4: Test và Deploy
```bash
# Cài đặt addon
docker-compose exec odoo odoo -i addon_name -d odoo --stop-after-init

# Update addon
docker-compose exec odoo odoo -u addon_name -d odoo --stop-after-init

# Debug mode
docker-compose exec odoo odoo -d odoo --dev=all
```

## 📝 Ví dụ Prompts cho Copilot

### Tạo addon CRM tùy chỉnh:
```
"Tạo addon CRM tùy chỉnh trong my-addon với:
- Model lead.custom với fields: name, email, phone, company, source, state
- Workflow: new -> qualified -> proposal -> won/lost
- Form view với statusbar
- Kanban view group by state
- Wizard để convert lead to opportunity"
```

### Tạo addon Inventory:
```
"Tạo addon quản lý kho trong my-addon với:
- Model stock.item với fields: name, sku, quantity, location, category
- Model stock.movement để track in/out
- Dashboard view hiển thị stock levels
- Alert khi stock thấp"
```

### Tạo addon HR:
```
"Tạo addon HR trong my-addon với:
- Model hr.employee.custom inherit hr.employee
- Thêm fields: skill_ids, certification_ids, performance_rating
- View form mở rộng
- Report performance review"
```

## 🎨 Copilot Best Practices

### 1. Descriptive Prompts:
```
❌ "Tạo model"
✅ "Tạo model quản lý đơn hàng với workflow và integration với mail system"
```

### 2. Specify Requirements:
```
❌ "Tạo view"
✅ "Tạo kanban view với drag-drop, color coding theo priority, và button actions"
```

### 3. Include Context:
```
❌ "Fix lỗi"
✅ "Fix validation error trong model khi state transition từ draft sang confirmed"
```

## 🚀 Sample Addon
Tham khảo `my-addon/sample_addon/` để xem ví dụ hoàn chỉnh về:
- ✅ Model structure với computed fields
- ✅ Complete views (tree, form, kanban)
- ✅ Wizard for bulk operations
- ✅ Security configuration
- ✅ API controllers
- ✅ Mail integration
- ✅ Demo data

## 📚 Tài liệu tham khảo
- [Odoo 18.0 Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Developer Tutorials](https://www.odoo.com/documentation/18.0/developer/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

## 💡 Tips
1. **Luôn sử dụng** naming conventions của Odoo
2. **Theo dõi** security và access rights
3. **Test kỹ** addon trước khi deploy
4. **Sử dụng** demo data để test
5. **Tận dụng** Copilot suggestions nhưng review code kỹ

---
**Happy Coding với GitHub Copilot! 🚀**
