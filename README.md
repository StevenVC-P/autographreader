# 🖋️ Autograph Reader

An AI-powered system for detecting and identifying autographs in images using computer vision and machine learning. This project combines web scraping, data validation, and YOLO object detection to build a comprehensive autograph recognition system.

## 🎯 Project Overview

The Autograph Reader project builds a progressive machine learning pipeline for autograph detection in sports memorabilia images. The system uses an iterative training approach:

### **Phase 1: Foundation Model Development** 🏗️

1. **Data Collection**: Scraping autograph listings from eBay with metadata
2. **Signer Validation**: Using WikiData to verify legitimate signers
3. **Manual Bootstrap**: Hand-label first 300 autograph images for initial training
4. **Progressive Training**: Apply model → review predictions → retrain (iterative cycles)
5. **Foundation Model**: Build robust general autograph detector for sports memorabilia

### **Phase 2: Signer-Specific Recognition** 🎭

1. **Individual Models**: Train specialized models for specific athletes
2. **Signature Style Learning**: Recognize unique characteristics and variations
3. **Automated Pipeline**: Scale recognition to many sports figures
4. **Authenticity Scoring**: Provide confidence-based authenticity assessment

## 🏗️ Architecture

### **Progressive Training Pipeline**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WikiData      │    │      eBay       │    │   Manual        │
│   Scraping      │───▶│   Scraping      │───▶│   Labeling      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Known Signers   │    │   SQLite DB     │    │ Foundation Model│
│   Database      │    │  (Autographs)   │    │   (300 images)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Signer-Specific │◀───│ Semi-Supervised │◀───│ Model Inference │
│    Models       │    │   Expansion     │    │ + Human Review  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
autographreader/
├── scripts/
│   ├── scraping/           # Data collection scripts
│   ├── DataPreping/        # Dataset preparation scripts
│   ├── Validation/         # Model validation scripts
│   ├── ML/                 # Machine learning training scripts (planned)
│   └── debug/              # Debugging utilities
├── config/                 # Configuration files (gitignored)
├── database/               # SQLite database (gitignored)
├── data/                   # Training and validation data (gitignored)
│   ├── training/           # Manual labeling workspace
│   ├── test_training/      # Validation dataset
│   └── unseen_eval/        # Test dataset for evaluation
├── yolo_dataset/           # YOLO-formatted datasets (gitignored)
├── models/                 # Trained model checkpoints (gitignored)
└── qa_review/              # Quality assurance data (gitignored)
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install requests undetected-chromedriver selenium beautifulsoup4 sqlite3
```

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/StevenVC-P/autographreader.git
   cd autographreader
   ```

2. **Follow the execution order** (see below)

## 📋 Progressive Training Workflow

### **Foundation Model Training (Phase 1)** 🏗️

#### **Step 1: Data Collection**

```bash
# Build signer reference database
python scripts/scraping/WikiDataScraping.py

# Collect autograph images from eBay
python scripts/scraping/eBayScraping.py

# Optional: QA review of scraped data
python scripts/DataPreping/export_scrape_qacheck.py
```

#### **Step 2: Manual Bootstrap (300 Images)**

```bash
# Export first batch for manual labeling
python scripts/DataPreping/export_for_labeling.py  # 200 images
# [Manual labeling using LabelImg - batch 1]

python scripts/DataPreping/export_for_labeling.py  # 100 more images
# [Manual labeling using LabelImg - batch 2]
# Total: 300 manually labeled images

# Check labeling progress
python scripts/DataPreping/countimages.py
```

#### **Step 3: Initial Model Training**

```bash
# Create YOLO training dataset
python scripts/DataPreping/export_yolo_dataset.py
python scripts/Validation/export_validation_sample.py

# Train foundation model (external YOLO training)
# Target: mAP > 0.7 for basic autograph detection
```

### **Semi-Supervised Expansion (Phase 1 Continued)** 🔄

#### **Step 4: Iterative Improvement Cycles**

```bash
# Export new batch for model inference
python scripts/DataPreping/export_for_labeling.py  # Next 200-300 images

# [Apply trained model to predict bounding boxes - planned script]
# [Human review and correction of predictions - planned script]
# [Retrain model with expanded dataset - planned script]

# Repeat cycle until satisfactory performance
# Target: mAP > 0.85, robust sports memorabilia detection
```

### **Signer-Specific Training (Phase 2)** 🎭

#### **Step 5: Individual Athlete Models**

```bash
# [Filter dataset by specific signers - planned script]
# [Train signer-specific models - planned script]
# [Evaluate individual recognition accuracy - planned script]

# Target: >90% accuracy for top 50 athletes
# Focus: Signature style recognition and authenticity scoring
```

