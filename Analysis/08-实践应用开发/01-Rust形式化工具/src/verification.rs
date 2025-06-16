//! Formal verification module for architecture validation

use crate::core::{Architecture, Component, Connection, Property, VerificationContext, VerificationResult, VerificationError, VerificationStrategy, ErrorSeverity};
use std::collections::HashMap;
use std::time::Instant;
use tracing::{info, warn, error};

/// Main verifier for architecture validation
pub struct Verifier {
    /// Registered verification strategies
    strategies: HashMap<String, Box<dyn VerificationStrategy>>,
    /// Verification configuration
    config: crate::core::Config,
}

impl Verifier {
    /// Create a new verifier
    pub fn new() -> Self {
        Self {
            strategies: HashMap::new(),
            config: crate::core::Config::default(),
        }
    }

    /// Add a verification strategy
    pub fn add_strategy(&mut self, strategy: Box<dyn VerificationStrategy>) {
        let name = strategy.name().to_string();
        self.strategies.insert(name, strategy);
    }

    /// Verify an architecture using the specified strategy
    pub fn verify(&self, architecture: &Architecture, strategy_name: &str) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        info!("Starting verification of architecture: {}", architecture.name);
        
        // Validate architecture first
        architecture.validate()?;
        
        // Get the verification strategy
        let strategy = self.strategies.get(strategy_name)
            .ok_or_else(|| format!("Verification strategy '{}' not found", strategy_name))?;
        
        // Create verification context
        let context = VerificationContext {
            architecture: architecture.clone(),
            config: self.config.clone(),
            strategy: strategy_name.to_string(),
            context_data: HashMap::new(),
        };
        
        // Perform verification
        let mut result = strategy.verify(&context)?;
        result.verification_time = start_time.elapsed();
        
        info!("Verification completed in {:?}", result.verification_time);
        
        Ok(result)
    }

    /// Verify an architecture using all available strategies
    pub fn verify_all(&self, architecture: &Architecture) -> Result<HashMap<String, VerificationResult>, Box<dyn std::error::Error>> {
        let mut results = HashMap::new();
        
        for (strategy_name, _) in &self.strategies {
            match self.verify(architecture, strategy_name) {
                Ok(result) => {
                    results.insert(strategy_name.clone(), result);
                }
                Err(e) => {
                    error!("Verification failed for strategy '{}': {}", strategy_name, e);
                    let error_result = VerificationResult {
                        success: false,
                        errors: vec![VerificationError {
                            code: "VERIFICATION_FAILED".to_string(),
                            message: e.to_string(),
                            location: None,
                            severity: ErrorSeverity::Error,
                        }],
                        warnings: Vec::new(),
                        details: HashMap::new(),
                        verification_time: std::time::Duration::ZERO,
                    };
                    results.insert(strategy_name.clone(), error_result);
                }
            }
        }
        
        Ok(results)
    }
}

/// Basic verification strategy
pub struct BasicVerificationStrategy;

impl VerificationStrategy for BasicVerificationStrategy {
    fn verify(&self, context: &VerificationContext) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut details = HashMap::new();
        
        let architecture = &context.architecture;
        
        // Check component consistency
        for component in &architecture.components {
            // Check for empty component names
            if component.name.trim().is_empty() {
                errors.push(VerificationError {
                    code: "EMPTY_COMPONENT_NAME".to_string(),
                    message: "Component name cannot be empty".to_string(),
                    location: Some(format!("Component: {}", component.name)),
                    severity: ErrorSeverity::Error,
                });
            }
            
            // Check for duplicate interface names within component
            let mut interface_names = std::collections::HashSet::new();
            for interface in &component.provided_interfaces {
                if !interface_names.insert(&interface.name) {
                    errors.push(VerificationError {
                        code: "DUPLICATE_INTERFACE_NAME".to_string(),
                        message: format!("Duplicate interface name '{}' in component '{}'", interface.name, component.name),
                        location: Some(format!("Component: {}", component.name)),
                        severity: ErrorSeverity::Error,
                    });
                }
            }
        }
        
        // Check connection consistency
        for connection in &architecture.connections {
            // Check for empty connection names
            if connection.name.trim().is_empty() {
                errors.push(VerificationError {
                    code: "EMPTY_CONNECTION_NAME".to_string(),
                    message: "Connection name cannot be empty".to_string(),
                    location: Some(format!("Connection: {}", connection.name)),
                    severity: ErrorSeverity::Error,
                });
            }
            
            // Check for self-connections
            if connection.source == connection.target {
                warnings.push(format!("Self-connection detected: {}", connection.name));
            }
        }
        
