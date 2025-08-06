# Human Detection Safety System for Assembly Lines

A comprehensive real-time safety monitoring system designed for automobile assembly lines that detects human presence, body parts (hands, head, arms), and triggers immediate audio/visual alarms when safety violations are detected.

## 🚨 Features

### Core Safety Features
- **Multi-Model Human Detection**: Combines YOLOv8 and MediaPipe for maximum accuracy
- **Body Part Detection**: Specific detection of hands, head, arms, and torso
- **Configurable Safety Zones**: Define danger zones and safe areas with polygon coordinates
- **Real-time Alerts**: Immediate audio and visual alarms for safety violations
- **Emergency Protocols**: Automatic emergency response for consecutive violations
- **Incident Logging**: Comprehensive logging with screenshot capture

### Technical Features
- **High Performance**: Optimized for real-time processing at 30+ FPS
- **Multiple Camera Support**: Works with webcams, IP cameras, and video files
- **Configurable Thresholds**: Adjustable confidence levels and detection parameters
- **Safety Score Calculation**: Real-time safety assessment scoring
- **Statistics & Reporting**: Detailed performance and incident analytics

## 🏭 Use Cases

- **Assembly Robot Areas**: Detect human intrusion near robotic equipment
- **Conveyor Belt Zones**: Monitor for unsafe human proximity to moving machinery
- **Restricted Access Areas**: Alert when personnel enter unauthorized zones
- **Hand Safety**: Critical detection of hands near dangerous machinery
- **Emergency Response**: Automatic protocols for consecutive safety violations

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-capable GPU (recommended for optimal performance)
- Webcam or IP camera
- Linux/Windows/macOS

### Quick Installation

```bash
# Clone the repository
cd /workspace/human_detection_safety_system

# Install dependencies
pip install -r requirements.txt

# Run the system
python main.py
```

### Detailed Setup

1. **Install Python Dependencies**:
```bash
pip install opencv-python==4.8.1.78
pip install ultralytics==8.0.196
pip install mediapipe==0.10.7
pip install torch torchvision
pip install pygame PyYAML numpy pandas scikit-learn matplotlib seaborn
```

2. **Download YOLO Models** (automatic on first run):
```bash
# Models will be downloaded automatically:
# - yolov8n.pt (nano - fastest)
# - yolov8s.pt (small)
# - yolov8m.pt (medium)
# - yolov8l.pt (large)
# - yolov8x.pt (extra large - most accurate)
```

3. **Configure Your Setup**:
```bash
# Copy and edit configuration file
cp config/safety_config.yaml config/my_assembly_line.yaml
# Edit the configuration file for your specific setup
```

## ⚙️ Configuration

### Basic Configuration

Edit `config/safety_config.yaml` to customize for your assembly line:

```yaml
# Camera Settings
camera:
  device_id: 0  # 0 for webcam, "rtsp://ip:port/stream" for IP camera
  resolution:
    width: 1920
    height: 1080
  fps: 30

# Safety Zones (normalized coordinates 0.0-1.0)
safety_zones:
  danger_zones:
    - name: "Assembly Robot Area"
      coordinates: [[0.2, 0.3], [0.8, 0.3], [0.8, 0.9], [0.2, 0.9]]
      color: [255, 0, 0]  # Red
    - name: "Conveyor Belt Zone"
      coordinates: [[0.0, 0.7], [1.0, 0.7], [1.0, 1.0], [0.0, 1.0]]
      color: [255, 165, 0]  # Orange

# Detection Models
models:
  yolo:
    model_path: "yolov8n.pt"  # Use yolov8x.pt for maximum accuracy
    confidence_threshold: 0.5
  pose_estimation:
    enabled: true
    min_detection_confidence: 0.7

# Alert System
alerts:
  audio:
    enabled: true
    volume: 0.8
    repeat_interval: 2.0
  visual:
    enabled: true
    flash_duration: 0.5
```

### Advanced Configuration

#### Safety Zones Setup
Define safety zones using normalized coordinates (0.0 to 1.0):

```yaml
safety_zones:
  danger_zones:
    - name: "Robot Arm Zone"
      coordinates: [[0.1, 0.2], [0.6, 0.2], [0.6, 0.8], [0.1, 0.8]]
      color: [255, 0, 0]  # Red for critical areas
      alpha: 0.3
  safe_zones:
    - name: "Operator Walkway"
      coordinates: [[0.0, 0.0], [1.0, 0.0], [1.0, 0.3], [0.0, 0.3]]
      color: [0, 255, 0]  # Green for safe areas
```

#### Detection Sensitivity
Adjust detection thresholds based on your environment:

```yaml
models:
  yolo:
    confidence_threshold: 0.7  # Higher = fewer false positives
    iou_threshold: 0.45
  pose_estimation:
    min_detection_confidence: 0.8  # Higher = more accurate pose detection
```

#### Emergency Protocols
Configure automatic emergency responses:

```yaml
emergency:
  auto_shutdown_enabled: false  # Set to true for equipment shutdown
  max_consecutive_detections: 5  # Trigger emergency after N detections
  detection_timeout: 10.0  # Reset counter after N seconds
  emergency_contact: "security@company.com"
```

## 🚀 Usage

### Basic Usage

```bash
# Run with default configuration
python main.py

# Run with custom configuration
python main.py --config config/my_assembly_line.yaml

# Enable verbose logging
python main.py --verbose
```

