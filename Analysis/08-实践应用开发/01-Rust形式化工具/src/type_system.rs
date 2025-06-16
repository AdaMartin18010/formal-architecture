//! Type system module for formal architecture verification

use crate::core::{Architecture, Component, Interface, Method, Parameter, VerificationResult, VerificationError, ErrorSeverity};
use std::collections::{HashMap, HashSet};
use tracing::{info, warn, error};

/// Type system for architecture verification
pub struct TypeSystem {
    /// Type definitions
    type_definitions: HashMap<String, TypeDefinition>,
    /// Type constraints
    type_constraints: Vec<TypeConstraint>,
    /// Type inference rules
    inference_rules: Vec<InferenceRule>,
}

/// Type definition
#[derive(Debug, Clone)]
pub struct TypeDefinition {
    /// Type name
    pub name: String,
    /// Type kind
    pub kind: TypeKind,
    /// Type parameters
    pub parameters: Vec<String>,
    /// Type constraints
    pub constraints: Vec<TypeConstraint>,
    /// Type constructors
    pub constructors: Vec<TypeConstructor>,
}

/// Type kind
#[derive(Debug, Clone)]
pub enum TypeKind {
    Primitive,
    Composite,
    Function,
    Interface,
    Generic,
}

/// Type constructor
#[derive(Debug, Clone)]
pub struct TypeConstructor {
    /// Constructor name
    pub name: String,
    /// Constructor parameters
    pub parameters: Vec<Type>,
    /// Return type
    pub return_type: Type,
}

/// Type representation
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Type {
    /// Primitive types
    Bool,
    Int,
    Float,
    String,
    Unit,
    
    /// Composite types
    Tuple(Vec<Type>),
    Record(HashMap<String, Type>),
    Variant(Vec<VariantCase>),
    
    /// Function types
    Function(Vec<Type>, Box<Type>),
    
    /// Generic types
    Generic(String, Vec<Type>),
    
    /// Interface types
    Interface(String),
    
    /// Type variables
    Variable(String),
    
    /// Unknown type
    Unknown,
}

/// Variant case
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct VariantCase {
    /// Case name
    pub name: String,
    /// Case data type
    pub data_type: Option<Type>,
}

/// Type constraint
#[derive(Debug, Clone)]
pub struct TypeConstraint {
    /// Constraint identifier
    pub id: String,
    /// Constraint expression
    pub expression: ConstraintExpression,
    /// Constraint context
    pub context: HashMap<String, Type>,
}

/// Constraint expression
#[derive(Debug, Clone)]
pub enum ConstraintExpression {
    /// Equality constraint
    Equal(Type, Type),
    /// Subtype constraint
    Subtype(Type, Type),
    /// Instance constraint
    Instance(Type, Type),
    /// And constraint
    And(Box<ConstraintExpression>, Box<ConstraintExpression>),
    /// Or constraint
    Or(Box<ConstraintExpression>, Box<ConstraintExpression>),
    /// Not constraint
    Not(Box<ConstraintExpression>),
}

/// Inference rule
#[derive(Debug, Clone)]
pub struct InferenceRule {
    /// Rule name
    pub name: String,
    /// Rule premises
    pub premises: Vec<TypeJudgment>,
    /// Rule conclusion
    pub conclusion: TypeJudgment,
    /// Rule conditions
    pub conditions: Vec<TypeConstraint>,
}

/// Type judgment
#[derive(Debug, Clone)]
pub struct TypeJudgment {
    /// Judgment context
    pub context: HashMap<String, Type>,
    /// Judgment expression
    pub expression: String,
    /// Judgment type
    pub type_: Type,
}

/// Type checker for architecture verification
pub struct TypeChecker {
    /// Type system
    type_system: TypeSystem,
    /// Type environment
    environment: TypeEnvironment,
    /// Type errors
    errors: Vec<TypeError>,
    /// Type warnings
    warnings: Vec<String>,
}

/// Type environment
#[derive(Debug, Clone)]
pub struct TypeEnvironment {
    /// Variable types
    variables: HashMap<String, Type>,
    /// Function types
    functions: HashMap<String, Type>,
    /// Interface types
    interfaces: HashMap<String, Type>,
    /// Component types
    components: HashMap<String, ComponentType>,
}

