-- for mysql only
CREATE TABLE IF NOT EXISTS user_basic_info (
    userid INT PRIMARY KEY NOT NULL AUTO_INCREMENT, -- 系统内的ID
    username VARCHAR(64) UNIQUE NOT NULL,       -- 用户名
    e_passwd VARCHAR(64) NOT NULL,              -- 加密后的密码
    e_salt VARCHAR(32) NOT NULL,                -- Salt
    schoolid VARCHAR(7) UNIQUE NOT NULL,        -- 学号
    confirmed BOOLEAN DEFAULT 0,                -- 管理员验证后为1
    vip_level INT DEFAULT 0,                    -- 会员等级
    sent_txl INT DEFAULT 0                      -- 是否已发送本级的同学录
);

CREATE TABLE IF NOT EXISTS txl_2025 (
    txid INT PRIMARY KEY AUTO_INCREMENT NOT NULL,   -- 留言ID
    publisher_id INT NOT NULL UNIQUE,           -- 留言者ID
    content JSON NOT NULL,                      -- 留言内容
    is_anonymous BOOLEAN DEFAULT 0              -- 是否匿名
) AUTO_INCREMENT=20250000;


CREATE TABLE IF NOT EXISTS user_token (
    userid INT PRIMARY KEY NOT NULL AUTO_INCREMENT,            -- 用户ID
    token VARCHAR(64) NOT NULL                 -- Token
);