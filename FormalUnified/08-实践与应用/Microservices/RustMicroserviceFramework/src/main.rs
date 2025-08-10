use actix_web::{web, App, HttpServer, HttpResponse, Result, middleware::Logger};
use actix_web::http::StatusCode;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::time::{Duration, interval};
use uuid::Uuid;

/// 服务注册信息
#[derive(Debug, Clone, Serialize, Deserialize)]
struct ServiceInfo {
    service_id: String,
    service_name: String,
    service_version: String,
    host: String,
    port: u16,
    health_check_url: String,
    metadata: HashMap<String, String>,
    last_heartbeat: u64,
    status: ServiceStatus,
}

/// 服务状态枚举
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
enum ServiceStatus {
    Healthy,
    Unhealthy,
    Unknown,
}

/// 服务注册请求
#[derive(Debug, Deserialize)]
struct ServiceRegistrationRequest {
    service_name: String,
    service_version: String,
    host: String,
    port: u16,
    health_check_url: String,
    metadata: HashMap<String, String>,
}

/// 服务发现请求
#[derive(Debug, Deserialize)]
struct ServiceDiscoveryRequest {
    service_name: String,
    service_version: Option<String>,
}

/// 服务注册中心
struct ServiceRegistry {
    services: Arc<Mutex<HashMap<String, ServiceInfo>>>,
}

impl ServiceRegistry {
    fn new() -> Self {
        Self {
            services: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// 注册服务
    fn register_service(&self, request: ServiceRegistrationRequest) -> Result<String, String> {
        let service_id = Uuid::new_v4().to_string();
        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let service_info = ServiceInfo {
            service_id: service_id.clone(),
            service_name: request.service_name,
            service_version: request.service_version,
            host: request.host,
            port: request.port,
            health_check_url: request.health_check_url,
            metadata: request.metadata,
            last_heartbeat: current_time,
            status: ServiceStatus::Healthy,
        };

        let mut services = self.services.lock().unwrap();
        services.insert(service_id.clone(), service_info);

        Ok(service_id)
    }

    /// 注销服务
    fn unregister_service(&self, service_id: &str) -> Result<(), String> {
        let mut services = self.services.lock().unwrap();
        if services.remove(service_id).is_some() {
            Ok(())
        } else {
            Err("Service not found".to_string())
        }
    }

    /// 更新服务心跳
    fn update_heartbeat(&self, service_id: &str) -> Result<(), String> {
        let mut services = self.services.lock().unwrap();
        if let Some(service) = services.get_mut(service_id) {
            let current_time = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            service.last_heartbeat = current_time;
            service.status = ServiceStatus::Healthy;
            Ok(())
        } else {
            Err("Service not found".to_string())
        }
    }

    /// 发现服务
    fn discover_service(&self, request: &ServiceDiscoveryRequest) -> Vec<ServiceInfo> {
        let services = self.services.lock().unwrap();
        services
            .values()
            .filter(|service| {
                service.service_name == request.service_name
                    && service.status == ServiceStatus::Healthy
                    && match &request.service_version {
                        Some(version) => service.service_version == *version,
                        None => true,
                    }
            })
            .cloned()
            .collect()
    }

    /// 获取所有服务
    fn get_all_services(&self) -> Vec<ServiceInfo> {
        let services = self.services.lock().unwrap();
        services.values().cloned().collect()
    }

    /// 清理过期服务
    fn cleanup_expired_services(&self, timeout_seconds: u64) {
        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let mut services = self.services.lock().unwrap();
        services.retain(|_, service| {
            if current_time - service.last_heartbeat > timeout_seconds {
                service.status = ServiceStatus::Unhealthy;
                false
            } else {
                true
            }
        });
    }
}

/// 负载均衡器
struct LoadBalancer {
    registry: Arc<ServiceRegistry>,
}

impl LoadBalancer {
    fn new(registry: Arc<ServiceRegistry>) -> Self {
        Self { registry }
    }

    /// 轮询负载均衡
    fn round_robin(&self, service_name: &str) -> Option<ServiceInfo> {
        let services = self.registry.discover_service(&ServiceDiscoveryRequest {
            service_name: service_name.to_string(),
            service_version: None,
        });

        if services.is_empty() {
            None
        } else {
            // 简单的轮询实现
            let current_time = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            let index = (current_time % services.len() as u64) as usize;
            Some(services[index].clone())
        }
    }

    /// 随机负载均衡
    fn random(&self, service_name: &str) -> Option<ServiceInfo> {
        let services = self.registry.discover_service(&ServiceDiscoveryRequest {
            service_name: service_name.to_string(),
            service_version: None,
        });

        if services.is_empty() {
            None
        } else {
            use rand::Rng;
            let mut rng = rand::thread_rng();
            let index = rng.gen_range(0..services.len());
            Some(services[index].clone())
        }
    }
}

/// 健康检查处理器
async fn health_check() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "timestamp": SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
    })))
}

