# Sample DICOM test data for DICOMweb conformance testing

This directory contains sample DICOM files used for testing STOW-RS (Store) operations.

## Files

### sample_ct.dcm
A minimal CT scan DICOM file for testing basic DICOM object storage.

### sample_xray.dcm
A minimal X-ray DICOM file for testing different modality storage.

## Creating Sample DICOM Files

To generate proper DICOM test files, you can use the following Python script:

```python
import pydicom
import numpy as np
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ImplicitVRLittleEndian
import datetime

def create_sample_ct():
    """Create a sample CT DICOM file."""
    # Create a minimal CT dataset
    ds = Dataset()
    ds.file_meta = Dataset()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage
    ds.file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    ds.file_meta.ImplementationClassUID = "1.2.3.4.5.6.7.8.9"
    
    # Patient information
    ds.PatientName = "Test^Patient"
    ds.PatientID = "TEST123"
    ds.PatientBirthDate = "19850101"
    ds.PatientSex = "M"
    
    # Study information
    ds.StudyInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    ds.StudyDate = "20230101"
    ds.StudyTime = "120000"
    ds.AccessionNumber = "ACC123"
    ds.StudyID = "STUDY001"
    
    # Series information
    ds.SeriesInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.16"
    ds.SeriesNumber = 1
    ds.Modality = "CT"
    ds.SeriesDate = "20230101"
    ds.SeriesTime = "120000"
    
    # Instance information
    ds.SOPInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    ds.InstanceNumber = 1
    
    # Image information
    ds.Rows = 512
    ds.Columns = 512
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    
    # Create minimal pixel data
    ds.PixelData = np.random.randint(0, 4096, (512, 512), dtype=np.uint16).tobytes()
    
    return ds

def create_sample_xray():
    """Create a sample X-ray DICOM file."""
    # Similar structure but with different SOP class for X-ray
    ds = create_sample_ct()
    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1"  # CR Image Storage
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
    ds.Modality = "CR"
    ds.PixelData = np.random.randint(0, 4096, (1024, 1024), dtype=np.uint16).tobytes()
    ds.Rows = 1024
    ds.Columns = 1024
    
    return ds

# Generate the files
if __name__ == "__main__":
    # Generate sample CT
    ct_ds = create_sample_ct()
    ct_ds.save_as("sample_ct.dcm")
    print("Generated sample_ct.dcm")
    
    # Generate sample X-ray
    xray_ds = create_sample_xray()
    xray_ds.save_as("sample_xray.dcm")
    print("Generated sample_xray.dcm")
```

## Requirements

To generate proper DICOM test files, install pydicom:
```bash
pip install pydicom numpy
```

Then run the script above to generate the test files.