/// Component type
#[derive(Debug, Clone)]
pub struct ComponentType {
    /// Component name
    pub name: String,
    /// Provided interfaces
    pub provided_interfaces: HashMap<String, Type>,
    /// Required interfaces
    pub required_interfaces: HashMap<String, Type>,
    /// Internal types
    pub internal_types: HashMap<String, Type>,
}

/// Type error
#[derive(Debug, Clone)]
pub struct TypeError {
    /// Error code
    pub code: String,
    /// Error message
    pub message: String,
    /// Error location
    pub location: Option<String>,
    /// Error severity
    pub severity: ErrorSeverity,
    /// Error context
    pub context: HashMap<String, String>,
}

impl TypeSystem {
    /// Create a new type system
    pub fn new() -> Self {
        let mut type_system = Self {
            type_definitions: HashMap::new(),
            type_constraints: Vec::new(),
            inference_rules: Vec::new(),
        };
        
        // Add primitive types
        type_system.add_primitive_types();
        
        // Add basic inference rules
        type_system.add_basic_rules();
        
        type_system
    }

    /// Add primitive types
    fn add_primitive_types(&mut self) {
        let primitive_types = vec![
            ("bool", Type::Bool),
            ("int", Type::Int),
            ("float", Type::Float),
            ("string", Type::String),
            ("unit", Type::Unit),
        ];

        for (name, type_) in primitive_types {
            self.type_definitions.insert(name.to_string(), TypeDefinition {
                name: name.to_string(),
                kind: TypeKind::Primitive,
                parameters: Vec::new(),
                constraints: Vec::new(),
                constructors: Vec::new(),
            });
        }
    }

    /// Add basic inference rules
    fn add_basic_rules(&mut self) {
        // Variable rule
        self.inference_rules.push(InferenceRule {
            name: "Var".to_string(),
            premises: Vec::new(),
            conclusion: TypeJudgment {
                context: HashMap::new(),
                expression: "x".to_string(),
                type_: Type::Variable("T".to_string()),
            },
            conditions: vec![TypeConstraint {
                id: "var_in_context".to_string(),
                expression: ConstraintExpression::Equal(
                    Type::Variable("x".to_string()),
                    Type::Variable("T".to_string())
                ),
                context: HashMap::new(),
            }],
        });

        // Function application rule
        self.inference_rules.push(InferenceRule {
            name: "App".to_string(),
            premises: vec![
                TypeJudgment {
                    context: HashMap::new(),
                    expression: "f".to_string(),
                    type_: Type::Function(vec![Type::Variable("T1".to_string())], Box::new(Type::Variable("T2".to_string()))),
                },
                TypeJudgment {
                    context: HashMap::new(),
                    expression: "x".to_string(),
                    type_: Type::Variable("T1".to_string()),
                },
            ],
            conclusion: TypeJudgment {
                context: HashMap::new(),
                expression: "f x".to_string(),
                type_: Type::Variable("T2".to_string()),
            },
            conditions: Vec::new(),
        });
    }

    /// Add type definition
    pub fn add_type_definition(&mut self, definition: TypeDefinition) {
        self.type_definitions.insert(definition.name.clone(), definition);
    }

    /// Add type constraint
    pub fn add_constraint(&mut self, constraint: TypeConstraint) {
        self.type_constraints.push(constraint);
    }

    /// Add inference rule
    pub fn add_rule(&mut self, rule: InferenceRule) {
        self.inference_rules.push(rule);
    }

    /// Check if type is well-formed
    pub fn is_well_formed(&self, type_: &Type) -> bool {
        match type_ {
            Type::Bool | Type::Int | Type::Float | Type::String | Type::Unit => true,
            Type::Tuple(types) => types.iter().all(|t| self.is_well_formed(t)),
            Type::Record(fields) => fields.values().all(|t| self.is_well_formed(t)),
            Type::Variant(cases) => cases.iter().all(|case| {
                case.data_type.as_ref().map_or(true, |t| self.is_well_formed(t))
            }),
            Type::Function(params, return_type) => {
                params.iter().all(|t| self.is_well_formed(t)) && self.is_well_formed(return_type)
            }
            Type::Generic(_, args) => args.iter().all(|t| self.is_well_formed(t)),
            Type::Interface(_) => true,
            Type::Variable(_) => true,
            Type::Unknown => false,
        }
    }