### **Current Available Scripts** 📝

#### **Data Collection & Preparation**

- `scripts/scraping/WikiDataScraping.py` - Build signer database
- `scripts/scraping/eBayScraping.py` - Scrape eBay listings
- `scripts/DataPreping/export_scrape_qacheck.py` - QA review export
- `scripts/DataPreping/export_for_labeling.py` - Export for manual labeling
- `scripts/DataPreping/countimages.py` - Monitor labeling progress
- `scripts/DataPreping/export_yolo_dataset.py` - Create YOLO dataset

#### **Validation & Testing**

- `scripts/Validation/export_validation_sample.py` - Create validation set
- `scripts/Validation/export_unseen_for_inference.py` - Create test set

#### **Debugging**

- `scripts/debug/SeleniumErrorDebug.py` - Troubleshoot scraping issues

## 🛠️ Key Features

### Web Scraping

- **Anti-detection**: Undetected Chrome, rotating user agents
- **Proxy support**: Built-in proxy rotation (currently disabled)
- **Rate limiting**: Respectful scraping with delays
- **Duplicate detection**: Avoids re-scraping existing data

### Data Validation

- **WikiData integration**: Validates signer authenticity
- **Confidence scoring**: Assigns confidence levels to matches
- **Caching**: Reduces API calls with local cache

### Dataset Management

- **Incremental updates**: Supports resuming interrupted scrapes
- **Quality control**: Manual review workflow
- **Version control**: Cutoff system for dataset versions
- **Format conversion**: Automatic YOLO format preparation

### Progressive Training

- **Manual Bootstrap**: Start with 300 hand-labeled images
- **Semi-Supervised Learning**: Model predictions + human review cycles
- **Iterative Improvement**: Continuous model refinement
- **Signer-Specific Models**: Individual athlete recognition

## 🗄️ Database Schema

### Current Tables

- **signers**: Signer information and metadata
- **autographs**: Listing details, images, and signer associations
- **scrape_runs**: Tracking scraping sessions

### Planned ML Tracking Tables

- **labeling_sessions**: Track manual labeling progress
- **model_training**: Store training run metrics and model paths
- **prediction_reviews**: Track human review of model predictions

## ⚙️ Configuration

### Signer Categories (WikiData)

Currently focused on:

- Athletes (`Q2066131`)
- Professional wrestlers (`Q2309784`)
- Baseball players (`Q10833314`)
- American football players (`Q3665646`)
- Coaches (`Q41583`)

### eBay Categories

- Sports memorabilia (`64482`)
- Additional categories available but commented out

## 🔧 Debugging

### Selenium Issues

```bash
python scripts/debug/SeleniumErrorDebug.py
```

- Tests Chrome driver functionality
- Helps diagnose scraping problems

## 📊 Progressive Training Summary

### **Phase 1: Foundation Model**

```
WikiData → eBay → Manual Labeling (300) → Foundation Model → Semi-Supervised Cycles
```

### **Phase 2: Signer-Specific Models**

```
Foundation Model → Signer Filtering → Individual Training → Authenticity Scoring
```

### **Success Metrics**

- **Foundation Model**: mAP > 0.85 for general autograph detection
- **Signer Models**: >90% accuracy for top 50 athletes
- **Production Ready**: Fast inference (<100ms) + confidence scoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.

## 🚨 Important Notes

- **Respect robots.txt**: Always follow website scraping policies
- **Rate limiting**: Built-in delays prevent server overload
- **Data privacy**: No personal information is collected
- **Fair use**: Images are used for research/educational purposes

## 🔮 Planned ML Scripts

### **Semi-Supervised Training Pipeline**

- [ ] `scripts/ML/apply_model_predictions.py` - Run inference on new images
- [ ] `scripts/ML/review_predictions.py` - Human review interface for corrections
- [ ] `scripts/ML/train_yolo_model.py` - Automated YOLO training pipeline
- [ ] `scripts/ML/evaluate_model.py` - Model performance evaluation

### **Signer-Specific Recognition**

- [ ] `scripts/ML/filter_by_signer.py` - Create signer-specific datasets
- [ ] `scripts/ML/train_signer_models.py` - Individual athlete model training
- [ ] `scripts/ML/authenticity_scorer.py` - Signature authenticity assessment

### **Future Enhancements**

- [ ] Support for additional auction sites
- [ ] More signer categories (entertainment, politics, etc.)
- [ ] Advanced ML models (transformer-based detection)
- [ ] Real-time inference API
- [ ] Web interface for model testing

---

**Happy autograph hunting! 🖋️✨**
