#!/usr/bin/env python3
"""
Generate sample DICOM test files for DICOMweb conformance testing.
"""

import struct
import os

def create_minimal_dicom_file(filename, sop_class_uid="1.2.840.10008.5.1.4.1.1.2", modality="CT"):
    """
    Create a minimal DICOM file for testing.
    
    Args:
        filename: Output filename
        sop_class_uid: SOP Class UID (default: CT Image Storage)
        modality: Modality type (default: CT)
    """
    
    # DICOM file header
    dicom_data = bytearray()
    
    # DICOM magic number
    dicom_data.extend(b'DICM')
    
    # Preamble (128 bytes of zeros)
    dicom_data.extend(b'\x00' * 128)
    
    # DICOM prefix (4 bytes)
    dicom_data.extend(b'DICM')
    
    # File Meta Information
    # File Meta Information Version
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0001))  # (0002,0001) File Meta Information Version
    dicom_data.extend(struct.pack('<BB', 0x00, 0x01))  # Value: 00 01
    
    # Media Storage SOP Class UID
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0002))  # (0002,0002) Media Storage SOP Class UID
    sop_class_data = sop_class_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<B', len(sop_class_data)))  # Length of string
    dicom_data.extend(sop_class_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Media Storage SOP Instance UID
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0003))  # (0002,0003) Media Storage SOP Instance UID
    sop_instance_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    sop_instance_data = sop_instance_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<B', len(sop_instance_data)))  # Length of string
    dicom_data.extend(sop_instance_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Transfer Syntax UID
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0010))  # (0002,0010) Transfer Syntax UID
    transfer_syntax = "1.2.840.10008.1.2"  # Implicit VR Little Endian
    transfer_syntax_data = transfer_syntax.encode('utf-8')
    dicom_data.extend(struct.pack('<B', len(transfer_syntax_data)))  # Length of string
    dicom_data.extend(transfer_syntax_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Implementation Class UID
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0012))  # (0002,0012) Implementation Class UID
    impl_class_uid = "1.2.3.4.5.6.7.8.9"
    impl_class_data = impl_class_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<B', len(impl_class_data)))  # Length of string
    dicom_data.extend(impl_class_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Implementation Version Name
    dicom_data.extend(struct.pack('<HH', 0x0002, 0x0013))  # (0002,0013) Implementation Version Name
    impl_version = "TEST_SOFT"
    impl_version_data = impl_version.encode('utf-8')
    dicom_data.extend(struct.pack('<B', len(impl_version_data)))  # Length of string
    dicom_data.extend(impl_version_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Minimal DICOM Data Set
    # Patient Name (0010,0010) - Person Name (PN)
    patient_name = "Test^Patient"
    patient_name_data = patient_name.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0010, 0x0010))  # (0010,0010) Patient Name
    dicom_data.extend(struct.pack('<B', len(patient_name_data)))  # Length of string
    dicom_data.extend(patient_name_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Patient ID (0010,0020) - Long String (LO)
    patient_id = "TEST123"
    patient_id_data = patient_id.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0010, 0x0020))  # (0010,0020) Patient ID
    dicom_data.extend(struct.pack('<B', len(patient_id_data)))  # Length of string
    dicom_data.extend(patient_id_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Study Instance UID (0020,000D) - Unique Identifier (UI)
    study_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    study_uid_data = study_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0020, 0x000D))  # (0020,000D) Study Instance UID
    dicom_data.extend(struct.pack('<B', len(study_uid_data)))  # Length of string
    dicom_data.extend(study_uid_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Series Instance UID (0020,000E) - Unique Identifier (UI)
    series_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.16"
    series_uid_data = series_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0020, 0x000E))  # (0020,000E) Series Instance UID
    dicom_data.extend(struct.pack('<B', len(series_uid_data)))  # Length of string
    dicom_data.extend(series_uid_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # SOP Instance UID (0008,0018) - Unique Identifier (UI)
    sop_uid = "1.2.3.4.5.6.7.8.9.10.11.12.13.14.15"
    sop_uid_data = sop_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0008, 0x0018))  # (0008,0018) SOP Instance UID
    dicom_data.extend(struct.pack('<B', len(sop_uid_data)))  # Length of string
    dicom_data.extend(sop_uid_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # SOP Class UID (0008,0016) - Unique Identifier (UI)
    sop_class_data_2 = sop_class_uid.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0008, 0x0016))  # (0008,0016) SOP Class UID
    dicom_data.extend(struct.pack('<B', len(sop_class_data_2)))  # Length of string
    dicom_data.extend(sop_class_data_2)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Modality (0008,0060) - Code String (CS)
    modality_data = modality.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0008, 0x0060))  # (0008,0060) Modality
    dicom_data.extend(struct.pack('<B', len(modality_data)))  # Length of string
    dicom_data.extend(modality_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Image specific tags
    if modality == "CT":
        # Image dimensions for CT
        dicom_data.extend(struct.pack('<HH', 0x0028, 0x0010))  # (0028,0010) Rows
        dicom_data.extend(struct.pack('<HH', 0x0028, 0x0010))  # (0028,0010) Rows
        dicom_data.extend(struct.pack('<H', 512))  # Value: 512
        dicom_data.extend(struct.pack('<HH', 0x0028, 0x0011))  # (0028,0011) Columns
        dicom_data.extend(struct.pack('<H', 512))  # Value: 512
    else:
        # Image dimensions for X-ray
        dicom_data.extend(struct.pack('<HH', 0x0028, 0x0010))  # (0028,0010) Rows
        dicom_data.extend(struct.pack('<H', 1024))  # Value: 1024
        dicom_data.extend(struct.pack('<HH', 0x0028, 0x0011))  # (0028,0011) Columns
        dicom_data.extend(struct.pack('<H', 1024))  # Value: 1024
    
    # Bits Allocated (0028,0100) - Unsigned Short (US)
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0100))  # (0028,0100) Bits Allocated
    dicom_data.extend(struct.pack('<H', 16))  # Value: 16
    
    # Bits Stored (0028,0101) - Unsigned Short (US)
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0101))  # (0028,0101) Bits Stored
    dicom_data.extend(struct.pack('<H', 16))  # Value: 16
    
    # High Bit (0028,0102) - Unsigned Short (US)
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0102))  # (0028,0102) High Bit
    dicom_data.extend(struct.pack('<H', 15))  # Value: 15
    
    # Pixel Representation (0028,0103) - Unsigned Short (US)
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0103))  # (0028,0103) Pixel Representation
    dicom_data.extend(struct.pack('<H', 0))  # Value: 0 (unsigned)
    
    # Samples Per Pixel (0028,0002) - Unsigned Short (US)
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0002))  # (0028,0002) Samples Per Pixel
    dicom_data.extend(struct.pack('<H', 1))  # Value: 1
    
    # Photometric Interpretation (0028,0004) - Code String (CS)
    photometric = "MONOCHROME2"
    photometric_data = photometric.encode('utf-8')
    dicom_data.extend(struct.pack('<HH', 0x0028, 0x0004))  # (0028,0004) Photometric Interpretation
    dicom_data.extend(struct.pack('<B', len(photometric_data)))  # Length of string
    dicom_data.extend(photometric_data)
    dicom_data.extend(struct.pack('<B', 0x00))  # NULL terminator
    
    # Add minimal pixel data (1KB of zeros)
    dicom_data.extend(b'\x00' * 1024)
    
    # Write the file
    with open(filename, 'wb') as f:
        f.write(dicom_data)
    
    print(f"Created {filename} ({len(dicom_data)} bytes)")

if __name__ == "__main__":
    # Create test_data directory if it doesn't exist
    os.makedirs("test_data", exist_ok=True)
    
    # Create sample CT file
    create_minimal_dicom_file("test_data/sample_ct.dcm", 
                             sop_class_uid="1.2.840.10008.5.1.4.1.1.2", 
                             modality="CT")
    
    # Create sample X-ray file
    create_minimal_dicom_file("test_data/sample_xray.dcm", 
                             sop_class_uid="1.2.840.10008.5.1.4.1.1.1", 
                             modality="CR")
    
    print("Sample DICOM files generated successfully!")