    /// Check type equality
    pub fn types_equal(&self, type1: &Type, type2: &Type) -> bool {
        match (type1, type2) {
            (Type::Bool, Type::Bool) |
            (Type::Int, Type::Int) |
            (Type::Float, Type::Float) |
            (Type::String, Type::String) |
            (Type::Unit, Type::Unit) => true,
            
            (Type::Tuple(types1), Type::Tuple(types2)) => {
                types1.len() == types2.len() && 
                types1.iter().zip(types2.iter()).all(|(t1, t2)| self.types_equal(t1, t2))
            }
            
            (Type::Record(fields1), Type::Record(fields2)) => {
                fields1.len() == fields2.len() && 
                fields1.iter().all(|(k, v)| {
                    fields2.get(k).map_or(false, |v2| self.types_equal(v, v2))
                })
            }
            
            (Type::Function(params1, return1), Type::Function(params2, return2)) => {
                params1.len() == params2.len() && 
                params1.iter().zip(params2.iter()).all(|(p1, p2)| self.types_equal(p1, p2)) &&
                self.types_equal(return1, return2)
            }
            
            (Type::Generic(name1, args1), Type::Generic(name2, args2)) => {
                name1 == name2 && 
                args1.len() == args2.len() && 
                args1.iter().zip(args2.iter()).all(|(a1, a2)| self.types_equal(a1, a2))
            }
            
            (Type::Interface(name1), Type::Interface(name2)) => name1 == name2,
            (Type::Variable(name1), Type::Variable(name2)) => name1 == name2,
            
            _ => false,
        }
    }

    /// Check subtype relationship
    pub fn is_subtype(&self, subtype: &Type, supertype: &Type) -> bool {
        // Reflexivity
        if self.types_equal(subtype, supertype) {
            return true;
        }

        match (subtype, supertype) {
            // Primitive type subtyping
            (Type::Int, Type::Float) => true,
            
            // Tuple subtyping (covariant)
            (Type::Tuple(types1), Type::Tuple(types2)) => {
                types1.len() == types2.len() && 
                types1.iter().zip(types2.iter()).all(|(t1, t2)| self.is_subtype(t1, t2))
            }
            
            // Record subtyping (width and depth)
            (Type::Record(fields1), Type::Record(fields2)) => {
                fields2.iter().all(|(k, v)| {
                    fields1.get(k).map_or(false, |v1| self.is_subtype(v1, v))
                })
            }
            
            // Function subtyping (contravariant in parameters, covariant in return)
            (Type::Function(params1, return1), Type::Function(params2, return2)) => {
                params1.len() == params2.len() && 
                params1.iter().zip(params2.iter()).all(|(p1, p2)| self.is_subtype(p2, p1)) &&
                self.is_subtype(return1, return2)
            }
            
            // Interface subtyping
            (Type::Interface(name1), Type::Interface(name2)) => {
                // In a real implementation, this would check interface inheritance
                name1 == name2
            }
            
            _ => false,
        }
    }
}

impl TypeChecker {
    /// Create a new type checker
    pub fn new(type_system: TypeSystem) -> Self {
        Self {
            type_system,
            environment: TypeEnvironment {
                variables: HashMap::new(),
                functions: HashMap::new(),
                interfaces: HashMap::new(),
                components: HashMap::new(),
            },
            errors: Vec::new(),
            warnings: Vec::new(),
        }
    }