        // Check property consistency
        for property in &architecture.properties {
            // Check for empty property names
            if property.name.trim().is_empty() {
                errors.push(VerificationError {
                    code: "EMPTY_PROPERTY_NAME".to_string(),
                    message: "Property name cannot be empty".to_string(),
                    location: Some(format!("Property: {}", property.name)),
                    severity: ErrorSeverity::Error,
                });
            }
            
            // Check for empty property expressions
            if property.expression.trim().is_empty() {
                errors.push(VerificationError {
                    code: "EMPTY_PROPERTY_EXPRESSION".to_string(),
                    message: format!("Property '{}' has empty expression", property.name),
                    location: Some(format!("Property: {}", property.name)),
                    severity: ErrorSeverity::Error,
                });
            }
        }
        
        // Add verification details
        details.insert("total_components".to_string(), architecture.components.len().to_string());
        details.insert("total_connections".to_string(), architecture.connections.len().to_string());
        details.insert("total_properties".to_string(), architecture.properties.len().to_string());
        
        let success = errors.is_empty();
        
        Ok(VerificationResult {
            success,
            errors,
            warnings,
            details,
            verification_time: std::time::Duration::ZERO, // Will be set by caller
        })
    }
    
    fn name(&self) -> &str {
        "basic"
    }
    
    fn description(&self) -> &str {
        "Basic verification strategy that checks for common architectural issues"
    }
}

/// Type system verification strategy
pub struct TypeSystemVerificationStrategy;

impl VerificationStrategy for TypeSystemVerificationStrategy {
    fn verify(&self, context: &VerificationContext) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut details = HashMap::new();
        
        let architecture = &context.architecture;
        
        // Check interface compatibility
        for connection in &architecture.connections {
            let source_component = architecture.get_component(&connection.source);
            let target_component = architecture.get_component(&connection.target);
            
            if let (Some(source), Some(target)) = (source_component, target_component) {
                // Check if source component provides an interface that target requires
                let mut interface_found = false;
                
                for provided_interface in &source.provided_interfaces {
                    for required_interface in &target.required_interfaces {
                        if provided_interface.name == required_interface.name {
                            interface_found = true;
                            
                            // Check interface type compatibility
                            if provided_interface.interface_type != required_interface.interface_type {
                                warnings.push(format!(
                                    "Interface type mismatch for '{}': provided={:?}, required={:?}",
                                    provided_interface.name,
                                    provided_interface.interface_type,
                                    required_interface.interface_type
                                ));
                            }
                            
                            // Check method compatibility
                            for provided_method in &provided_interface.methods {
                                if let Some(required_method) = required_interface.methods.iter()
                                    .find(|m| m.name == provided_method.name) {
                                    
                                    // Check parameter compatibility
                                    if provided_method.parameters.len() != required_method.parameters.len() {
                                        errors.push(VerificationError {
                                            code: "METHOD_PARAMETER_MISMATCH".to_string(),
                                            message: format!(
                                                "Method '{}' parameter count mismatch: provided={}, required={}",
                                                provided_method.name,
                                                provided_method.parameters.len(),
                                                required_method.parameters.len()
                                            ),
                                            location: Some(format!("Interface: {}", provided_interface.name)),
                                            severity: ErrorSeverity::Error,
                                        });
                                    }
                                    
                                    // Check return type compatibility
                                    if provided_method.return_type != required_method.return_type {
                                        warnings.push(format!(
                                            "Method '{}' return type mismatch: provided={:?}, required={:?}",
                                            provided_method.name,
                                            provided_method.return_type,
                                            required_method.return_type
                                        ));
                                    }
                                }
                            }
                        }
                    }
                }
                
                if !interface_found {
                    errors.push(VerificationError {
                        code: "INTERFACE_NOT_FOUND".to_string(),
                        message: format!(
                            "No compatible interface found for connection '{}' from '{}' to '{}'",
                            connection.name, connection.source, connection.target
                        ),
                        location: Some(format!("Connection: {}", connection.name)),
                        severity: ErrorSeverity::Error,
                    });
                }
            }
        }
        
        // Add verification details
        details.insert("interface_checks".to_string(), "completed".to_string());
        details.insert("type_compatibility_checks".to_string(), "completed".to_string());
        
        let success = errors.is_empty();
        
