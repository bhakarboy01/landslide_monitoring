# AI Landslide Detection Research

## Overview
This document contains research findings on AI-based landslide detection methods and datasets for integration into the landslide monitoring system.

## Key Datasets

### 1. CAS Landslide Dataset
- **Source**: Chinese Academy of Sciences (CAS)
- **Size**: 20,865 RGB images
- **Coverage**: 9 distinct regions worldwide
- **Data Sources**: Satellite imagery (Sentinel-2A/B, Landsat) and UAV imagery
- **Key Features**:
  - Large-scale and multisensor dataset
  - Diverse terrain and environmental conditions
  - High-quality annotations
  - Publicly available for research
  - Addresses limitations of existing smaller datasets
- **Access**: Available through Google Earth Engine and collaborative partners
- **Publication**: Nature Scientific Data (2024)

### 2. Landslide4Sense Dataset
- **Source**: Kaggle competition dataset
- **Purpose**: Multi-sensor satellite imagery for global landslide detection
- **Features**: Promotes research in landslide detection using satellite data
- **Access**: Available on Kaggle platform

### 3. HR-GLDD (High-Resolution Global Landslide Detection Dataset)
- **Features**: High-resolution satellite imagery
- **Coverage**: Globally distributed
- **Purpose**: Artificial intelligence applications in landslide detection

## Research Approaches

### Deep Learning Methods
1. **Convolutional Neural Networks (CNNs)**
   - U-Net architecture for landslide segmentation
   - Multi-source data fusion networks (MSFD-Net)
   - Transfer learning approaches

2. **Machine Learning Techniques**
   - Support Vector Machines (SVM)
   - Random Forest classifiers
   - Ensemble methods

### Data Sources
1. **Satellite Imagery**
   - Sentinel-2A/B
   - Landsat series
   - Planet imagery
   - Digital Globe

2. **UAV Imagery**
   - High-resolution local data
   - Real-time monitoring capabilities
   - Flexible deployment

## Implementation Considerations for Raspberry Pi

### Computational Constraints
- Limited processing power
- Memory constraints
- Need for optimized models

### Potential Solutions
1. **Model Optimization**
   - Quantization techniques
   - Pruning methods
   - Knowledge distillation

2. **Edge Computing Approaches**
   - TensorFlow Lite
   - ONNX Runtime
   - OpenVINO toolkit

3. **Hybrid Processing**
   - Local preprocessing
   - Cloud-based inference
   - Edge-cloud collaboration

## Next Steps
1. Evaluate lightweight model architectures
2. Implement transfer learning from pre-trained models
3. Develop real-time inference pipeline
4. Test performance on Raspberry Pi hardware



## Lightweight AI Models for Raspberry Pi

### MobileNetV2
**Overview**: Lightweight and efficient CNN designed for image classification and recognition tasks, especially on mobile and embedded devices like Raspberry Pi.

**Key Features**:
- **Lightweight**: Smaller in size compared to models like ResNet or VGG
- **Fast**: Uses fewer resources, making it suitable for real-time applications
- **Efficient**: Reduces computation by using depthwise separable convolutions
- **Pretrained**: Easily available as a pretrained model on TensorFlow and Keras

**Technical Details**:
- Uses depthwise separable convolutions (breaks standard convolution into depthwise and pointwise)
- Inverted residual blocks with bottleneck structure
- Reduces number of operations while maintaining performance

**Limitations**:
- Slightly lower accuracy than heavier models
- Not suitable for tasks needing high-detail features like medical imaging

### SSD MobileNet
**Overview**: Combines Single Shot MultiBox Detector (SSD) with MobileNet for object detection.

**Key Features**:
- Real-time object detection
- Optimized for mobile and edge devices
- Good balance between speed and accuracy

### Other Lightweight Models
1. **Vosk**: Speech recognition model
2. **FER+**: Facial emotion recognition
3. **Scikit-learn**: Traditional machine learning algorithms

## Performance Considerations
- Models optimized for real-time performance on low-power devices
- Trade-off between accuracy and computational efficiency
- Suitable for applications where speed is more important than perfect accuracy

## Tools and Frameworks
- **TensorFlow Lite**: Optimized for mobile and edge devices
- **Keras**: High-level neural networks API
- **OpenCV**: Computer vision library
- **NumPy**: Numerical computing library


## Transfer Learning for Landslide Detection

### Research Findings from MDPI Paper (2022)

**Study Overview**: "Improving Landslide Recognition on UAV Data through Transfer Learning"
- **Authors**: Kaixin Yang, Wei Li, Xinran Yang, Lei Zhang
- **Publication**: Applied Sciences, 2022
- **Focus**: UAV-based landslide detection using transfer learning

**Key Challenges Addressed**:
1. **Insufficient Training Data**: Few public datasets available for landslide disasters
2. **Computational Requirements**: Deep learning models require massive computing resources
3. **Time Constraints**: Emergency response requires rapid disaster assessment

**Transfer Learning Approach**:
- **Source Domains Used**:
  - Places365 dataset
  - UC Merced land use dataset
  - RSSCN7 dataset
- **Method**: Fine-tuning existing model parameters with small field samples
- **Benefits**: Reduced computing resources and training time

**Technical Implementation**:
- **Base Model**: SSD (Single Shot MultiBox Detector)
- **Comparison**: Transfer learning vs traditional SSD model
- **Results**: Better detection performance with transfer learning approach

**Study Area**: Zhangmu Port region in Tibet (affected by Nepal earthquake, April 25, 2015)

### Deep Learning Methods for Landslide Detection

**Popular Architectures**:
1. **Region-based Methods**:
   - R-CNN, Fast R-CNN, Faster R-CNN
   - R-FCN (Region-based Fully Convolutional Networks)
   - Higher accuracy but slower processing

2. **Regression-based Methods**:
   - YOLO (You Only Look Once)
   - SSD (Single Shot MultiBox Detector)
   - Faster processing but potentially lower accuracy

**Advantages of Deep Learning**:
- Automatic feature extraction from raw images
- Large-area landslide detection capability
- Better suited for emergency response requirements
- Reduced manual interpretation workload

### Implementation Strategy for Raspberry Pi

**Recommended Approach**:
1. **Use Transfer Learning**: Leverage pre-trained models to reduce training requirements
2. **Model Optimization**: Convert to TensorFlow Lite for edge deployment
3. **Hybrid Processing**: Combine local preprocessing with cloud-based inference when needed
4. **Progressive Enhancement**: Start with simple detection, add complexity over time

