-- 用户表增加部门外键约束
ALTER TABLE users
MODIFY COLUMN department_id INT,
ADD CONSTRAINT fk_user_department
FOREIGN KEY (department_id) REFERENCES departments(id)
ON DELETE SET NULL;

-- 工具表增加分类表外键
CREATE TABLE IF NOT EXISTS tool_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    parent_id INT NULL,
    FOREIGN KEY (parent_id) REFERENCES tool_categories(id)
);

ALTER TABLE tools
MODIFY COLUMN category INT,
ADD CONSTRAINT fk_tool_category
FOREIGN KEY (category) REFERENCES tool_categories(id)
ON DELETE SET NULL;

-- 工具-存放位置关联表（多对多关系）
CREATE TABLE IF NOT EXISTS tool_locations (
    tool_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (tool_id, location_id),
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES storage_locations(id) ON DELETE CASCADE
);

-- 工具-维护记录关联表
CREATE TABLE IF NOT EXISTS tool_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tool_id INT NOT NULL,
    maintenance_date DATETIME NOT NULL,
    maintenance_type ENUM('日常保养', '定期检修', '故障维修') NOT NULL,
    description TEXT,
    technician VARCHAR(100),
    next_maintenance_date DATETIME,
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
);

-- 借还记录表增加工具状态快照
ALTER TABLE borrow_records
ADD COLUMN tool_status_before ENUM('可用', '借出', '维修中', '报废'),
ADD COLUMN tool_status_after ENUM('可用', '借出', '维修中', '报废');

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
    FOREIGN KEY (approver_id) REFERENCES users(id)
);


-- 创建统计快照表
CREATE TABLE IF NOT EXISTS inventory_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    snapshot_date DATETIME NOT NULL,
    total_tools INT NOT NULL,
    available_tools INT NOT NULL,
    borrowed_tools INT NOT NULL,
    under_maintenance INT NOT NULL
);

-- 工具使用频率统计表
CREATE TABLE IF NOT EXISTS tool_usage_stats (
    tool_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    borrow_count INT NOT NULL DEFAULT 0,
    total_borrow_days INT NOT NULL DEFAULT 0,
    PRIMARY KEY (tool_id, year, month),
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
);