/// 服务注册处理器
async fn register_service(
    registry: web::Data<Arc<ServiceRegistry>>,
    request: web::Json<ServiceRegistrationRequest>,
) -> Result<HttpResponse> {
    match registry.register_service(request.into_inner()) {
        Ok(service_id) => Ok(HttpResponse::Created().json(serde_json::json!({
            "service_id": service_id,
            "message": "Service registered successfully"
        }))),
        Err(error) => Ok(HttpResponse::BadRequest().json(serde_json::json!({
            "error": error
        }))),
    }
}

/// 服务注销处理器
async fn unregister_service(
    registry: web::Data<Arc<ServiceRegistry>>,
    service_id: web::Path<String>,
) -> Result<HttpResponse> {
    match registry.unregister_service(&service_id) {
        Ok(_) => Ok(HttpResponse::Ok().json(serde_json::json!({
            "message": "Service unregistered successfully"
        }))),
        Err(error) => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "error": error
        }))),
    }
}

/// 服务发现处理器
async fn discover_service(
    registry: web::Data<Arc<ServiceRegistry>>,
    request: web::Json<ServiceDiscoveryRequest>,
) -> Result<HttpResponse> {
    let services = registry.discover_service(&request);
    Ok(HttpResponse::Ok().json(services))
}

/// 心跳更新处理器
async fn heartbeat(
    registry: web::Data<Arc<ServiceRegistry>>,
    service_id: web::Path<String>,
) -> Result<HttpResponse> {
    match registry.update_heartbeat(&service_id) {
        Ok(_) => Ok(HttpResponse::Ok().json(serde_json::json!({
            "message": "Heartbeat updated successfully"
        }))),
        Err(error) => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "error": error
        }))),
    }
}

/// 获取所有服务处理器
async fn get_all_services(
    registry: web::Data<Arc<ServiceRegistry>>,
) -> Result<HttpResponse> {
    let services = registry.get_all_services();
    Ok(HttpResponse::Ok().json(services))
}

/// 负载均衡处理器
async fn load_balance(
    load_balancer: web::Data<Arc<LoadBalancer>>,
    service_name: web::Path<String>,
    query: web::Query<HashMap<String, String>>,
) -> Result<HttpResponse> {
    let strategy = query.get("strategy").unwrap_or(&"round_robin".to_string());
    
    let service = match strategy.as_str() {
        "random" => load_balancer.random(&service_name),
        _ => load_balancer.round_robin(&service_name),
    };

    match service {
        Some(service_info) => Ok(HttpResponse::Ok().json(service_info)),
        None => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "error": "No healthy service found"
        }))),
    }
}

/// 启动服务清理任务
async fn start_cleanup_task(registry: Arc<ServiceRegistry>) {
    let mut interval = interval(Duration::from_secs(30)); // 每30秒清理一次
    
    loop {
        interval.tick().await;
        registry.cleanup_expired_services(60); // 60秒超时
        println!("Cleaned up expired services");
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // 初始化日志
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    // 创建服务注册中心
    let registry = Arc::new(ServiceRegistry::new());
    
    // 创建负载均衡器
    let load_balancer = Arc::new(LoadBalancer::new(registry.clone()));

    // 启动服务清理任务
    let cleanup_registry = registry.clone();
    tokio::spawn(start_cleanup_task(cleanup_registry));

    println!("🚀 微服务注册中心启动中...");
    println!("📍 服务地址: http://localhost:8080");
    println!("📋 API文档:");
    println!("   POST /api/v1/services/register    - 服务注册");
    println!("   DELETE /api/v1/services/{id}      - 服务注销");
    println!("   POST /api/v1/services/discover    - 服务发现");
    println!("   PUT /api/v1/services/{id}/heartbeat - 心跳更新");
    println!("   GET /api/v1/services              - 获取所有服务");
    println!("   GET /api/v1/load-balance/{name}  - 负载均衡");
    println!("   GET /health                       - 健康检查");

    // 启动HTTP服务器
    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(registry.clone()))
            .app_data(web::Data::new(load_balancer.clone()))
            .service(
                web::scope("/api/v1")
                    .service(
                        web::scope("/services")
                            .route("/register", web::post().to(register_service))
                            .route("/discover", web::post().to(discover_service))
                            .route("/{service_id}", web::delete().to(unregister_service))
                            .route("/{service_id}/heartbeat", web::put().to(heartbeat))
                            .route("", web::get().to(get_all_services))
                    )
            )
            .service(
                web::scope("/api/v1/load-balance")
                    .route("/{service_name}", web::get().to(load_balance))
            )
            .route("/health", web::get().to(health_check))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
} 