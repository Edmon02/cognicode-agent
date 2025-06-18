#!/usr/bin/env python3
"""
Script to download and setup AI models for CogniCode Agent
"""

import os
import sys
from pathlib import Path
import requests
from transformers import AutoTokenizer, AutoModel, T5Tokenizer, T5ForConditionalGeneration

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger

logger = setup_logger('model-setup')

MODELS_DIR = Path('/app/models')
MODELS_TO_DOWNLOAD = [
    {
        'name': 'microsoft/codebert-base',
        'type': 'encoder',
        'use_case': 'code analysis and bug detection'
    },
    {
        'name': 'Salesforce/codet5-small',
        'type': 'encoder-decoder',
        'use_case': 'code generation and refactoring'
    }
]

def download_model(model_info):
    """Download and cache a specific model"""
    model_name = model_info['name']
    model_path = MODELS_DIR / model_name.replace('/', '_')
    
    logger.info(f"Downloading {model_name} for {model_info['use_case']}...")
    
    try:
        # Create model directory
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Download tokenizer and model based on type
        if model_info['type'] == 'encoder':
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Save to local directory
            tokenizer.save_pretrained(str(model_path))
            model.save_pretrained(str(model_path))
            
        elif model_info['type'] == 'encoder-decoder':
            tokenizer = T5Tokenizer.from_pretrained(model_name)
            model = T5ForConditionalGeneration.from_pretrained(model_name)
            
            # Save to local directory
            tokenizer.save_pretrained(str(model_path))
            model.save_pretrained(str(model_path))
        
        logger.info(f"Successfully downloaded {model_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {str(e)}")
        return False

def check_disk_space():
    """Check if there's enough disk space for models"""
    statvfs = os.statvfs(MODELS_DIR.parent)
    free_space_gb = (statvfs.f_frsize * statvfs.f_available) / (1024**3)
    
    logger.info(f"Available disk space: {free_space_gb:.2f} GB")
    
    if free_space_gb < 5:  # Require at least 5GB free
        logger.warning("Low disk space detected. Models may require 2-5GB.")
        return False
    
    return True

def main():
    """Main setup function"""
    logger.info("Starting CogniCode AI model setup...")
    
    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check disk space
    if not check_disk_space():
        logger.error("Insufficient disk space for model downloads")
        sys.exit(1)
    
    # Download each model
    success_count = 0
    for model_info in MODELS_TO_DOWNLOAD:
        if download_model(model_info):
            success_count += 1
    
    if success_count == len(MODELS_TO_DOWNLOAD):
        logger.info("All models downloaded successfully!")
        
        # Create a marker file to indicate setup completion
        marker_file = MODELS_DIR / '.setup_complete'
        marker_file.touch()
        
        logger.info("Model setup complete. CogniCode Agent is ready to use!")
    else:
        logger.error(f"Only {success_count}/{len(MODELS_TO_DOWNLOAD)} models downloaded successfully")
        sys.exit(1)

if __name__ == '__main__':
    main()