        Ok(VerificationResult {
            success,
            errors,
            warnings,
            details,
            verification_time: std::time::Duration::ZERO, // Will be set by caller
        })
    }
    
    fn name(&self) -> &str {
        "type_system"
    }
    
    fn description(&self) -> &str {
        "Type system verification strategy that checks interface compatibility and type safety"
    }
}

/// Performance verification strategy
pub struct PerformanceVerificationStrategy;

impl VerificationStrategy for PerformanceVerificationStrategy {
    fn verify(&self, context: &VerificationContext) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut details = HashMap::new();
        
        let architecture = &context.architecture;
        
        // Check for potential performance issues
        let component_count = architecture.components.len();
        let connection_count = architecture.connections.len();
        
        // Check for high coupling
        let avg_connections_per_component = if component_count > 0 {
            connection_count as f64 / component_count as f64
        } else {
            0.0
        };
        
        if avg_connections_per_component > 5.0 {
            warnings.push(format!(
                "High coupling detected: average {:.2} connections per component",
                avg_connections_per_component
            ));
        }
        
        // Check for potential bottlenecks
        let mut component_connection_counts = HashMap::new();
        for connection in &architecture.connections {
            *component_connection_counts.entry(&connection.source).or_insert(0) += 1;
            *component_connection_counts.entry(&connection.target).or_insert(0) += 1;
        }
        
        for (component_name, count) in component_connection_counts {
            if count > 10 {
                warnings.push(format!(
                    "Potential bottleneck detected: component '{}' has {} connections",
                    component_name, count
                ));
            }
        }
        
        // Check for circular dependencies
        if let Err(cycle_error) = detect_circular_dependencies(architecture) {
            errors.push(VerificationError {
                code: "CIRCULAR_DEPENDENCY".to_string(),
                message: cycle_error,
                location: None,
                severity: ErrorSeverity::Error,
            });
        }
        
        // Add verification details
        details.insert("component_count".to_string(), component_count.to_string());
        details.insert("connection_count".to_string(), connection_count.to_string());
        details.insert("avg_connections_per_component".to_string(), avg_connections_per_component.to_string());
        
        let success = errors.is_empty();
        
        Ok(VerificationResult {
            success,
            errors,
            warnings,
            details,
            verification_time: std::time::Duration::ZERO, // Will be set by caller
        })
    }
    
    fn name(&self) -> &str {
        "performance"
    }
    
    fn description(&self) -> &str {
        "Performance verification strategy that checks for performance-related architectural issues"
    }
}

/// Detect circular dependencies in the architecture
fn detect_circular_dependencies(architecture: &Architecture) -> Result<(), String> {
    use std::collections::{HashMap, HashSet};
    
    // Build adjacency list
    let mut graph: HashMap<String, Vec<String>> = HashMap::new();
    for connection in &architecture.connections {
        graph.entry(connection.source.clone())
            .or_insert_with(Vec::new)
            .push(connection.target.clone());
    }
    
    // DFS to detect cycles
    let mut visited = HashSet::new();
    let mut rec_stack = HashSet::new();
    
    fn has_cycle(
        node: &str,
        graph: &HashMap<String, Vec<String>>,
        visited: &mut HashSet<String>,
        rec_stack: &mut HashSet<String>,
    ) -> bool {
        if rec_stack.contains(node) {
            return true;
        }
        
        if visited.contains(node) {
            return false;
        }
        
        visited.insert(node.to_string());
        rec_stack.insert(node.to_string());
        
        if let Some(neighbors) = graph.get(node) {
            for neighbor in neighbors {
                if has_cycle(neighbor, graph, visited, rec_stack) {
                    return true;
                }
            }
        }
        
        rec_stack.remove(node);
        false
    }
    
    for node in graph.keys() {
        if !visited.contains(node) {
            if has_cycle(node, &graph, &mut visited, &mut rec_stack) {
                return Err(format!("Circular dependency detected involving component '{}'", node));
            }
        }
    }
    
    Ok(())
}

/// Verification report generator
pub struct VerificationReport {
    /// Architecture name
    pub architecture_name: String,
    /// Verification results
    pub results: HashMap<String, VerificationResult>,
    /// Summary statistics
    pub summary: ReportSummary,
}

