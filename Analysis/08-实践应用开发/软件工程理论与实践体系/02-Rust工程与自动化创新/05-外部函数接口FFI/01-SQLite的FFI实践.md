# Rust FFI实践：安全包装libsqlite3

外部函数接口（Foreign Function Interface, FFI）是Rust与C/C++等其他语言编写的库进行交互的关键机制。本节通过一个完整的示例，展示如何为C库`libsqlite3`创建一个安全、符合Rust习惯的包装器。

这个过程主要包括：

1. **声明C接口**：使用`extern "C"`块声明C库中的类型、常量和函数。
2. **创建安全包装**：设计Rust结构体和方法，封装不安全的`unsafe`操作。
3. **管理资源**：利用Rust的`Drop`特征实现资源的自动和安全释放（例如，数据库连接、预处理语句）。

## 核心实现

```rust
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

// 1. C接口声明
// 使用`#[repr(C)]`确保Rust结构体与C的内存布局兼容。
// `_private`字段是一个零大小数组，用于防止直接在Rust中实例化这些类型，
// 因为它们只能由C库创建和管理。
#[repr(C)]
pub struct sqlite3 {
    _private: [u8; 0],
}

#[repr(C)]
pub struct sqlite3_stmt {
    _private: [u8; 0],
}

// C库中的常量定义
const SQLITE_OK: c_int = 0;
const SQLITE_ROW: c_int = 100;
const SQLITE_DONE: c_int = 101;

// `extern "C"`块声明了我们将要调用的C函数签名
extern "C" {
    fn sqlite3_open(filename: *const c_char, ppDb: *mut *mut sqlite3) -> c_int;
    fn sqlite3_close(db: *mut sqlite3) -> c_int;
    fn sqlite3_prepare_v2(
        db: *mut sqlite3,
        zSql: *const c_char,
        nByte: c_int,
        ppStmt: *mut *mut sqlite3_stmt,
        pzTail: *mut *const c_char,
    ) -> c_int;
    fn sqlite3_step(stmt: *mut sqlite3_stmt) -> c_int;
    fn sqlite3_column_text(stmt: *mut sqlite3_stmt, iCol: c_int) -> *const c_char;
    fn sqlite3_column_int(stmt: *mut sqlite3_stmt, iCol: c_int) -> c_int;
    fn sqlite3_finalize(stmt: *mut sqlite3_stmt) -> c_int;
    fn sqlite3_errmsg(db: *mut sqlite3) -> *const c_char;
}

// 2. 安全的Rust包装 (Safe Rust Wrapper)
pub struct Database {
    handle: *mut sqlite3,
}

impl Database {
    // 封装了打开数据库的`unsafe`操作
    pub fn open(path: &str) -> Result<Self, String> {
        let c_path = CString::new(path).map_err(|e| e.to_string())?;
        let mut handle: *mut sqlite3 = std::ptr::null_mut();
        
        unsafe {
            let result = sqlite3_open(c_path.as_ptr(), &mut handle);
            
            if result != SQLITE_OK {
                let error = if !handle.is_null() {
                    let error_msg = CStr::from_ptr(sqlite3_errmsg(handle))
                        .to_string_lossy()
                        .to_string();
                    sqlite3_close(handle); // 尝试关闭以释放资源
                    error_msg
                } else {
                    "SQLite无法打开数据库且未提供错误句柄".to_string()
                };
                return Err(error);
            }
        }
        
        Ok(Database { handle })
    }
    
    // 封装了执行查询的`unsafe`操作
    pub fn query<T, F>(&self, sql: &str, mut row_callback: F) -> Result<(), String>
    where
        F: FnMut(Row) -> T,
    {
        let c_sql = CString::new(sql).map_err(|e| e.to_string())?;
        let mut stmt: *mut sqlite3_stmt = std::ptr::null_mut();
        
        unsafe {
            let result = sqlite3_prepare_v2(
                self.handle,
                c_sql.as_ptr(),
                -1, // 告诉SQLite自动计算SQL字符串的长度
                &mut stmt,
                std::ptr::null_mut(),
            );
            
            if result != SQLITE_OK {
                return Err(CStr::from_ptr(sqlite3_errmsg(self.handle))
                    .to_string_lossy()
                    .to_string());
            }
            
            loop {
                let step_result = sqlite3_step(stmt);
                
                match step_result {
                    SQLITE_ROW => {
                        let row = Row { stmt };
                        row_callback(row);
                    }
                    SQLITE_DONE => break,
                    _ => {
                        let error = CStr::from_ptr(sqlite3_errmsg(self.handle))
                            .to_string_lossy()
                            .to_string();
                        sqlite3_finalize(stmt);
                        return Err(error);
                    }
                }
            }
            
            sqlite3_finalize(stmt);
        }
        
        Ok(())
    }
}

// 3. 封装行数据访问
pub struct Row {
    stmt: *mut sqlite3_stmt,
}

impl Row {
    pub fn get_text(&self, column: i32) -> Option<String> {
        unsafe {
            let text_ptr = sqlite3_column_text(self.stmt, column);
            if text_ptr.is_null() {
                None
            } else {
                Some(CStr::from_ptr(text_ptr).to_string_lossy().to_string())
            }
        }
    }
    
    pub fn get_int(&self, column: i32) -> i32 {
        unsafe { sqlite3_column_int(self.stmt, column) }
    }
}

// 4. 实现`Drop`以进行自动资源清理
impl Drop for Database {
    fn drop(&mut self) {
        if !self.handle.is_null() {
            unsafe {
                sqlite3_close(self.handle);
            }
        }
    }
}

// 5. 使用示例
fn use_sqlite_example() -> Result<(), String> {
    let db = Database::open(":memory:")?;
    
    db.query("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)", |row|{})?;
    db.query("INSERT INTO users (name) VALUES ('Alice'), ('Bob')", |row|{})?;

    println!("Users in database:");
    db.query("SELECT id, name FROM users", |row| {
        println!(" - ID: {}, Name: {}", row.get_int(0), row.get_text(1).unwrap_or_default());
    })?;
    
    Ok(())
}