    /// Check architecture type safety
    pub fn check_architecture(&mut self, architecture: &Architecture) -> Result<VerificationResult, Box<dyn std::error::Error>> {
        info!("Starting type checking for architecture: {}", architecture.name);
        
        let start_time = std::time::Instant::now();
        
        // Reset errors and warnings
        self.errors.clear();
        self.warnings.clear();
        
        // Check component types
        for component in &architecture.components {
            self.check_component_types(component)?;
        }
        
        // Check interface compatibility
        for connection in &architecture.connections {
            self.check_interface_compatibility(connection, architecture)?;
        }
        
        // Check method signatures
        for component in &architecture.components {
            self.check_method_signatures(component)?;
        }
        
        // Check type constraints
        self.check_type_constraints()?;
        
        let verification_time = start_time.elapsed();
        
        // Convert type errors to verification errors
        let verification_errors: Vec<VerificationError> = self.errors.iter().map(|e| VerificationError {
            code: e.code.clone(),
            message: e.message.clone(),
            location: e.location.clone(),
            severity: e.severity.clone(),
        }).collect();
        
        let mut details = HashMap::new();
        details.insert("total_components_checked".to_string(), architecture.components.len().to_string());
        details.insert("total_interfaces_checked".to_string(), architecture.components.iter()
            .map(|c| c.provided_interfaces.len() + c.required_interfaces.len()).sum::<usize>().to_string());
        details.insert("type_errors".to_string(), self.errors.len().to_string());
        details.insert("type_warnings".to_string(), self.warnings.len().to_string());
        
        Ok(VerificationResult {
            success: self.errors.is_empty(),
            errors: verification_errors,
            warnings: self.warnings.clone(),
            details,
            verification_time,
        })
    }

    /// Check component types
    fn check_component_types(&mut self, component: &Component) -> Result<(), Box<dyn std::error::Error>> {
        // Check provided interfaces
        for interface in &component.provided_interfaces {
            self.check_interface_types(interface, &format!("component '{}'", component.name))?;
        }
        
        // Check required interfaces
        for interface in &component.required_interfaces {
            self.check_interface_types(interface, &format!("component '{}'", component.name))?;
        }
        
        // Create component type
        let mut provided_interfaces = HashMap::new();
        for interface in &component.provided_interfaces {
            provided_interfaces.insert(interface.name.clone(), Type::Interface(interface.name.clone()));
        }
        
        let mut required_interfaces = HashMap::new();
        for interface in &component.required_interfaces {
            required_interfaces.insert(interface.name.clone(), Type::Interface(interface.name.clone()));
        }
        
        let component_type = ComponentType {
            name: component.name.clone(),
            provided_interfaces,
            required_interfaces,
            internal_types: HashMap::new(),
        };
        
        self.environment.components.insert(component.name.clone(), component_type);
        
        Ok(())
    }

    /// Check interface types
    fn check_interface_types(&mut self, interface: &Interface, context: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Check method types
        for method in &interface.methods {
            self.check_method_types(method, &format!("{} interface '{}'", context, interface.name))?;
        }
        
        // Register interface type
        let interface_type = Type::Interface(interface.name.clone());
        self.environment.interfaces.insert(interface.name.clone(), interface_type);
        
        Ok(())
    }

    /// Check method types
    fn check_method_types(&mut self, method: &Method, context: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Check parameter types
        for parameter in &method.parameters {
            if !self.type_system.is_well_formed(&self.parse_type(&parameter.parameter_type)) {
                self.errors.push(TypeError {
                    code: "INVALID_PARAMETER_TYPE".to_string(),
                    message: format!("Invalid parameter type '{}' in {}", parameter.parameter_type, context),
                    location: Some(format!("Method: {}", method.name)),
                    severity: ErrorSeverity::Error,
                    context: HashMap::new(),
                });
            }
        }
        
        // Check return type
        if let Some(return_type_str) = &method.return_type {
            if !self.type_system.is_well_formed(&self.parse_type(return_type_str)) {
                self.errors.push(TypeError {
                    code: "INVALID_RETURN_TYPE".to_string(),
                    message: format!("Invalid return type '{}' in {}", return_type_str, context),
                    location: Some(format!("Method: {}", method.name)),
                    severity: ErrorSeverity::Error,
                    context: HashMap::new(),
                });
            }
        }
        
        Ok(())
    }

