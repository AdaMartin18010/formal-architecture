//! Core data structures and types for formal architecture verification

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use thiserror::Error;

/// Global state for the library
static mut GLOBAL_STATE: Option<Arc<Mutex<GlobalState>>> = None;

/// Global state structure
#[derive(Debug)]
struct GlobalState {
    /// Registry of registered components
    component_registry: HashMap<String, Component>,
    /// Registry of verification strategies
    verification_strategies: HashMap<String, Box<dyn VerificationStrategy>>,
    /// Configuration settings
    config: Config,
}

/// Configuration settings
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Enable debug logging
    pub debug: bool,
    /// Maximum verification time in seconds
    pub max_verification_time: u64,
    /// Enable parallel processing
    pub parallel: bool,
    /// Output format
    pub output_format: OutputFormat,
}

/// Output format for verification results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OutputFormat {
    Json,
    Yaml,
    Text,
    Markdown,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            debug: false,
            max_verification_time: 300, // 5 minutes
            parallel: true,
            output_format: OutputFormat::Json,
        }
    }
}

/// Initialize global state
pub fn init_global_state() -> Result<(), Box<dyn std::error::Error>> {
    unsafe {
        if GLOBAL_STATE.is_none() {
            GLOBAL_STATE = Some(Arc::new(Mutex::new(GlobalState {
                component_registry: HashMap::new(),
                verification_strategies: HashMap::new(),
                config: Config::default(),
            })));
        }
    }
    Ok(())
}

/// Cleanup global state
pub fn cleanup_global_state() {
    unsafe {
        GLOBAL_STATE = None;
    }
}

/// Get global state reference
pub fn get_global_state() -> Option<Arc<Mutex<GlobalState>>> {
    unsafe { GLOBAL_STATE.clone() }
}

/// Architecture represents a software architecture
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Architecture {
    /// Architecture name
    pub name: String,
    /// Architecture description
    pub description: String,
    /// Components in the architecture
    pub components: Vec<Component>,
    /// Connections between components
    pub connections: Vec<Connection>,
    /// Properties to verify
    pub properties: Vec<Property>,
    /// Metadata
    pub metadata: HashMap<String, String>,
}

impl Architecture {
    /// Create a new architecture
    pub fn new(name: String, description: String) -> Self {
        Self {
            name,
            description,
            components: Vec::new(),
            connections: Vec::new(),
            properties: Vec::new(),
            metadata: HashMap::new(),
        }
    }

    /// Add a component to the architecture
    pub fn add_component(&mut self, component: Component) {
        self.components.push(component);
    }

    /// Add a connection to the architecture
    pub fn add_connection(&mut self, connection: Connection) {
        self.connections.push(connection);
    }

    /// Add a property to verify
    pub fn add_property(&mut self, property: Property) {
        self.properties.push(property);
    }

    /// Get component by name
    pub fn get_component(&self, name: &str) -> Option<&Component> {
        self.components.iter().find(|c| c.name == name)
    }

    /// Get connection by name
    pub fn get_connection(&self, name: &str) -> Option<&Connection> {
        self.connections.iter().find(|c| c.name == name)
    }

    /// Validate architecture consistency
    pub fn validate(&self) -> Result<(), ArchitectureError> {
        // Check for duplicate component names
        let mut names = std::collections::HashSet::new();
        for component in &self.components {
            if !names.insert(&component.name) {
                return Err(ArchitectureError::DuplicateComponentName(component.name.clone()));
            }
        }

        // Check for duplicate connection names
        let mut names = std::collections::HashSet::new();
        for connection in &self.connections {
            if !names.insert(&connection.name) {
                return Err(ArchitectureError::DuplicateConnectionName(connection.name.clone()));
            }
        }

        // Check that all connections reference valid components
        for connection in &self.connections {
            if !self.components.iter().any(|c| c.name == connection.source) {
                return Err(ArchitectureError::InvalidComponentReference(connection.source.clone()));
            }
            if !self.components.iter().any(|c| c.name == connection.target) {
                return Err(ArchitectureError::InvalidComponentReference(connection.target.clone()));
            }
        }

        Ok(())
    }
}

/// Component represents a software component
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Component {
    /// Component name
    pub name: String,
    /// Component type
    pub component_type: ComponentType,
    /// Interfaces provided by this component
    pub provided_interfaces: Vec<Interface>,
    /// Interfaces required by this component
    pub required_interfaces: Vec<Interface>,
    /// Component properties
    pub properties: HashMap<String, String>,
    /// Component implementation details
    pub implementation: Option<Implementation>,
}

/// Component type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ComponentType {
    Service,
    Library,
    Database,
    MessageQueue,
    Cache,
    LoadBalancer,
    Gateway,
    Custom(String),
}

/// Interface represents a component interface
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Interface {
    /// Interface name
    pub name: String,
    /// Interface type
    pub interface_type: InterfaceType,
    /// Methods or operations
    pub methods: Vec<Method>,
    /// Interface properties
    pub properties: HashMap<String, String>,
}

/// Interface type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InterfaceType {
    REST,
    GraphQL,
    gRPC,
    Message,
    Database,
    File,
    Custom(String),
}

