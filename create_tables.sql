-- 创建用户表（已移除部门相关字段）
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    employee_id VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    role ENUM('admin', 'manager', 'worker') NOT NULL DEFAULT 'worker',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 创建工具分类表（支持多级分类）
CREATE TABLE IF NOT EXISTS tool_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    parent_id INT NULL,
    FOREIGN KEY (parent_id) REFERENCES tool_categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 创建存放位置表
CREATE TABLE IF NOT EXISTS storage_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 创建工具主表
CREATE TABLE IF NOT EXISTS tools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    specification TEXT,
    total_quantity INT NOT NULL DEFAULT 0,
    manufacturer VARCHAR(100),
    purchase_date DATE,
    category_id INT,
    min_quantity INT DEFAULT 1 COMMENT '库存预警值',
    status ENUM('可用', '借出', '维修中', '报废') DEFAULT '可用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES tool_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 工具-存放位置关联表（多对多关系）
CREATE TABLE IF NOT EXISTS tool_locations (
    tool_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (tool_id, location_id),
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES storage_locations(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 创建借还记录表
CREATE TABLE IF NOT EXISTS borrow_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tool_id INT NOT NULL,
    user_id INT NOT NULL,
    quantity INT NOT NULL,
    borrow_date DATETIME NOT NULL,
    due_date DATETIME NOT NULL,
    return_date DATETIME,
    reason TEXT,
    tool_status_before ENUM('可用', '借出', '维修中', '报废'),
    tool_status_after ENUM('可用', '借出', '维修中', '报废'),
    status ENUM('待审批', '已借出', '已归还', '已拒绝', '逾期未还') DEFAULT '待审批',
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 创建审批流程表
CREATE TABLE IF NOT EXISTS approval_flows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    approver_id INT NOT NULL,
    approval_step INT NOT NULL,
    status ENUM('待审批', '已批准', '已拒绝') DEFAULT '待审批',
    comments TEXT,
    action_date DATETIME,
    FOREIGN KEY (record_id) REFERENCES borrow_records(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 创建工具维护记录表
CREATE TABLE IF NOT EXISTS tool_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tool_id INT NOT NULL,
    maintenance_date DATETIME NOT NULL,
    maintenance_type ENUM('日常保养', '定期检修', '故障维修') NOT NULL,
    description TEXT,
    technician VARCHAR(100),
    next_maintenance_date DATETIME,
    status_before ENUM('可用', '借出', '维修中', '报废'),
    status_after ENUM('可用', '借出', '维修中', '报废'),
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 创建库存统计快照表
CREATE TABLE IF NOT EXISTS inventory_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    snapshot_date DATETIME NOT NULL,
    total_tools INT NOT NULL,
    available_tools INT NOT NULL,
    borrowed_tools INT NOT NULL,
    under_maintenance INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 创建工具使用统计表
CREATE TABLE IF NOT EXISTS tool_usage_stats (
    tool_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    borrow_count INT NOT NULL DEFAULT 0,
    total_borrow_days INT NOT NULL DEFAULT 0,
    avg_borrow_duration DECIMAL(10,2),
    PRIMARY KEY (tool_id, year, month),
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 创建提醒记录表
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_record_id INT COMMENT '相关记录ID',
    related_type VARCHAR(50) COMMENT '相关记录类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);