    /// Check interface compatibility
    fn check_interface_compatibility(
        &self,
        connection: &crate::core::Connection,
        architecture: &Architecture,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let source_component = architecture.get_component(&connection.source);
        let target_component = architecture.get_component(&connection.target);
        
        if let (Some(source), Some(target)) = (source_component, target_component) {
            // Check if source provides an interface that target requires
            let mut interface_found = false;
            
            for provided_interface in &source.provided_interfaces {
                for required_interface in &target.required_interfaces {
                    if provided_interface.name == required_interface.name {
                        interface_found = true;
                        
                        // Check interface compatibility
                        if !self.interfaces_compatible(provided_interface, required_interface) {
                            self.errors.push(TypeError {
                                code: "INTERFACE_INCOMPATIBLE".to_string(),
                                message: format!(
                                    "Interface '{}' provided by '{}' is incompatible with required interface in '{}'",
                                    provided_interface.name, connection.source, connection.target
                                ),
                                location: Some(format!("Connection: {}", connection.name)),
                                severity: ErrorSeverity::Error,
                                context: HashMap::new(),
                            });
                        }
                    }
                }
            }
            
            if !interface_found {
                self.errors.push(TypeError {
                    code: "INTERFACE_NOT_FOUND".to_string(),
                    message: format!(
                        "No compatible interface found for connection '{}' from '{}' to '{}'",
                        connection.name, connection.source, connection.target
                    ),
                    location: Some(format!("Connection: {}", connection.name)),
                    severity: ErrorSeverity::Error,
                    context: HashMap::new(),
                });
            }
        }
        
        Ok(())
    }

    /// Check if two interfaces are compatible
    fn interfaces_compatible(&self, provided: &Interface, required: &Interface) -> bool {
        // Check if all required methods are provided
        for required_method in &required.methods {
            if let Some(provided_method) = provided.methods.iter().find(|m| m.name == required_method.name) {
                // Check parameter compatibility
                if provided_method.parameters.len() != required_method.parameters.len() {
                    return false;
                }
                
                for (provided_param, required_param) in provided_method.parameters.iter().zip(required_method.parameters.iter()) {
                    let provided_type = self.parse_type(&provided_param.parameter_type);
                    let required_type = self.parse_type(&required_param.parameter_type);
                    
                    if !self.type_system.is_subtype(&provided_type, &required_type) {
                        return false;
                    }
                }
                
                // Check return type compatibility
                if let (Some(provided_return), Some(required_return)) = (&provided_method.return_type, &required_method.return_type) {
                    let provided_type = self.parse_type(provided_return);
                    let required_type = self.parse_type(required_return);
                    
                    if !self.type_system.is_subtype(&provided_type, &required_type) {
                        return false;
                    }
                }
            } else {
                return false;
            }
        }
        
        true
    }

    /// Check method signatures
    fn check_method_signatures(&mut self, component: &Component) -> Result<(), Box<dyn std::error::Error>> {
        for interface in &component.provided_interfaces {
            for method in &interface.methods {
                // Check for duplicate method names
                let method_count = interface.methods.iter()
                    .filter(|m| m.name == method.name)
                    .count();
                
                if method_count > 1 {
                    self.errors.push(TypeError {
                        code: "DUPLICATE_METHOD".to_string(),
                        message: format!("Duplicate method '{}' in interface '{}'", method.name, interface.name),
                        location: Some(format!("Component: {}", component.name)),
                        severity: ErrorSeverity::Error,
                        context: HashMap::new(),
                    });
                }
                
                // Check parameter names
                let mut param_names = HashSet::new();
                for parameter in &method.parameters {
                    if !param_names.insert(&parameter.name) {
                        self.errors.push(TypeError {
                            code: "DUPLICATE_PARAMETER".to_string(),
                            message: format!("Duplicate parameter '{}' in method '{}'", parameter.name, method.name),
                            location: Some(format!("Component: {}", component.name)),
                            severity: ErrorSeverity::Error,
                            context: HashMap::new(),
                        });
                    }
                }
            }
        }
        
        Ok(())
    }

    /// Check type constraints
    fn check_type_constraints(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        for constraint in &self.type_system.type_constraints {
            if !self.satisfies_constraint(constraint) {
                self.errors.push(TypeError {
                    code: "CONSTRAINT_VIOLATION".to_string(),
                    message: format!("Type constraint '{}' violated", constraint.id),
                    location: None,
                    severity: ErrorSeverity::Error,
                    context: HashMap::new(),
                });
            }
        }
        
        Ok(())
    }

