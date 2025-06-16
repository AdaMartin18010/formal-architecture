//! Formal Architecture Tools
//! 
//! This library provides formal verification and analysis tools for software architecture.
//! It implements various formal methods including theorem proving, model checking,
//! and type system verification.

pub mod core;
pub mod verification;
pub mod model_checking;
pub mod type_system;
pub mod architecture;
pub mod petri_net;
pub mod temporal_logic;
pub mod theorem_proving;
pub mod constraint_solving;
pub mod utils;

pub use core::*;
pub use verification::*;
pub use model_checking::*;
pub use type_system::*;
pub use architecture::*;
pub use petri_net::*;
pub use temporal_logic::*;
pub use theorem_proving::*;
pub use constraint_solving::*;
pub use utils::*;

/// Re-export commonly used types and traits
pub mod prelude {
    pub use crate::core::{
        Architecture, Component, Interface, Connection, Property, VerificationResult,
        VerificationError, VerificationContext
    };
    
    pub use crate::verification::{
        Verifier, VerificationStrategy, VerificationReport
    };
    
    pub use crate::model_checking::{
        ModelChecker, ModelCheckingResult, StateSpace, TransitionSystem
    };
    
    pub use crate::type_system::{
        TypeSystem, Type, TypeChecker, TypeError
    };
    
    pub use crate::petri_net::{
        PetriNet, Place, Transition, Marking, PetriNetAnalyzer
    };
    
    pub use crate::temporal_logic::{
        TemporalLogic, LTLFormula, CTLFormula, ModelChecker
    };
    
    pub use crate::theorem_proving::{
        TheoremProver, Proof, ProofStep, Axiom, Rule
    };
    
    pub use crate::constraint_solving::{
        ConstraintSolver, Constraint, Solution, SolverError
    };
}

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Library authors
pub const AUTHORS: &str = env!("CARGO_PKG_AUTHORS");

/// Library description
pub const DESCRIPTION: &str = env!("CARGO_PKG_DESCRIPTION");

/// Initialize the library
pub fn init() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    
    // Initialize global state
    crate::core::init_global_state()?;
    
    tracing::info!("Formal Architecture Tools initialized successfully");
    Ok(())
}

/// Cleanup library resources
pub fn cleanup() {
    tracing::info!("Cleaning up Formal Architecture Tools");
    crate::core::cleanup_global_state();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_library_initialization() {
        assert!(init().is_ok());
        cleanup();
    }

    #[test]
    fn test_version_info() {
        assert!(!VERSION.is_empty());
        assert!(!AUTHORS.is_empty());
        assert!(!DESCRIPTION.is_empty());
    }
} 