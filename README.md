# DeLTA SHG Control Center

An integrated Python-based control and analysis suite for Second Harmonic Generation (SHG) experiments. This system seamlessly manages both Andor CCD cameras and Standa motorized stages, providing synchronized data acquisition and advanced image analysis capabilities.

---

## 🚀 Features

- **Camera Control**
  - Full integration with Andor SDK2 via `pylablib`
  - Temperature regulation with context-managed sessions
  - Configurable exposure time, EM gain, shutter mode, and readout mode
  - Support for `.sif` and `.h5` file formats with metadata extraction

- **Motor Control**
  - Dual-axis rotation using Standa 8MRU stages
  - Homing, zeroing, and synchronized speed/acceleration settings
  - Threaded motor control for concurrent camera acquisition

- **Data Analysis**
  - Interactive background selection and ROI definition
  - Circular averaging with customizable angular binning
  - Polar and Cartesian intensity plots
  - Export of processed data to `.txt` files

- **User Interface**
  - Command-line interface for streamlined operations
  - Modular class design for extensibility and integration

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.8 or higher
- [Anaconda](https://www.anaconda.com/) (recommended for package management)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/TedMercer/DeLTA_SHG_Control_Center.git
   cd DeLTA_SHG_Control_Center
   ```

2. **Create and activate a virtual environment:**

   ```bash
   conda create -n delta_shg_env python=3.8
   conda activate delta_shg_env
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Ensure that the Andor SDK2 drivers are installed and properly configured on your system.*

---

## 📂 Directory Structure

```
DeLTA_SHG_Control_Center/
├── camController.py          # Camera control module
├── motorController.py        # Motor control module
├── mainController.py         # Main script for synchronized acquisition
├── SHG_Analysis_class.py     # Data analysis class
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚙️ Usage

### Running the Main Controller

```bash
python mainController.py
```

This script initializes the camera and motors, performs synchronized data acquisition, and saves the results to the specified directory.

### Using the SHGUI

Refer to my analysis repo on how to view the data. [SHGUI](https://github.com/TedMercer/SHGUI)
---

## 📸 Example Workflow

1. **Initialize the camera and motors using `mainController.py`.**
2. **Acquire synchronized data while rotating the sample.**
3. **Analyze the acquired data using [SHGUI](https://github.com/TedMercer/SHGUI).**
4. **Visualize and export the results for further analysis.**

---

## 🧪 Testing

To test individual components:

- **Camera Initialization:**

  ```python
  from camController import Cam
  with Cam(name='test', data_path='path_to_save') as cam:
      cam.set_exposure(2.0)
      cam.set_em_gain(0)
      cam.acquire_and_plot(save=True)
  ```

- **Motor Control:**

  ```python
  from motorController import StandaMotor
  motor = StandaMotor('xi-com:\\\\.\\COM4')
  motor.gth()
  motor.set_speed(500)
  motor.rotate('right', duration=5)
  motor.close()
  ```

---

## 📧 Contact

For questions, suggestions, or contributions, please contact [e.mercer@northeastern.edu](mailto:e.mercer@northeastern.edu).

---

## 📝 License

This project is licensed under the MIT License. Please look at the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- [pylablib](https://github.com/labpy/pylablib) for device interfacing
- [Standa Customer Support](https://www.standa.lt/) for their support