    /// Check if constraint is satisfied
    fn satisfies_constraint(&self, constraint: &TypeConstraint) -> bool {
        match &constraint.expression {
            ConstraintExpression::Equal(type1, type2) => {
                self.type_system.types_equal(type1, type2)
            }
            ConstraintExpression::Subtype(subtype, supertype) => {
                self.type_system.is_subtype(subtype, supertype)
            }
            ConstraintExpression::Instance(instance, type_) => {
                self.type_system.is_subtype(instance, type_)
            }
            ConstraintExpression::And(expr1, expr2) => {
                self.satisfies_constraint_expression(expr1) && self.satisfies_constraint_expression(expr2)
            }
            ConstraintExpression::Or(expr1, expr2) => {
                self.satisfies_constraint_expression(expr1) || self.satisfies_constraint_expression(expr2)
            }
            ConstraintExpression::Not(expr) => {
                !self.satisfies_constraint_expression(expr)
            }
        }
    }

    /// Check if constraint expression is satisfied
    fn satisfies_constraint_expression(&self, expr: &ConstraintExpression) -> bool {
        match expr {
            ConstraintExpression::Equal(type1, type2) => {
                self.type_system.types_equal(type1, type2)
            }
            ConstraintExpression::Subtype(subtype, supertype) => {
                self.type_system.is_subtype(subtype, supertype)
            }
            ConstraintExpression::Instance(instance, type_) => {
                self.type_system.is_subtype(instance, type_)
            }
            ConstraintExpression::And(expr1, expr2) => {
                self.satisfies_constraint_expression(expr1) && self.satisfies_constraint_expression(expr2)
            }
            ConstraintExpression::Or(expr1, expr2) => {
                self.satisfies_constraint_expression(expr1) || self.satisfies_constraint_expression(expr2)
            }
            ConstraintExpression::Not(expr) => {
                !self.satisfies_constraint_expression(expr)
            }
        }
    }

    /// Parse type from string
    fn parse_type(&self, type_str: &str) -> Type {
        match type_str.trim() {
            "bool" => Type::Bool,
            "int" => Type::Int,
            "float" => Type::Float,
            "string" => Type::String,
            "unit" => Type::Unit,
            _ => {
                // Try to parse as interface type
                if type_str.starts_with("interface:") {
                    let interface_name = type_str.trim_start_matches("interface:").trim();
                    Type::Interface(interface_name.to_string())
                } else {
                    Type::Unknown
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::{ComponentType, InterfaceType};

    #[test]
    fn test_type_system_creation() {
        let type_system = TypeSystem::new();
        assert!(!type_system.type_definitions.is_empty());
        assert!(!type_system.inference_rules.is_empty());
    }

    #[test]
    fn test_type_equality() {
        let type_system = TypeSystem::new();
        
        assert!(type_system.types_equal(&Type::Bool, &Type::Bool));
        assert!(type_system.types_equal(&Type::Int, &Type::Int));
        assert!(!type_system.types_equal(&Type::Bool, &Type::Int));
        
        let tuple1 = Type::Tuple(vec![Type::Int, Type::String]);
        let tuple2 = Type::Tuple(vec![Type::Int, Type::String]);
        let tuple3 = Type::Tuple(vec![Type::Int, Type::Bool]);
        
        assert!(type_system.types_equal(&tuple1, &tuple2));
        assert!(!type_system.types_equal(&tuple1, &tuple3));
    }

    #[test]
    fn test_subtyping() {
        let type_system = TypeSystem::new();
        
        assert!(type_system.is_subtype(&Type::Int, &Type::Float));
        assert!(!type_system.is_subtype(&Type::Float, &Type::Int));
        assert!(type_system.is_subtype(&Type::Int, &Type::Int));
    }

    #[test]
    fn test_type_checker() {
        let type_system = TypeSystem::new();
        let mut checker = TypeChecker::new(type_system);
        
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
        
        let result = checker.check_architecture(&architecture).unwrap();
        assert!(result.success);
    }
} 