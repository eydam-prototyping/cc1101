use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use core::time;
use std::{thread::sleep, time::{Duration, SystemTime, UNIX_EPOCH}};
use rppal::gpio::{Gpio, InputPin, Level, Trigger};

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

#[pyclass]
pub struct CapturedBits{
    start_capture: Duration,
    end_capture: Duration,
    bits: Vec<u8>,
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

#[pymethods]
impl CapturedBits{
    #[getter]
    fn get_start_capture(&self) -> f64{
        self.start_capture.as_secs_f64()
    }
    #[getter]
    fn get_end_capture(&self) -> f64{
        self.end_capture.as_secs_f64()
    }
    #[getter]
    fn get_bits(&self) -> Vec<u8>{
        self.bits.clone()
    }
}

fn wait_for_interrupt_non_py(pin: &mut InputPin, timeout_ms: Duration, direction: Trigger) -> Option<Level> {
    pin.set_interrupt(direction).unwrap();
    loop {
        match pin.poll_interrupt(false, Some(timeout_ms)) {
            Ok(None) => return None,
            Ok(Some(Level::Low)) => return Some(Level::Low),
            Ok(Some(Level::High)) => return Some(Level::High),
            Err(_) => return None,
        }
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
fn asynchronous_serial_read(threshold_pin_number: u8, data_pin_number:u8, timeout_ms: u64) -> PyResult<Option<CapturedTransitions>> {
    // Wait for the rising edge on GDO0
    let rising_edge = wait_for_interrupt(threshold_pin_number, timeout_ms, TRIGGER_RISING_EDGE)?;
    if rising_edge.is_none() {
        return Ok(None); // Timeout
    }
    let start_capture = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    
    let mut transitions: Vec<(f64, u8)> = Vec::new();
    let gdo0_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(threshold_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_input();

    loop{
        if gdo0_pin.is_low(){
            break;
        }
        let signal_edge = wait_for_interrupt(data_pin_number, timeout_ms, TRIGGER_BOTH_EDGES)?;
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

#[pyfunction]
fn asynchronous_serial_write(data_pin_number:u8, baudrate:u32, data:Vec<u8>) -> PyResult<Option<()>> {
    let gpio = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
    
    let pin = gpio.get(data_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?;

    let mut data_pin = pin.into_output();

    let bit_time = 1.0 / baudrate as f64;
    for byte in data{
        for i in 0..8{
            // Write the bit to the data pin
            let bit = (byte >> i) & 1;
            // Wait for the bit time
            std::thread::sleep(Duration::from_secs_f64(bit_time));
            // Write the bit to the data pin
            match bit{
                0 => data_pin.set_low(),
                1 => data_pin.set_high(),
                _ => return Err(PyRuntimeError::new_err("Invalid bit value.")),
            };
        }
    }
    Ok(Some(()))
}

#[pyfunction]
fn synchronous_serial_write(clock_pin_number: u8, data_pin_number:u8, data:Vec<u8>, baudrate: u32) -> PyResult<Option<()>> {
    
    let mut data_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(data_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_output();
    data_pin.set_low();
    sleep(time::Duration::from_micros(10000));

    let mut clock_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(clock_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_input();

    for byte in data{
        for i in 0..8{
            let bit = (byte >> (7-i)) & 1;
            wait_for_interrupt_non_py(&mut clock_pin, Duration::from_millis(1000), Trigger::FallingEdge);
            match bit{
                0 => data_pin.set_low(),
                1 => data_pin.set_high(),
                _ => return Err(PyRuntimeError::new_err("Invalid bit value.")),
            };
            wait_for_interrupt_non_py(&mut clock_pin, Duration::from_millis(1000), Trigger::RisingEdge);
        }
    }
    Ok(Some(()))
}

#[pyfunction]
fn synchronous_serial_read(clock_pin_number: u8, data_pin_number:u8, timeout_ms: u64, max_same_bits: u8) -> PyResult<Option<CapturedBits>> {
    // Wait for the rising edge on GDO0
    
    let mut bits: Vec<u8> = Vec::new();

    let mut data_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(data_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_input();

    let mut clock_pin = Gpio::new()
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .get(clock_pin_number)
        .map_err(|err| PyRuntimeError::new_err(err.to_string()))?
        .into_input();

    let mut same_bits = 1;
    let mut last_bit = 1;

    let _ = wait_for_interrupt_non_py(&mut data_pin, Duration::from_millis(timeout_ms), Trigger::RisingEdge).ok_or_else(|| PyRuntimeError::new_err("Timeout waiting for rising edge"))?;
    
    let start_capture = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    loop{
        /*let clock_edge = wait_for_interrupt(clock_pin_number, timeout_ms, TRIGGER_FALLING_EDGE)?;
        if clock_edge.is_none(){
            return Ok(None); // Timeout
        }*/
        let _ = wait_for_interrupt_non_py(&mut clock_pin, Duration::from_millis(timeout_ms), Trigger::RisingEdge).ok_or_else(|| PyRuntimeError::new_err("Timeout waiting for falling edge"))?;

        let bit = data_pin.read();
        if bit == Level::High{
            bits.push(1);
            if last_bit == 1{
                same_bits += 1;
            }else{
                same_bits = 1;
                last_bit = 1;
            }
        }else{
            bits.push(0);
            if last_bit == 0{
                same_bits += 1;
            }else{
                same_bits = 1;
                last_bit = 0;
            }
        }
        if same_bits == max_same_bits{
            break;
        }
    }
    
    let end_capture = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    Ok(Some(CapturedBits{start_capture, end_capture, bits}))

}

#[pymodule]
fn rust_rpi_cc1101_driver(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(asynchronous_serial_read, m)?)?;
    m.add_function(wrap_pyfunction!(asynchronous_serial_write, m)?)?;
    m.add_function(wrap_pyfunction!(synchronous_serial_read, m)?)?;
    m.add_function(wrap_pyfunction!(synchronous_serial_write, m)?)?;
    m.add_function(wrap_pyfunction!(wait_for_interrupt, m)?)?;

    m.add("TRIGGER_DISABLED", TRIGGER_DISABLED)?;
    m.add("TRIGGER_RISING_EDGE", TRIGGER_RISING_EDGE)?;
    m.add("TRIGGER_FALLING_EDGE", TRIGGER_FALLING_EDGE)?;
    m.add("TRIGGER_BOTH", TRIGGER_BOTH_EDGES)?;

    m.add("GPIO_LOW", GPIO_LOW)?;
    m.add("GPIO_HIGH", GPIO_HIGH)?;

    Ok(())
}
