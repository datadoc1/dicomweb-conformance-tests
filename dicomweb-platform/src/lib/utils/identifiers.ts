import { format } from 'date-fns';

export function generateTestIdentifier(): string {
  const now = new Date();
  const dateStr = format(now, 'yyyyMMdd_HHmmss');
  const randomStr = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `DICOM_${dateStr}_${randomStr}`;
}

export function generateShareToken(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export function parsePacsVendor(pacsUrl: string, pacsName?: string): string {
  // Try to extract vendor from URL patterns
  if (pacsName) {
    const vendorPatterns = [
      { pattern: /agfa/i, vendor: 'AGFA' },
      { pattern: /fuji/i, vendor: 'FUJI' },
      { pattern: /philips/i, vendor: 'Philips' },
      { pattern: /ge\s*healthcare|ge\s*medical/i, vendor: 'GE Healthcare' },
      { pattern: /siemens/i, vendor: 'Siemens Healthineers' },
      { pattern: /carestream/i, vendor: 'Carestream' },
      { pattern: /idexx/i, vendor: 'IDEXX' },
      { pattern: /orthanc/i, vendor: 'Orthanc' },
    ];
    
    for (const { pattern, vendor } of vendorPatterns) {
      if (pattern.test(pacsName)) {
        return vendor;
      }
    }
  }
  
  // Try to extract from URL
  const urlPatterns = [
    { pattern: /agfa/i, vendor: 'AGFA' },
    { pattern: /fuji/i, vendor: 'FUJI' },
    { pattern: /philips/i, vendor: 'Philips' },
    { pattern: /ge/i, vendor: 'GE Healthcare' },
    { pattern: /siemens/i, vendor: 'Siemens Healthineers' },
    { pattern: /carestream/i, vendor: 'Carestream' },
    { pattern: /orthanc/i, vendor: 'Orthanc' },
  ];
  
  for (const { pattern, vendor } of urlPatterns) {
    if (pattern.test(pacsUrl)) {
      return vendor;
    }
  }
  
  return 'Unknown Vendor';
}