/// Report summary
#[derive(Debug, Clone)]
pub struct ReportSummary {
    /// Total number of strategies used
    pub total_strategies: usize,
    /// Number of successful verifications
    pub successful_verifications: usize,
    /// Number of failed verifications
    pub failed_verifications: usize,
    /// Total number of errors
    pub total_errors: usize,
    /// Total number of warnings
    pub total_warnings: usize,
    /// Average verification time
    pub avg_verification_time: std::time::Duration,
}

impl VerificationReport {
    /// Create a new verification report
    pub fn new(architecture_name: String, results: HashMap<String, VerificationResult>) -> Self {
        let total_strategies = results.len();
        let successful_verifications = results.values().filter(|r| r.success).count();
        let failed_verifications = total_strategies - successful_verifications;
        
        let total_errors: usize = results.values().map(|r| r.errors.len()).sum();
        let total_warnings: usize = results.values().map(|r| r.warnings.len()).sum();
        
        let total_time: std::time::Duration = results.values()
            .map(|r| r.verification_time)
            .sum();
        let avg_verification_time = if total_strategies > 0 {
            total_time / total_strategies as u32
        } else {
            std::time::Duration::ZERO
        };
        
        let summary = ReportSummary {
            total_strategies,
            successful_verifications,
            failed_verifications,
            total_errors,
            total_warnings,
            avg_verification_time,
        };
        
        Self {
            architecture_name,
            results,
            summary,
        }
    }
    
    /// Generate a markdown report
    pub fn to_markdown(&self) -> String {
        let mut markdown = String::new();
        
        markdown.push_str(&format!("# Verification Report: {}\n\n", self.architecture_name));
        
        // Summary
        markdown.push_str("## Summary\n\n");
        markdown.push_str(&format!("- **Total Strategies**: {}\n", self.summary.total_strategies));
        markdown.push_str(&format!("- **Successful Verifications**: {}\n", self.summary.successful_verifications));
        markdown.push_str(&format!("- **Failed Verifications**: {}\n", self.summary.failed_verifications));
        markdown.push_str(&format!("- **Total Errors**: {}\n", self.summary.total_errors));
        markdown.push_str(&format!("- **Total Warnings**: {}\n", self.summary.total_warnings));
        markdown.push_str(&format!("- **Average Verification Time**: {:?}\n\n", self.summary.avg_verification_time));
        
        // Detailed results
        markdown.push_str("## Detailed Results\n\n");
        
        for (strategy_name, result) in &self.results {
            markdown.push_str(&format!("### {}\n\n", strategy_name));
            markdown.push_str(&format!("**Status**: {}\n\n", if result.success { "✅ PASSED" } else { "❌ FAILED" }));
            
            if !result.errors.is_empty() {
                markdown.push_str("**Errors**:\n");
                for error in &result.errors {
                    markdown.push_str(&format!("- {}: {}\n", error.code, error.message));
                }
                markdown.push_str("\n");
            }
            
            if !result.warnings.is_empty() {
                markdown.push_str("**Warnings**:\n");
                for warning in &result.warnings {
                    markdown.push_str(&format!("- {}\n", warning));
                }
                markdown.push_str("\n");
            }
            
            if !result.details.is_empty() {
                markdown.push_str("**Details**:\n");
                for (key, value) in &result.details {
                    markdown.push_str(&format!("- {}: {}\n", key, value));
                }
                markdown.push_str("\n");
            }
        }
        
        markdown
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::{ComponentType, InterfaceType, PropertyType, PropertyPriority};

    #[test]
    fn test_basic_verification_strategy() {
        let strategy = BasicVerificationStrategy;
        let mut architecture = Architecture::new(
            "Test Architecture".to_string(),
            "A test architecture".to_string(),
        );
        
        // Add a valid component
        let component = Component {
            name: "TestComponent".to_string(),
            component_type: ComponentType::Service,
            provided_interfaces: Vec::new(),
            required_interfaces: Vec::new(),
            properties: HashMap::new(),
            implementation: None,
        };
        architecture.add_component(component);
        
        let context = VerificationContext {
            architecture: architecture.clone(),
            config: crate::core::Config::default(),
            strategy: "basic".to_string(),
            context_data: HashMap::new(),
        };
        
        let result = strategy.verify(&context).unwrap();
        assert!(result.success);
    }

    #[test]
    fn test_verifier() {
        let mut verifier = Verifier::new();
        verifier.add_strategy(Box::new(BasicVerificationStrategy));
        
        let mut architecture = Architecture::new(
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
        architecture.add_component(component);
        
        let result = verifier.verify(&architecture, "basic").unwrap();
        assert!(result.success);
    }
} 