### Interactive Controls

While the system is running:
- **'q'**: Quit the system
- **'p'**: Pause/Resume monitoring
- **'s'**: Show detailed statistics
- **'r'**: Reset emergency protocol

### System Output

The system displays:
- **Live video feed** with safety zones overlay
- **Detection boxes** around humans and body parts
- **Safety alerts** with severity levels
- **Real-time statistics** (FPS, safety score, violations)
- **System status** (Active, Emergency, Paused)

## 📊 Monitoring & Analytics

### Real-time Statistics
```bash
📊 SYSTEM STATISTICS
==================================================
Runtime: 01:23:45
Frames processed: 150,450
Current FPS: 28.5
Detection FPS: 25.2
Emergency risk level: LOW
Active alerts: 0
Total incidents: 3
Screenshots captured: 3
==================================================
```

### Incident Logs
All incidents are logged to CSV with:
- Timestamp and unique incident ID
- Severity level (LOW, MEDIUM, HIGH, CRITICAL)
- Zone and detection type
- Screenshot capture
- Body parts involved
- Emergency status

### Log Files
- **System logs**: `logs/safety_system.log`
- **Incident reports**: `logs/incidents.csv`
- **Screenshots**: `logs/screenshots/`

## 🔧 Customization

### Adding New Safety Zones

1. **Define zone coordinates** in the configuration:
```yaml
safety_zones:
  danger_zones:
    - name: "New Machinery Zone"
      coordinates: [[0.3, 0.4], [0.7, 0.4], [0.7, 0.9], [0.3, 0.9]]
      color: [255, 100, 0]
```

2. **Test zone placement** by running the system and observing the overlay

### Custom Alert Messages

```yaml
alerts:
  text_alerts:
    messages:
      human_detected: "⚠️ OPERATOR IN DANGER ZONE ⚠️"
      hand_detected: "🚫 HANDS NEAR MACHINERY - STOP IMMEDIATELY 🚫"
      pose_detected: "⚠️ UNSAFE POSTURE DETECTED ⚠️"
```

### Performance Optimization

For high-performance requirements:

```yaml
# Use faster YOLO model
models:
  yolo:
    model_path: "yolov8n.pt"  # Fastest

# Reduce processing load
performance:
  skip_frames: 1  # Process every other frame
  resize_factor: 0.75  # Reduce input resolution

# Optimize camera settings
camera:
  resolution:
    width: 1280  # Lower resolution for speed
    height: 720
  fps: 30
```

## 🛡️ Safety Considerations

### Critical Safety Notes
- **This system is a safety aid, not a replacement for proper safety protocols**
- **Always maintain physical safety barriers and equipment**
- **Regularly test and calibrate the system**
- **Train operators on system alerts and responses**
- **Have manual emergency stops readily available**

### Recommended Setup
1. **Position cameras** to minimize blind spots
2. **Ensure adequate lighting** for consistent detection
3. **Regular maintenance** of cameras and equipment
4. **Backup power supply** for critical installations
5. **Network redundancy** for IP camera systems

## 📝 Troubleshooting

### Common Issues

**Camera not detected:**
```bash
# Check available cameras
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Update device_id in config
camera:
  device_id: 1  # Try different numbers
```

**Low detection accuracy:**
```yaml
# Increase model size
models:
  yolo:
    model_path: "yolov8x.pt"  # Most accurate but slower

# Adjust confidence thresholds
models:
  yolo:
    confidence_threshold: 0.3  # Lower = more sensitive
```

**Performance issues:**
```yaml
# Optimize for speed
models:
  yolo:
    model_path: "yolov8n.pt"  # Fastest model

performance:
  skip_frames: 2  # Process every 3rd frame
  resize_factor: 0.5  # Half resolution
```

### Error Messages

| Error | Solution |
|-------|----------|
| `Camera not found` | Check device_id in config |
| `YOLO model not found` | Run with internet connection to download |
| `Audio initialization failed` | Install pygame: `pip install pygame` |
| `Configuration file not found` | Check path in command line argument |

## 📞 Support & Maintenance

### Regular Maintenance
- **Weekly**: Check log files and incident reports
- **Monthly**: Clean camera lenses and check positioning
- **Quarterly**: Review and update safety zones
- **Annually**: Full system calibration and testing

### Performance Monitoring
Monitor these key metrics:
- **Detection FPS**: Should be >20 for real-time performance
- **False positive rate**: Should be <5% in normal conditions
- **System uptime**: Target >99.5% availability
- **Response time**: Alerts should trigger within 200ms

### System Updates
```bash
# Update dependencies
pip install --upgrade ultralytics opencv-python mediapipe

# Backup configuration before updates
cp config/safety_config.yaml config/safety_config_backup.yaml
```

## 📄 License & Compliance

This system is designed for industrial safety applications. Ensure compliance with:
- Local workplace safety regulations
- Data privacy laws (if recording personnel)
- Industry-specific safety standards (ISO, OSHA, etc.)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional detection models
- Enhanced safety zone algorithms
- Integration with industrial control systems
- Mobile app for remote monitoring
- Advanced analytics and reporting

---

**⚠️ IMPORTANT SAFETY NOTICE ⚠️**

This system is designed to enhance safety but should never be the sole safety measure. Always maintain proper physical safety barriers, emergency stops, and trained personnel. Regular testing and maintenance are essential for reliable operation.