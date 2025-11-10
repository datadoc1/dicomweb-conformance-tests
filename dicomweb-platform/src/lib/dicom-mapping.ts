import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

export interface DicomTestMapping {
  [testId: string]: {
    test_name: string;
    protocol: 'QIDO' | 'WADO' | 'STOW';
    dicom_section: string;
    requirement: 'SHALL' | 'SHOULD' | 'MAY';
    classification: 'mandatory' | 'recommended' | 'optional';
    description: string;
    test_type: 'basic' | 'optional' | 'advanced';
    performance_critical: boolean;
  };
}

export interface DicomMappingData {
  version: string;
  last_updated: string;
  standard_reference: string;
  tests: DicomTestMapping;
  protocol_summaries: {
    [protocol: string]: {
      total_tests: number;
      mandatory_tests: number;
      recommended_tests: number;
      optional_tests: number;
      critical_sections: string[];
    };
  };
}

let cachedMapping: DicomMappingData | null = null;

export function loadDicomMapping(): DicomMappingData {
  if (cachedMapping) {
    return cachedMapping;
  }

  try {
    // Try to load from the generated DICOM mapping file
    const mappingPath = join(process.cwd(), '../../DICOM_CONFORMANCE_MAPPING.json');
    
    if (existsSync(mappingPath)) {
      const mappingData = readFileSync(mappingPath, 'utf8');
      cachedMapping = JSON.parse(mappingData);
      return cachedMapping!;
    }
  } catch (error) {
    console.warn('Failed to load DICOM mapping from file:', error);
  }

  // Fallback to embedded mapping if file doesn't exist
  cachedMapping = getEmbeddedMapping();
  return cachedMapping;
}

function getEmbeddedMapping(): DicomMappingData {
  return {
    version: "1.0.0",
    last_updated: "2025-11-10",
    standard_reference: "DICOM Part 18 (PS3.18) - DICOM Web Services",
    tests: {
      "QIDO_001": {
        test_name: "QIDO-RS Studies Endpoint",
        protocol: "QIDO",
        dicom_section: "6.2.1",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support QIDO-RS query operations at the Studies level",
        test_type: "basic",
        performance_critical: true
      },
      "QIDO_002": {
        test_name: "QIDO-RS Series Endpoint",
        protocol: "QIDO",
        dicom_section: "6.2.2",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support QIDO-RS query operations at the Series level",
        test_type: "basic",
        performance_critical: true
      },
      "QIDO_003": {
        test_name: "QIDO-RS Instances Endpoint",
        protocol: "QIDO",
        dicom_section: "6.2.3",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support QIDO-RS query operations at the Instances level",
        test_type: "basic",
        performance_critical: true
      },
      "QIDO_004": {
        test_name: "QIDO-RS Query Parameters",
        protocol: "QIDO",
        dicom_section: "6.2.4",
        requirement: "SHOULD",
        classification: "recommended",
        description: "The server SHOULD support common DICOM query parameters",
        test_type: "basic",
        performance_critical: false
      },
      "QIDO_005": {
        test_name: "QIDO-RS Response Format",
        protocol: "QIDO",
        dicom_section: "6.2.5",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL return DICOM data in application/dicom+json format",
        test_type: "basic",
        performance_critical: false
      },
      "WADO_001": {
        test_name: "WADO-RS Retrieve Metadata",
        protocol: "WADO",
        dicom_section: "6.3.1",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support WADO-RS metadata retrieval",
        test_type: "basic",
        performance_critical: true
      },
      "WADO_002": {
        test_name: "WADO-RS Retrieve Instances",
        protocol: "WADO",
        dicom_section: "6.3.2",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support WADO-RS DICOM instance retrieval",
        test_type: "basic",
        performance_critical: true
      },
      "WADO_003": {
        test_name: "WADO-RS Retrieve Frames",
        protocol: "WADO",
        dicom_section: "6.3.3",
        requirement: "SHOULD",
        classification: "recommended",
        description: "The server SHOULD support WADO-RS frame retrieval for multi-frame images",
        test_type: "optional",
        performance_critical: false
      },
      "WADO_004": {
        test_name: "WADO-RS Accept Headers",
        protocol: "WADO",
        dicom_section: "6.3.4",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL handle proper Accept headers for DICOM content",
        test_type: "basic",
        performance_critical: false
      },
      "STOW_001": {
        test_name: "STOW-RS Store Studies",
        protocol: "STOW",
        dicom_section: "6.4.1",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL support STOW-RS study storage operations",
        test_type: "basic",
        performance_critical: true
      },
      "STOW_002": {
        test_name: "STOW-RS Content-Type Validation",
        protocol: "STOW",
        dicom_section: "6.4.2",
        requirement: "SHALL",
        classification: "mandatory",
        description: "The server SHALL validate Content-Type headers for DICOM data",
        test_type: "basic",
        performance_critical: false
      },
      "STOW_003": {
        test_name: "STOW-RS Multiple Instances",
        protocol: "STOW",
        dicom_section: "6.4.3",
        requirement: "SHOULD",
        classification: "recommended",
        description: "The server SHOULD support storing multiple DICOM instances in a single request",
        test_type: "basic",
        performance_critical: false
      },
      "STOW_004": {
        test_name: "STOW-RS Large File Handling",
        protocol: "STOW",
        dicom_section: "6.4.4",
        requirement: "SHOULD",
        classification: "recommended",
        description: "The server SHOULD handle large DICOM files efficiently",
        test_type: "advanced",
        performance_critical: true
      }
    },
    protocol_summaries: {
      "QIDO": {
        total_tests: 5,
        mandatory_tests: 3,
        recommended_tests: 2,
        optional_tests: 0,
        critical_sections: ["6.2.1", "6.2.2", "6.2.3"]
      },
      "WADO": {
        total_tests: 4,
        mandatory_tests: 2,
        recommended_tests: 2,
        optional_tests: 0,
        critical_sections: ["6.3.1", "6.3.2"]
      },
      "STOW": {
        total_tests: 4,
        mandatory_tests: 2,
        recommended_tests: 2,
        optional_tests: 0,
        critical_sections: ["6.4.1", "6.4.2"]
      }
    }
  };
}

export function getTestClassification(testId: string): {
  requirement: 'SHALL' | 'SHOULD' | 'MAY';
  classification: 'mandatory' | 'recommended' | 'optional';
  isCritical: boolean;
} {
  const mapping = loadDicomMapping();
  const test = mapping.tests[testId];
  
  if (!test) {
    return {
      requirement: 'SHOULD',
      classification: 'recommended',
      isCritical: false
    };
  }
  
  return {
    requirement: test.requirement,
    classification: test.classification,
    isCritical: test.performance_critical
  };
}

export function getProtocolRequirements(protocol: 'QIDO' | 'WADO' | 'STOW') {
  const mapping = loadDicomMapping();
  return mapping.protocol_summaries[protocol];
}

export function getMandatoryTests(protocol?: 'QIDO' | 'WADO' | 'STOW'): string[] {
  const mapping = loadDicomMapping();
  const tests = Object.entries(mapping.tests);
  
  return tests
    .filter(([_, test]) => {
      if (protocol && test.protocol !== protocol) return false;
      return test.requirement === 'SHALL';
    })
    .map(([testId, _]) => testId);
}