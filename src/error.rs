use pyo3::prelude::*;

// Create exceptions with class instead of create_exception! macro
// https://github.com/PyO3/pyo3/issues/295#issuecomment-852358088
#[pyclass(extends=pyo3::exceptions::PyException)]
pub struct EggSmolError {
    #[pyo3(get)]
    context: String,
}

#[pymethods]
impl EggSmolError {
    #[new]
    fn new(context: String) -> Self {
        EggSmolError { context }
    }
}

// Wrap the egg_smol::Error so we can automatically convert from it to the PyErr
// and so return it from each function automatically
// https://pyo3.rs/latest/function/error_handling.html#foreign-rust-error-types
pub struct WrappedError(egg_smol::Error);

// Convert from the WrappedError to the PyErr by creating a new Python error
impl From<WrappedError> for PyErr {
    fn from(error: WrappedError) -> Self {
        PyErr::new::<EggSmolError, _>(error.0.to_string())
    }
}

// Convert from an egg_smol::Error to a WrappedError
impl From<egg_smol::Error> for WrappedError {
    fn from(other: egg_smol::Error) -> Self {
        Self(other)
    }
}

// Use similar to PyResult, wraps a result type and can be converted to PyResult
pub type EggResult<T> = Result<T, WrappedError>;