/// Method represents an interface method
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Method {
    /// Method name
    pub name: String,
    /// Method parameters
    pub parameters: Vec<Parameter>,
    /// Return type
    pub return_type: Option<String>,
    /// Method properties
    pub properties: HashMap<String, String>,
}

/// Parameter represents a method parameter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    /// Parameter name
    pub name: String,
    /// Parameter type
    pub parameter_type: String,
    /// Whether parameter is required
    pub required: bool,
    /// Default value
    pub default_value: Option<String>,
}

/// Implementation represents component implementation details
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Implementation {
    /// Programming language
    pub language: String,
    /// Source code or reference
    pub source: String,
    /// Dependencies
    pub dependencies: Vec<String>,
    /// Build configuration
    pub build_config: HashMap<String, String>,
}

/// Connection represents a connection between components
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Connection {
    /// Connection name
    pub name: String,
    /// Source component
    pub source: String,
    /// Target component
    pub target: String,
    /// Connection type
    pub connection_type: ConnectionType,
    /// Connection properties
    pub properties: HashMap<String, String>,
}

/// Connection type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConnectionType {
    HTTP,
    gRPC,
    Message,
    Database,
    File,
    Event,
    Custom(String),
}

/// Property represents a property to verify
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Property {
    /// Property name
    pub name: String,
    /// Property description
    pub description: String,
    /// Property type
    pub property_type: PropertyType,
    /// Property expression
    pub expression: String,
    /// Property priority
    pub priority: PropertyPriority,
}

/// Property type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PropertyType {
    Safety,
    Liveness,
    Invariant,
    Temporal,
    Performance,
    Security,
    Custom(String),
}

/// Property priority
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PropertyPriority {
    Critical,
    High,
    Medium,
    Low,
}

/// Verification result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationResult {
    /// Whether verification succeeded
    pub success: bool,
    /// Verification errors
    pub errors: Vec<VerificationError>,
    /// Verification warnings
    pub warnings: Vec<String>,
    /// Verification details
    pub details: HashMap<String, String>,
    /// Verification time
    pub verification_time: std::time::Duration,
}

/// Verification error
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationError {
    /// Error code
    pub code: String,
    /// Error message
    pub message: String,
    /// Error location
    pub location: Option<String>,
    /// Error severity
    pub severity: ErrorSeverity,
}

/// Error severity
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ErrorSeverity {
    Error,
    Warning,
    Info,
}

/// Verification context
#[derive(Debug, Clone)]
pub struct VerificationContext {
    /// Architecture being verified
    pub architecture: Architecture,
    /// Verification configuration
    pub config: Config,
    /// Verification strategy
    pub strategy: String,
    /// Additional context data
    pub context_data: HashMap<String, String>,
}

/// Architecture errors
#[derive(Error, Debug)]
pub enum ArchitectureError {
    #[error("Duplicate component name: {0}")]
    DuplicateComponentName(String),
    #[error("Duplicate connection name: {0}")]
    DuplicateConnectionName(String),
    #[error("Invalid component reference: {0}")]
    InvalidComponentReference(String),
    #[error("Invalid connection reference: {0}")]
    InvalidConnectionReference(String),
    #[error("Validation failed: {0}")]
    ValidationFailed(String),
}

/// Verification strategy trait
pub trait VerificationStrategy: Send + Sync {
    /// Verify an architecture
    fn verify(&self, context: &VerificationContext) -> Result<VerificationResult, Box<dyn std::error::Error>>;
    
    /// Get strategy name
    fn name(&self) -> &str;
    
    /// Get strategy description
    fn description(&self) -> &str;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_architecture_creation() {
        let mut arch = Architecture::new(
            "Test Architecture".to_string(),
            "A test architecture".to_string(),
        );

        let component = Component {
            name: "TestComponent".to_string(),
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };

        arch.add_component(component);
        assert_eq!(arch.components.len(), 1);
        assert_eq!(arch.components[0].name, "TestComponent");
    }

    #[test]
    fn test_architecture_validation() {
        let mut arch = Architecture::new(
            "Test Architecture".to_string(),
            "A test architecture".to_string(),
        );

        let component1 = Component {
            name: "Component1".to_string(),
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };

        let component2 = Component {
            name: "Component2".to_string(),
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };

        arch.add_component(component1);
        arch.add_component(component2);

        let connection = Connection {
            name: "Connection1".to_string(),
            source: "Component1".to_string(),
            target: "Component2".to_string(),
            connection_type: ConnectionType::HTTP,
            properties: HashMap::new(),
        };

        arch.add_connection(connection);

        assert!(arch.validate().is_ok());
    }

    #[test]
    fn test_architecture_validation_duplicate_component() {
        let mut arch = Architecture::new(
            "Test Architecture".to_string(),
            "A test architecture".to_string(),
        );

        let component1 = Component {
            name: "Component1".to_string(),
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };

        let component2 = Component {
            name: "Component1".to_string(), // Duplicate name
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };

        arch.add_component(component1);
        arch.add_component(component2);

        assert!(arch.validate().is_err());
    }
} 