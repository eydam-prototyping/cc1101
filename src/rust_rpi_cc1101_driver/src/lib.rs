use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use rppal::gpio::{Gpio, Level, Trigger};

pub const TRIGGER_DISABLED: u8 = 0;
pub const TRIGGER_RISING_EDGE: u8 = 1;
pub const TRIGGER_FALLING_EDGE: u8 = 2;
pub const TRIGGER_BOTH_EDGES: u8 = 3;
pub const GPIO_LOW: u8 = 0;
pub const GPIO_HIGH: u8 = 1;

#[pyclass]
pub struct CapturedTransitions{
    start_capture: Duration,
    end_capture: Duration,
    transitions: Vec<(f64, u8)>,
}

#[pymethods]
impl CapturedTransitions{
    #[getter]
    fn get_start_capture(&self) -> f64{
        self.start_capture.as_secs_f64()
    }
    #[getter]
    fn get_end_capture(&self) -> f64{
        self.end_capture.as_secs_f64()
    }
    #[getter]
    fn get_transitions(&self) -> Vec<(f64, u8)>{
        self.transitions.clone()
    }
}

#[pyfunction]
fn wait_for_interrupt(pin_number: u8, timeout_ms: u64, direction: u8) -> PyResult<Option<u8>> {
    // Convert the direction to a Trigger
    let trigger = match direction {
        TRIGGER_DISABLED => Trigger::Disabled,
        TRIGGER_RISING_EDGE => Trigger::RisingEdge,
        TRIGGER_FALLING_EDGE => Trigger::FallingEdge,
        TRIGGER_BOTH_EDGES => Trigger::Both,
        _ => return Err(PyRuntimeError::new_err("Invalid trigger direction.")),
    };

    // Single steps to map errors to PyRuntimeError
    let gpio = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
    
    let pin = gpio.get(pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;

    let mut input_pin = pin.into_input();

    input_pin.set_interrupt(trigger)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;

    let timeout_d = Duration::from_millis(timeout_ms);
    // Poll the pin for an interrupt
    loop {
        match input_pin.poll_interrupt(false, Some(timeout_d)) {
            Ok(level) => {
                match level {
                    Some(Level::Low) => return Ok(Some(GPIO_LOW)),
                    Some(Level::High) => return Ok(Some(GPIO_HIGH)),
                    None => return Ok(None),
                };
            },
            Err(e) => return Err(PyRuntimeError::new_err(e.to_string())),
        }
    }
}

#[pyfunction]
fn serial_read(gdo0: u8, gdo2:u8, timeout_ms: u64) -> PyResult<Option<CapturedTransitions>> {
    // Wait for the rising edge on GDO0
    let rising_edge = wait_for_interrupt(gdo0, timeout_ms, TRIGGER_RISING_EDGE)?;
    if rising_edge.is_none() {
        return Ok(None); // Timeout
    }
    let start_capture = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    
    let mut transitions: Vec<(f64, u8)> = Vec::new();
    let gdo0_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(gdo0)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_input();

    loop{
        if gdo0_pin.is_low(){
            break;
        }
        let signal_edge = wait_for_interrupt(gdo2, timeout_ms, TRIGGER_BOTH_EDGES)?;
        if signal_edge.is_none(){
            return Ok(None); // Timeout
        }
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        transitions.push((timestamp.as_secs_f64(), signal_edge.unwrap()));
    }
    
    let end_capture = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    Ok(Some(CapturedTransitions{start_capture, end_capture, transitions}))
    
}

#[pymodule]
fn rust_rpi_cc1101_driver(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(serial_read, m)?)?;
    m.add_function(wrap_pyfunction!(wait_for_interrupt, m)?)?;

    m.add("TRIGGER_DISABLED", TRIGGER_DISABLED)?;
    m.add("TRIGGER_RISING_EDGE", TRIGGER_RISING_EDGE)?;
    m.add("TRIGGER_FALLING_EDGE", TRIGGER_FALLING_EDGE)?;
    m.add("TRIGGER_BOTH", TRIGGER_BOTH_EDGES)?;

    m.add("GPIO_LOW", GPIO_LOW)?;
    m.add("GPIO_HIGH", GPIO_HIGH)?;

    Ok(())
}
