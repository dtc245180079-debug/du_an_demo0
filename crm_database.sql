-- =====================================================================
-- CƠ SỞ DỮ LIỆU ĐỒ ÁN / HỆ THỐNG CRM & BÁN HÀNG ĐIỆN THOẠI AI
-- Hệ quản trị CSDL: MySQL 8.0+ / MariaDB 10.3+
-- Database Name: customer_support_ai
-- Bảng mã: utf8mb4 / utf8mb4_unicode_ci (Hỗ trợ tiếng Việt đầy đủ)
-- Tài khoản quản trị mặc định: admin / Mật khẩu: 12345678
-- Ngày cập nhật & đồng bộ chuẩn: 2026-10-02 01:08:48
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `customer_support_ai` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `customer_support_ai`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- BẢNG: `users`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'customer',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `users` (4 bản ghi)
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `full_name`, `phone`, `role`, `avatar`, `is_active`, `created_at`) VALUES
(1, 'admin', 'admin@cskh.vn', 'pbkdf2:sha256:1000000$8n3DTEjll9RAcb6S$3cd1eae56fbbf0e1ac8dff6cfd5d01614c224445ae94585617adcce95a89545d', 'Quản Trị Viên Hệ Thống', '0901234567', 'admin', NULL, 1, '2026-10-02 01:06:19'),
(2, 'nhanvien', 'agent1@cskh.vn', 'pbkdf2:sha256:1000000$8n3DTEjll9RAcb6S$3cd1eae56fbbf0e1ac8dff6cfd5d01614c224445ae94585617adcce95a89545d', 'Nguyễn Văn Hỗ Trợ', '0912345678', 'agent', NULL, 1, '2026-10-02 01:06:19'),
(3, 'agent2', 'agent2@cskh.vn', 'pbkdf2:sha256:1000000$8n3DTEjll9RAcb6S$3cd1eae56fbbf0e1ac8dff6cfd5d01614c224445ae94585617adcce95a89545d', 'Trần Thị Chăm Sóc', '0923456789', 'agent', NULL, 1, '2026-10-02 01:06:19'),
(4, 'khachhang', 'hung.le@gmail.com', 'pbkdf2:sha256:1000000$8n3DTEjll9RAcb6S$3cd1eae56fbbf0e1ac8dff6cfd5d01614c224445ae94585617adcce95a89545d', 'Lê Văn Hùng', '0987654321', 'customer', NULL, 1, '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `customers`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `customers`;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `zalo_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fb_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ig_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `member_rank` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Bạc',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_phone` (`phone`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `customers` (3 bản ghi)
INSERT INTO `customers` (`id`, `user_id`, `full_name`, `phone`, `email`, `zalo_id`, `fb_id`, `ig_id`, `member_rank`, `notes`, `created_at`, `updated_at`) VALUES
(1, 4, 'Lê Văn Hùng', '0987654321', 'hung.le@gmail.com', 'zalo_hung99', 'fb_hungvip', NULL, 'VIP', 'Khách VIP thường mua flagship Apple.', '2026-10-02 01:07:27', '2026-10-02 01:07:27'),
(2, NULL, 'Trần Thị Mai', '0912345678', 'mai.tran@gmail.com', 'zalo_mai', NULL, NULL, 'Vàng', 'Quan tâm chính sách trả góp 0% qua thẻ tín dụng.', '2026-10-02 01:07:27', '2026-10-02 01:07:27'),
(3, NULL, 'Nguyễn Tuấn Anh', '0933221100', 'anh.nguyen@gmail.com', NULL, NULL, NULL, 'Bạc', 'Khách hàng mới tiếp cận qua Webchat.', '2026-10-02 01:07:27', '2026-10-02 01:07:27');

-- ---------------------------------------------------------------------
-- BẢNG: `customer_preferences`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `customer_preferences`;
CREATE TABLE `customer_preferences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `budget_min` decimal(15,2) DEFAULT NULL,
  `budget_max` decimal(15,2) DEFAULT NULL,
  `primary_usage` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preferred_brands` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `desired_screen_size` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `key_criteria` text COLLATE utf8mb4_unicode_ci,
  `interested_products` text COLLATE utf8mb4_unicode_ci,
  `agent_notes` text COLLATE utf8mb4_unicode_ci,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_id` (`customer_id`),
  KEY `idx_pref_cust` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `customer_preferences` (1 bản ghi)
INSERT INTO `customer_preferences` (`id`, `customer_id`, `budget_min`, `budget_max`, `primary_usage`, `preferred_brands`, `desired_screen_size`, `key_criteria`, `interested_products`, `agent_notes`, `updated_at`) VALUES
(1, 1, '25000000.00', '35000000.00', 'Chụp ảnh quay phim & Sang trọng', 'Apple, Samsung', 'Màn hình lớn > 6.7 inch', 'Camera zoom quang học tốt, Pin trâu, Hỗ trợ trả góp 0%', '1,3', 'Khách VIP thích sản phẩm màu Titan Tự Nhiên hoặc Titan Xám', '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `tickets`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `tickets`;
CREATE TABLE `tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` int NOT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'web',
  `subject` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'medium',
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'open',
  `assigned_agent_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `resolved_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_code` (`ticket_code`),
  KEY `idx_status` (`status`),
  KEY `idx_assigned` (`assigned_agent_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `tickets` (3 bản ghi)
INSERT INTO `tickets` (`id`, `ticket_code`, `customer_id`, `customer_name`, `customer_phone`, `customer_email`, `channel`, `subject`, `priority`, `status`, `assigned_agent_id`, `created_at`, `updated_at`, `resolved_at`) VALUES
(1, 'TK-202610-001', 1, 'Lê Văn Hùng', '0987654321', 'hung.le@gmail.com', 'web', 'Màn hình iPhone 15 Pro Max xuất hiện sọc xanh mép phải', 'high', 'in_progress', 2, '2026-10-02 01:07:27', '2026-10-02 01:07:27', NULL),
(2, 'TK-202610-002', 2, 'Trần Thị Mai', '0912345678', 'mai.tran@gmail.com', 'zalo', 'Tư vấn hồ sơ trả góp 0% Galaxy S24 Ultra qua thẻ Sacombank', 'medium', 'open', 2, '2026-10-02 01:07:27', '2026-10-02 01:07:27', NULL),
(3, 'TK-202610-003', 3, 'Nguyễn Tuấn Anh', '0933221100', 'anh.nguyen@gmail.com', 'facebook', 'Hỏi chính sách bảo hành 1 đổi 1 và quà tặng Xiaomi 14', 'low', 'resolved', 3, '2026-10-02 01:07:27', '2026-10-02 01:07:27', NULL);

-- ---------------------------------------------------------------------
-- BẢNG: `ticket_messages`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `ticket_messages`;
CREATE TABLE `ticket_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `sender_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_id` int DEFAULT NULL,
  `sender_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'web',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ticket` (`ticket_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `ticket_messages` (4 bản ghi)
INSERT INTO `ticket_messages` (`id`, `ticket_id`, `sender_type`, `sender_id`, `sender_name`, `message`, `channel`, `created_at`) VALUES
(1, 1, 'customer', NULL, 'Lê Văn Hùng', 'Em ơi máy iPhone 15 Pro Max mới mua được 2 tháng tự dưng mép phải màn hình có sọc xanh lá, bên em có nhận bảo hành không?', 'web', '2026-10-02 01:07:27'),
(2, 1, 'agent', NULL, 'Nguyễn Văn Hỗ Trợ', 'Dạ chào anh Hùng! Máy còn trong thời gian bảo hành và không bị rơi vỡ hay vào nước bên em sẽ gửi hãng thay màn hình miễn phí cho anh ạ. Anh có thể mang qua chi nhánh gần nhất nhé!', 'web', '2026-10-02 01:07:27'),
(3, 2, 'customer', NULL, 'Trần Thị Mai', 'Mình muốn mua Galaxy S24 Ultra trả góp qua thẻ Sacombank thì có mất phí chuyển đổi không shop?', 'web', '2026-10-02 01:07:27'),
(4, 2, 'agent', NULL, 'Nguyễn Văn Hỗ Trợ', 'Dạ chào chị Mai, bên em đang có chương trình liên kết Sacombank trả góp 0% lãi suất và miễn 100% phí chuyển đổi kỳ hạn 6-12 tháng ạ.', 'web', '2026-10-02 01:07:27');

-- ---------------------------------------------------------------------
-- BẢNG: `ticket_surveys`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `ticket_surveys`;
CREATE TABLE `ticket_surveys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `customer_id` int DEFAULT NULL,
  `rating_csat` int DEFAULT NULL,
  `score_nps` int DEFAULT NULL,
  `feedback` text COLLATE utf8mb4_unicode_ci,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_id` (`ticket_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `support_faqs`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `support_faqs`;
CREATE TABLE `support_faqs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `issue_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `symptom` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `solution` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_faq_cat_brand` (`category`,`brand`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `support_faqs` (20 bản ghi)
INSERT INTO `support_faqs` (`id`, `issue_name`, `category`, `brand`, `symptom`, `solution`, `created_at`) VALUES
(1, 'Màn hình iPhone bị sọc xanh', 'Kỹ thuật', 'Apple', 'Màn hình xuất hiện sọc xanh lá cây sau khi cập nhật hoặc tự nhiên bị.', 'Nếu máy còn bảo hành và không có dấu hiệu rơi cấn, vào nước, trung tâm sẽ gửi hãng thay màn hình miễn phí. Nếu hết bảo hành, cửa hàng hỗ trợ giảm 20% chi phí thay linh kiện chính hãng.', '2026-10-02 01:07:27'),
(2, 'Thủ tục mua trả góp 0%', 'Trả góp', 'Tất cả', 'Khách hàng hỏi cần giấy tờ gì để mua trả góp và trả trước bao nhiêu.', 'Chỉ cần mang theo CCCD gắn chip. Hỗ trợ 2 hình thức: Trả góp 0% qua thẻ tín dụng (không cần trả trước) hoặc qua công ty tài chính (Home Credit/HD Saison, trả trước từ 10% giá trị máy).', '2026-10-02 01:07:27'),
(3, 'Chính sách 1 đổi 1 trong 30 ngày', 'Bảo hành', 'Tất cả', 'Máy mới mua bị lỗi phần cứng có được đổi mới không?', 'Trong vòng 30 ngày đầu tính từ ngày mua, nếu máy gặp lỗi phần cứng do nhà sản xuất (được kỹ thuật viên thẩm định), khách hàng được đổi ngay 1 máy mới nguyên seal cùng model hoàn toàn miễn phí.', '2026-10-02 01:07:27'),
(4, 'Điện thoại tụt pin nhanh và nóng máy', 'Kỹ thuật', 'Samsung', 'Máy tụt pin nhanh bất thường, máy nóng khi dùng 4G hoặc lướt web.', 'Khách hàng thử tắt ứng dụng chạy ngầm và giảm độ sáng màn hình. Nếu máy tụt quá 20% pin/giờ khi không sử dụng, mời khách mang máy ra cửa hàng để kỹ thuật đo dòng và kiểm tra độ chai pin.', '2026-10-02 01:07:27'),
(5, 'Quên mật khẩu Apple ID / iCloud', 'Kỹ thuật', 'Apple', 'Khách quên mật khẩu iCloud, không tải được ứng dụng hoặc bị khóa máy.', 'Cửa hàng không thể tự mở khóa iCloud. Hướng dẫn khách truy cập iforgot.apple.com để đặt lại mật khẩu bằng SĐT đăng ký, hoặc mang hóa đơn mua hàng gốc đến để nhờ Apple hỗ trợ.', '2026-10-02 01:07:27'),
(6, 'Vỡ kính màn hình', 'Kỹ thuật', 'Tất cả', 'Máy bị rơi vỡ mặt kính nhưng màn hình vẫn hiển thị và cảm ứng bình thường.', 'Cửa hàng hỗ trợ ép kính lại với giá ưu đãi. Thời gian xử lý từ 2-4 tiếng tùy tình trạng và model máy.', '2026-10-02 01:07:27'),
(7, 'Thay pin chính hãng ở đâu', 'Kỹ thuật', 'Apple', 'Pin iPhone bị chai, báo bảo trì, cần thay pin chính hãng.', 'Cửa hàng có hỗ trợ thay pin dung lượng chuẩn hoặc dung lượng cao từ các hãng thứ 3 uy tín (Pisen, Energizer). Thay pin chính hãng Apple sẽ cần gửi về trung tâm bảo hành Apple.', '2026-10-02 01:07:27'),
(8, 'Camera bị mờ, rung', 'Kỹ thuật', 'Tất cả', 'Mở camera thấy hình ảnh bị mờ, rung lắc hoặc có đốm đen.', 'Nếu máy còn bảo hành và không có tác động vật lý, hãng sẽ hỗ trợ thay cụm camera mới. Hết bảo hành cửa hàng sẽ báo giá thay thế.', '2026-10-02 01:07:27'),
(9, 'Thu cũ đổi mới (Trade-in)', 'Bán hàng', 'Tất cả', 'Khách muốn bán lại máy cũ để lên đời máy mới.', 'Cửa hàng hỗ trợ thu mua máy cũ với giá cao. Máy cũ sẽ được định giá dựa trên ngoại hình và tình trạng hoạt động.', '2026-10-02 01:07:27'),
(10, 'Không nhận diện Face ID / Vân tay', 'Kỹ thuật', 'Tất cả', 'Máy báo không thể thiết lập Face ID hoặc không nhận vân tay.', 'Nếu lỗi do phần mềm, khởi động lại hoặc khôi phục cài đặt gốc có thể khắc phục. Nếu do phần cứng (cáp, cảm biến), cần kỹ thuật viên kiểm tra trực tiếp.', '2026-10-02 01:07:27'),
(11, 'Mất sóng, không nhận SIM', 'Kỹ thuật', 'Tất cả', 'Máy báo không có dịch vụ, không nhận SIM dù đã thử SIM khác.', 'Khách hàng thử bật tắt chế độ máy bay. Nếu không được, có thể do khe SIM hoặc IC sóng bị lỗi, cần mang ra cửa hàng để kiểm tra phần cứng.', '2026-10-02 01:07:27'),
(12, 'Loa bị rè, nghe gọi nhỏ', 'Kỹ thuật', 'Tất cả', 'Loa ngoài hoặc loa trong nghe rất nhỏ, bị rè khi bật âm lượng lớn.', 'Khách hàng dùng bàn chải mềm vệ sinh nhẹ màng loa. Nếu vẫn bị, kỹ thuật sẽ hỗ trợ vệ sinh chuyên sâu hoặc thay loa nếu màng loa đã rách.', '2026-10-02 01:07:27'),
(13, 'Sạc không vào pin', 'Kỹ thuật', 'Tất cả', 'Cắm sạc nhưng máy không báo sạc hoặc sạc rất chậm.', 'Thử đổi cáp sạc và củ sạc khác. Kiểm tra cổng sạc có bụi bẩn không. Nếu vẫn không được, có thể hỏng chân sạc hoặc IC sạc trên main.', '2026-10-02 01:07:27'),
(14, 'Bảo hành phụ kiện', 'Bảo hành', 'Tất cả', 'Cáp, sạc, tai nghe mua kèm máy hoặc mua lẻ bị lỗi.', 'Phụ kiện chính hãng mua kèm máy thường bảo hành 6-12 tháng tùy hãng. Phụ kiện mua lẻ bảo hành theo chính sách của nhà sản xuất, thường là 1 đổi 1 nếu lỗi do NSX.', '2026-10-02 01:07:27'),
(15, 'Màn hình bị chảy mực', 'Kỹ thuật', 'Tất cả', 'Màn hình xuất hiện đốm đen, ngày càng lan rộng ra xung quanh.', 'Chảy mực 100% do tác động vật lý (cấn, tì đè). Lỗi này bị từ chối bảo hành hãng, khách hàng phải chịu phí thay màn hình mới.', '2026-10-02 01:07:27'),
(16, 'Treo logo, chớp tắt', 'Kỹ thuật', 'Tất cả', 'Khởi động máy chỉ hiện logo rồi tắt hoặc treo luôn ở logo.', 'Có thể do lỗi xung đột phần mềm hoặc lỗi ổ cứng/mainboard. Cửa hàng sẽ thử chạy lại phần mềm trước, nếu không hết sẽ kiểm tra phần cứng.', '2026-10-02 01:07:27'),
(17, 'Hỗ trợ chuyển dữ liệu', 'Dịch vụ', 'Tất cả', 'Khách hàng mua máy mới muốn chuyển dữ liệu từ máy cũ sang.', 'Cửa hàng hỗ trợ chuyển toàn bộ danh bạ, ảnh, video, ứng dụng miễn phí khi khách mua máy mới. Thời gian tùy thuộc vào dung lượng dữ liệu.', '2026-10-02 01:07:27'),
(18, 'Lỗi cập nhật iOS/Android', 'Phần mềm', 'Tất cả', 'Đang cập nhật phần mềm thì máy báo lỗi, không lên nguồn.', 'Khách hàng mang máy ra cửa hàng, kỹ thuật viên sẽ dùng máy tính để chạy lại (restore/flash) bản Rom gốc mới nhất cho máy.', '2026-10-02 01:07:27'),
(19, 'Quên mật khẩu màn hình', 'Phần mềm', 'Tất cả', 'Khách hàng quên mật khẩu mở khóa màn hình điện thoại.', 'Cần khôi phục cài đặt gốc qua máy tính (sẽ mất toàn bộ dữ liệu trên máy). Yêu cầu khách phải nhớ mật khẩu iCloud/Google Account để kích hoạt lại.', '2026-10-02 01:07:27'),
(20, 'Lỗi kết nối WiFi/Bluetooth', 'Kỹ thuật', 'Tất cả', 'Máy không dò được WiFi, Bluetooth hoặc kết nối bị chập chờn.', 'Thử Reset lại cài đặt mạng trong phần Cài đặt. Nếu không cải thiện, có thể do chip WiFi/Bluetooth trên main bị lỗi, cần can thiệp phần cứng.', '2026-10-02 01:07:27');

-- ---------------------------------------------------------------------
-- BẢNG: `phone_products`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `phone_products`;
CREATE TABLE `phone_products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `slug` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `listed_price` decimal(15,2) NOT NULL,
  `promo_price` decimal(15,2) DEFAULT NULL,
  `stock_quantity` int DEFAULT '0',
  `stock_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'in_stock',
  `warehouse_location` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT 'Kho Tổng TP.HCM',
  `is_active` tinyint DEFAULT '1',
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `screen_spec` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `chip_spec` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ram_spec` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `storage_spec` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `camera_spec` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `battery_spec` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `os_spec` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `connectivity_spec` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `warranty_months` int DEFAULT '12',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_prod_brand` (`brand`),
  KEY `idx_prod_status` (`stock_status`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `phone_products` (6 bản ghi)
INSERT INTO `phone_products` (`id`, `name`, `brand`, `model`, `slug`, `description`, `listed_price`, `promo_price`, `stock_quantity`, `stock_status`, `warehouse_location`, `is_active`, `image_url`, `screen_spec`, `chip_spec`, `ram_spec`, `storage_spec`, `camera_spec`, `battery_spec`, `os_spec`, `connectivity_spec`, `warranty_months`, `created_at`, `updated_at`) VALUES
(1, 'iPhone 15 Pro Max', 'Apple', 'A3106', 'iphone-15-pro-max', 'Flagship cao cấp nhất của Apple với khung viền Titan siêu nhẹ, camera tiềm vọng 5x và chip A17 Pro mạnh mẽ vượt trội.', '34990000.00', '29990000.00', 15, 'in_stock', 'Kho Quận 1 (TP.HCM)', 1, 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop', '6.7 inch OLED Super Retina XDR 120Hz ProMotion', 'Apple A17 Pro (3nm)', '8GB', '256GB / 512GB / 1TB', 'Chính 48MP (F/1.78) + Siêu rộng 12MP + Tele 5x 12MP (OIS)', '4422 mAh, Sạc nhanh 25W, MagSafe 15W', 'iOS 17', '5G, Wi-Fi 6E, Bluetooth 5.3, USB-C 3.0', 12, '2026-10-02 01:06:19', '2026-10-02 01:06:19'),
(2, 'iPhone 15', 'Apple', 'A3090', 'iphone-15', 'Thiết kế mặt lưng nhám thời thượng, màn hình Dynamic Island thông minh và camera 48MP sắc nét.', '22990000.00', '19490000.00', 25, 'in_stock', 'Kho Quận 1 (TP.HCM)', 1, 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop', '6.1 inch OLED Super Retina XDR 60Hz Dynamic Island', 'Apple A16 Bionic (4nm)', '6GB', '128GB / 256GB', 'Chính 48MP + Siêu rộng 12MP (zoom 2x chất lượng quang học)', '3349 mAh, Sạc nhanh 20W, MagSafe', 'iOS 17', '5G, Wi-Fi 6, USB-C', 12, '2026-10-02 01:06:19', '2026-10-02 01:06:19'),
(3, 'Samsung Galaxy S24 Ultra', 'Samsung', 'SM-S928B', 'samsung-galaxy-s24-ultra', 'Siêu phẩm AI toàn năng với khung viền Titan, màn hình chống chói Dynamic AMOLED 2X và quyền năng Galaxy AI.', '33990000.00', '27990000.00', 12, 'in_stock', 'Kho Quận 3 (TP.HCM)', 1, 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop', '6.8 inch Dynamic AMOLED 2X 120Hz QHD+ Phẳng (Kính Gorilla Armor chống chói)', 'Snapdragon 8 Gen 3 for Galaxy (4nm)', '12GB', '256GB / 512GB / 1TB', 'Chính 200MP + Tele 50MP (5x) + Tele 10MP (3x) + Siêu rộng 12MP', '5000 mAh, Sạc nhanh 45W, Bút S-Pen', 'Android 14 (One UI 6.1, Galaxy AI)', '5G, Wi-Fi 7, Bluetooth 5.3, UWB', 12, '2026-10-02 01:06:19', '2026-10-02 01:06:19'),
(4, 'Samsung Galaxy A55 5G', 'Samsung', 'SM-A556B', 'samsung-galaxy-a55-5g', 'Điện thoại tầm trung xuất sắc với khung viền kim loại, chống nước IP67 và camera chụp đêm chuyên nghiệp.', '9990000.00', '8490000.00', 30, 'in_stock', 'Kho Quận 3 (TP.HCM)', 1, 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&auto=format&fit=crop', '6.6 inch Super AMOLED 120Hz FHD+ Vision Booster', 'Exynos 1480 (4nm)', '8GB', '128GB / 256GB', 'Chính 50MP (OIS) + Siêu rộng 12MP + Macro 5MP', '5000 mAh, Sạc nhanh 25W', 'Android 14 (One UI 6.1)', '5G, Wi-Fi 6, IP67', 12, '2026-10-02 01:06:19', '2026-10-02 01:06:19'),
(5, 'Xiaomi 14', 'Xiaomi', '23127PN0CC', 'xiaomi-14', 'Flagship nhỏ gọn hoàn hảo với ống kính quang học Leica Summilux đỉnh cao và hiệu năng bùng nổ.', '22990000.00', '18990000.00', 8, 'in_stock', 'Kho Tân Bình (TP.HCM)', 1, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop', '6.36 inch OLED 1.5K 120Hz LTPO viền siêu mỏng', 'Snapdragon 8 Gen 3 (4nm)', '12GB', '256GB / 512GB', 'Bộ 3 camera Leica 50MP (Chính + Tele 75mm + Siêu rộng)', '4610 mAh, Sạc siêu tốc 90W + Không dây 50W', 'Xiaomi HyperOS (Android 14)', '5G, Wi-Fi 7, Hồng ngoại IR, IP68', 24, '2026-10-02 01:06:19', '2026-10-02 01:06:19'),
(6, 'Oppo Find N3 5G', 'Oppo', 'CPH2499', 'oppo-find-n3', 'Tuyệt tác màn hình gập cao cấp không nếp gấp, camera Hasselblad đẳng cấp doanh nhân.', '44990000.00', '41990000.00', 5, 'in_stock', 'Kho Quận 1 (TP.HCM)', 1, 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500&auto=format&fit=crop', 'Màn trong 7.82 inch 120Hz + Màn ngoài 6.31 inch 120Hz', 'Snapdragon 8 Gen 2 (4nm)', '16GB', '512GB', 'Hasselblad: 48MP (Sony LYT-T808) + 64MP tiềm vọng + 48MP siêu rộng', '4805 mAh, Sạc SuperVOOC 67W', 'ColorOS 13.2 (Android 13)', '5G, Wi-Fi 7, Loa kép không gian', 12, '2026-10-02 01:06:19', '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `phone_variants`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `phone_variants`;
CREATE TABLE `phone_variants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `color` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `storage` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price_modifier` decimal(15,2) DEFAULT '0.00',
  `stock_quantity` int DEFAULT '10',
  `sku` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  KEY `idx_var_prod` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `phone_variants` (10 bản ghi)
INSERT INTO `phone_variants` (`id`, `product_id`, `color`, `storage`, `price_modifier`, `stock_quantity`, `sku`) VALUES
(1, 1, 'Titan Tự Nhiên', '256GB', '0.00', 8, 'IP15PM-256-NAT'),
(2, 1, 'Titan Đen', '256GB', '0.00', 5, 'IP15PM-256-BLK'),
(3, 1, 'Titan Xanh', '512GB', '5000000.00', 2, 'IP15PM-512-BLU'),
(4, 2, 'Xanh Pastel', '128GB', '0.00', 15, 'IP15-128-BLU'),
(5, 2, 'Hồng Pastel', '128GB', '0.00', 10, 'IP15-128-PNK'),
(6, 3, 'Xám Titan', '256GB', '0.00', 7, 'S24U-256-GRY'),
(7, 3, 'Đen Titan', '512GB', '4000000.00', 5, 'S24U-512-BLK'),
(8, 4, 'Xanh Iceblue', '128GB', '0.00', 20, 'A55-128-ICE'),
(9, 5, 'Đen Nhám', '256GB', '0.00', 8, 'MI14-256-BLK'),
(10, 6, 'Vàng Cổ Điển', '512GB', '0.00', 5, 'N3-512-GLD');

-- ---------------------------------------------------------------------
-- BẢNG: `product_price_history`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `product_price_history`;
CREATE TABLE `product_price_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `old_listed_price` decimal(15,2) DEFAULT NULL,
  `new_listed_price` decimal(15,2) DEFAULT NULL,
  `old_promo_price` decimal(15,2) DEFAULT NULL,
  `new_promo_price` decimal(15,2) DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_by_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_hist_prod` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `promotions`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `promotions`;
CREATE TABLE `promotions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `promo_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `discount_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'fixed',
  `discount_value` decimal(15,2) NOT NULL,
  `min_order_amount` decimal(15,2) DEFAULT '0.00',
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `is_active` tinyint DEFAULT '1',
  `applicable_brands` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'all',
  PRIMARY KEY (`id`),
  UNIQUE KEY `promo_code` (`promo_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `promotions` (3 bản ghi)
INSERT INTO `promotions` (`id`, `promo_code`, `name`, `discount_type`, `discount_value`, `min_order_amount`, `start_date`, `end_date`, `is_active`, `applicable_brands`) VALUES
(1, 'TET2026', 'Lì Xì Tết - Giảm 1.000.000đ cho đơn từ 20 triệu', 'fixed', '1000000.00', '20000000.00', '2026-01-01', '2026-12-31', 1, 'all'),
(2, 'APPLE500', 'Ưu đãi khách hàng thân thiết mua Apple', 'fixed', '500000.00', '15000000.00', '2026-01-01', '2026-12-31', 1, 'Apple'),
(3, 'SAM5PERCENT', 'Giảm 5% cho dòng Galaxy S24 Ultra', 'percent', '5.00', '25000000.00', '2026-01-01', '2026-12-31', 1, 'Samsung');

-- ---------------------------------------------------------------------
-- BẢNG: `quotations`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `quotations`;
CREATE TABLE `quotations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quote_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` int NOT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `agent_id` int NOT NULL,
  `agent_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_listed_amount` decimal(15,2) DEFAULT '0.00',
  `discount_amount` decimal(15,2) DEFAULT '0.00',
  `final_amount` decimal(15,2) DEFAULT '0.00',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'sent',
  `items_json` text COLLATE utf8mb4_unicode_ci,
  `promotion_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `expiry_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `quote_code` (`quote_code`),
  KEY `idx_quote_cust` (`customer_id`),
  KEY `idx_quote_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `quotations` (1 bản ghi)
INSERT INTO `quotations` (`id`, `quote_code`, `customer_id`, `customer_name`, `customer_phone`, `agent_id`, `agent_name`, `total_listed_amount`, `discount_amount`, `final_amount`, `status`, `items_json`, `promotion_code`, `notes`, `expiry_date`, `created_at`, `updated_at`) VALUES
(1, 'BG-2026-1001', 1, 'Lê Khách Hàng VIP', '0987654321', 2, 'Nguyễn Văn Hỗ Trợ', '34990000.00', '5000000.00', '29990000.00', 'sent', '[{"product_id": 1, "name": "iPhone 15 Pro Max 256GB (Titan Tự Nhiên)", "qty": 1, "listed_price": 34990000.0, "promo_price": 29990000.0, "subtotal": 29990000.0}]', 'APPLE500', 'Báo giá ưu đãi kèm gói dán màn hình cao cấp và ốp lưng chính hãng', '2026-12-31', '2026-10-02 01:06:19', '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `sales_orders`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `sales_orders`;
CREATE TABLE `sales_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quote_id` int DEFAULT NULL,
  `customer_id` int NOT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `agent_id` int NOT NULL,
  `total_amount` decimal(15,2) NOT NULL,
  `discount_amount` decimal(15,2) DEFAULT '0.00',
  `final_amount` decimal(15,2) NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'new',
  `shipping_address` text COLLATE utf8mb4_unicode_ci,
  `receiver_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `receiver_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_carrier` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'GHN',
  `payment_method` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'cod',
  `items_json` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_code` (`order_code`),
  KEY `idx_so_cust` (`customer_id`),
  KEY `idx_so_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `orders`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` decimal(15,2) DEFAULT '0.00',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'completed',
  `shipping_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_carrier` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_status` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `items_summary` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_code` (`order_code`),
  KEY `idx_ord_phone` (`customer_phone`),
  KEY `idx_ord_ship` (`shipping_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `order_status_history`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `order_status_history`;
CREATE TABLE `order_status_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `old_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `changed_by` int DEFAULT NULL,
  `changed_by_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_hist_order` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `sales_opportunities`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `sales_opportunities`;
CREATE TABLE `sales_opportunities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int DEFAULT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` decimal(15,2) DEFAULT '0.00',
  `stage` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'lead',
  `probability` int DEFAULT '20',
  `assigned_agent_id` int DEFAULT NULL,
  `expected_close_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_opp_stage` (`stage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `warranties`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `warranties`;
CREATE TABLE `warranties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `warranty_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_id` int DEFAULT NULL,
  `customer_id` int NOT NULL,
  `customer_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_id` int NOT NULL,
  `product_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `imei_serial` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `warranty_package` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT 'Bảo hành chính hãng 12 tháng',
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `warranty_code` (`warranty_code`),
  KEY `idx_warr_cust` (`customer_id`),
  KEY `idx_warr_imei` (`imei_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `warranties` (1 bản ghi)
INSERT INTO `warranties` (`id`, `warranty_code`, `order_id`, `customer_id`, `customer_name`, `customer_phone`, `product_id`, `product_name`, `imei_serial`, `warranty_package`, `start_date`, `end_date`, `status`, `created_at`) VALUES
(1, 'BH-2026-9011', 1, 1, 'Lê Khách Hàng VIP', '0987654321', 1, 'iPhone 15 Pro Max 256GB', '356789012345678', 'Bảo hành chính hãng 12 tháng Apple Care+', '2026-01-15', '2027-01-15', 'active', '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `followup_reminders`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `followup_reminders`;
CREATE TABLE `followup_reminders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `agent_id` int NOT NULL,
  `reminder_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `due_date` date NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `completed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_rem_agent` (`agent_id`),
  KEY `idx_rem_due` (`due_date`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dữ liệu khởi tạo cho bảng `followup_reminders` (1 bản ghi)
INSERT INTO `followup_reminders` (`id`, `customer_id`, `order_id`, `agent_id`, `reminder_type`, `due_date`, `content`, `status`, `completed_at`, `created_at`) VALUES
(1, 1, 1, 2, '7_day_satisfaction', '2026-10-02', 'Gọi điện hỏi thăm khách hàng sau 7 ngày nhận máy iPhone 15 Pro Max, kiểm tra tình trạng sử dụng và hướng dẫn kích hoạt iCloud', 'pending', NULL, '2026-10-02 01:06:19');

-- ---------------------------------------------------------------------
-- BẢNG: `omnichannel_messages`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `omnichannel_messages`;
CREATE TABLE `omnichannel_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `external_msg_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `conversation_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sender_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `direction` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `raw_payload` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_conv` (`conversation_id`),
  KEY `idx_ext_msg` (`external_msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `auto_replies`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `auto_replies`;
CREATE TABLE `auto_replies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trigger_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint DEFAULT '1',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ch_trg` (`channel`,`trigger_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `call_logs`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `call_logs`;
CREATE TABLE `call_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agent_id` int DEFAULT NULL,
  `customer_phone` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `direction` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'outbound',
  `call_duration` int DEFAULT '0',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'completed',
  `recording_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `call_sid` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_call_phone` (`customer_phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `work_shifts`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `work_shifts`;
CREATE TABLE `work_shifts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agent_id` int NOT NULL,
  `shift_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shift_date` date NOT NULL,
  `start_time` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `end_time` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'scheduled',
  `check_in_time` timestamp NULL DEFAULT NULL,
  `check_out_time` timestamp NULL DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_shift_agent` (`agent_id`),
  KEY `idx_shift_date` (`shift_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `idempotent_keys`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `idempotent_keys`;
CREATE TABLE `idempotent_keys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scope` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_name` (`key_name`),
  KEY `idx_key_scope` (`scope`,`key_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BẢNG: `audit_logs`
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci,
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_audit_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
-- =====================================================================
-- HOÀN TẤT ĐỒNG BỘ 100% CƠ SỞ DỮ LIỆU MYSQL CHO DỰ ÁN CRM & BÁN HÀNG
-- =====================================================================
