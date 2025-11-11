// Vendor Identification from HTTP Headers and Responses
// This system automatically detects PACS vendors based on HTTP response headers,
// server signatures, and other diagnostic information

interface VendorSignature {
  id: string;
  name: string;
  website: string;
  patterns: {
    server?: string[];
    headers?: { [key: string]: string[] };
    responsePatterns?: string[];
    userAgent?: string[];
  };
  commonEndpoints: string[];
  knownIssues?: string[];
  supportLevel: 'full' | 'partial' | 'limited';
}

interface VendorMatch {
  vendor: VendorSignature;
  confidence: number;
  matchedPatterns: string[];
  source: 'server' | 'headers' | 'response' | 'userAgent';
}

export class VendorIdentifier {
  private vendorSignatures: VendorSignature[] = [
    {
      id: 'agfa-healthcare',
      name: 'AGFA Healthcare',
      website: 'https://www.agfahealthcare.com',
      patterns: {
        server: ['Agfa', 'agfa', 'AGFA'],
        headers: {
          'x-agfa-version': ['*'],
          'x-server': ['agfa*', 'AGFA*']
        },
        responsePatterns: [
          'agfa',
          'healthcare',
          'Impax',
          'Enterprise'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      knownIssues: ['STOW-RS support varies by version'],
      supportLevel: 'partial'
    },
    {
      id: 'fujifilm',
      name: 'FUJIFILM Healthcare',
      website: 'https://www.fujifilm.com/healthcare',
      patterns: {
        server: ['Fujifilm', 'fujifilm', 'FUJIFILM'],
        headers: {
          'x-fuji-version': ['*'],
          'x-server': ['fujifilm*']
        },
        responsePatterns: [
          'fujifilm',
          'synapse',
          'pacs',
          'dicom'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'philips',
      name: 'Philips Healthcare',
      website: 'https://www.philips.com/healthcare',
      patterns: {
        server: ['Philips', 'philips', 'PHILIPS'],
        headers: {
          'x-philips-version': ['*'],
          'x-intellispace': ['*'],
          'x-server': ['philips*']
        },
        responsePatterns: [
          'philips',
          'intellispace',
          'pacs',
          'dicom'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'ge-healthcare',
      name: 'GE Healthcare',
      website: 'https://www.gehealthcare.com',
      patterns: {
        server: ['GE', 'ge', 'GE-Healthcare', 'Centricity'],
        headers: {
          'x-ge-version': ['*'],
          'x-centricity': ['*'],
          'x-server': ['ge*', 'centricity*']
        },
        responsePatterns: [
          'ge',
          'centricity',
          'healthcare',
          'pacs'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'partial'
    },
    {
      id: 'siemens-healthineers',
      name: 'Siemens Healthineers',
      website: 'https://www.siemens-healthineers.com',
      patterns: {
        server: ['Siemens', 'siemens', 'Healthineers'],
        headers: {
          'x-siemens-version': ['*'],
          'x-server': ['siemens*']
        },
        responsePatterns: [
          'siemens',
          'healthineers',
          'syngo',
          'pacs'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'partial'
    },
    {
      id: 'carestream',
      name: 'Carestream Health',
      website: 'https://www.carestream.com',
      patterns: {
        server: ['Carestream', 'carestream', 'CARESTREAM'],
        headers: {
          'x-carestream-version': ['*'],
          'x-server': ['carestream*']
        },
        responsePatterns: [
          'carestream',
          'pacs',
          'vue'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'partial'
    },
    {
      id: 'sectra',
      name: 'Sectra AB',
      website: 'https://www.sectra.com',
      patterns: {
        server: ['Sectra', 'sectra', 'SECTRA'],
        headers: {
          'x-sectra-version': ['*'],
          'x-server': ['sectra*']
        },
        responsePatterns: [
          'sectra',
          'pacs',
          'radiology'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'nucleus',
      name: 'Nucleus Health',
      website: 'https://www.nucleushealth.com',
      patterns: {
        server: ['Nucleus', 'nucleus', 'NUCLEUS'],
        headers: {
          'x-nucleus-version': ['*'],
          'x-server': ['nucleus*']
        },
        responsePatterns: [
          'nucleus',
          'radcloud',
          'pacs'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'partial'
    },
    {
      id: 'dcm4chee',
      name: 'dcm4chee PACS',
      website: 'https://www.dcm4che.org',
      patterns: {
        server: ['dcm4chee', 'DCM4CHEE', 'dcm4che'],
        headers: {
          'x-dcm4chee-version': ['*'],
          'x-server': ['dcm4chee*']
        },
        responsePatterns: [
          'dcm4chee',
          'dcm4che',
          'jboss'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'orthanc',
      name: 'Orthanc DICOM Server',
      website: 'https://www.orthanc-server.com',
      patterns: {
        server: ['Orthanc', 'orthanc', 'ORTHANC'],
        headers: {
          'x-orthanc-version': ['*'],
          'x-server': ['orthanc*']
        },
        responsePatterns: [
          'orthanc',
          'dicom',
          'server'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'dicomserver',
      name: 'DICOM Server (DCMTK)',
      website: 'https://dicom.offis.de',
      patterns: {
        server: ['DCMTK', 'dcmtk', 'dicomserver'],
        headers: {
          'x-dcmtk-version': ['*'],
          'x-server': ['dcmtk*']
        },
        responsePatterns: [
          'dcmtk',
          'dicom',
          'server'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'full'
    },
    {
      id: 'com.pixelmed',
      name: 'PixelMed DICOM Toolkit',
      website: 'https://www.pixelmed.com',
      patterns: {
        server: ['PixelMed', 'pixelmed', 'PIXELMED'],
        headers: {
          'x-pixelmed-version': ['*'],
          'x-server': ['pixelmed*']
        },
        responsePatterns: [
          'pixelmed',
          'dicom'
        ]
      },
      commonEndpoints: ['/dicomweb', '/wado', '/rs'],
      supportLevel: 'partial'
    }
  ];

  /**
   * Identify vendor from HTTP response data
   */
  public async identifyVendor(
    url: string, 
    response?: {
      headers?: { [key: string]: string };
      server?: string;
      statusCode?: number;
      responseTime?: number;
    }
  ): Promise<VendorMatch[]> {
    const matches: VendorMatch[] = [];

    if (!response) {
      return matches;
    }

    // Check each vendor signature
    for (const vendor of this.vendorSignatures) {
      const vendorMatches = await this.checkVendor(vendor, response);
      matches.push(...vendorMatches);
    }

    // Sort by confidence
    return matches.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Check a specific vendor against response data
   */
  private async checkVendor(
    vendor: VendorSignature, 
    response: {
      headers?: { [key: string]: string };
      server?: string;
      statusCode?: number;
      responseTime?: number;
    }
  ): Promise<VendorMatch[]> {
    const matches: VendorMatch[] = [];
    let totalConfidence = 0;
    const matchedPatterns: string[] = [];

    // Check Server header
    if (response.server && vendor.patterns.server) {
      for (const pattern of vendor.patterns.server) {
        if (response.server.toLowerCase().includes(pattern.toLowerCase())) {
          totalConfidence += 30;
          matchedPatterns.push(`server:${pattern}`);
        }
      }
    }

    // Check custom headers
    if (response.headers && vendor.patterns.headers) {
      for (const [headerName, patterns] of Object.entries(vendor.patterns.headers)) {
        const headerValue = response.headers[headerName.toLowerCase()];
        if (headerValue) {
          for (const pattern of patterns) {
            if (pattern === '*' || headerValue.toLowerCase().includes(pattern.toLowerCase())) {
              totalConfidence += 25;
              matchedPatterns.push(`header:${headerName}:${pattern}`);
            }
          }
        }
      }
    }

    // Check User-Agent
    if (response.headers && vendor.patterns.userAgent) {
      const userAgent = response.headers['user-agent'];
      if (userAgent) {
        for (const pattern of vendor.patterns.userAgent) {
          if (userAgent.toLowerCase().includes(pattern.toLowerCase())) {
            totalConfidence += 20;
            matchedPatterns.push(`userAgent:${pattern}`);
          }
        }
      }
    }

    // Only create match if we found significant patterns
    if (totalConfidence > 0) {
      const confidence = Math.min(totalConfidence, 100); // Cap at 100%
      matches.push({
        vendor,
        confidence,
        matchedPatterns,
        source: response.server ? 'server' : 'headers'
      });
    }

    return matches;
  }

  /**
   * Get vendor by ID
   */
  public getVendorById(id: string): VendorSignature | null {
    return this.vendorSignatures.find(v => v.id === id) || null;
  }

  /**
   * Get all vendors
   */
  public getAllVendors(): VendorSignature[] {
    return this.vendorSignatures;
  }

  /**
   * Get vendor recommendations based on test results
   */
  public getVendorRecommendations(vendor: VendorSignature, testResults: any[]): string[] {
    const recommendations: string[] = [];

    if (vendor.knownIssues && vendor.knownIssues.length > 0) {
      recommendations.push(`Known issues: ${vendor.knownIssues.join(', ')}`);
    }

    if (vendor.supportLevel === 'partial') {
      recommendations.push('This vendor has partial DICOMweb support - some features may not work as expected.');
    }

    // Add specific recommendations based on test results
    const failedTests = testResults.filter(test => test.status === 'FAIL');
    if (failedTests.length > 0) {
      const stowFailures = failedTests.filter(test => test.protocol === 'STOW');
      if (stowFailures.length > 0) {
        recommendations.push('STOW-RS failures detected - this vendor may have limited store support.');
      }

      const qidoFailures = failedTests.filter(test => test.protocol === 'QIDO');
      if (qidoFailures.length > 0) {
        recommendations.push('QIDO-RS failures detected - query functionality may be limited.');
      }

      const wadoFailures = failedTests.filter(test => test.protocol === 'WADO');
      if (wadoFailures.length > 0) {
        recommendations.push('WADO-RS failures detected - retrieval functionality may be limited.');
      }
    }

    return recommendations;
  }

  /**
   * Add custom vendor signature
   */
  public addCustomVendor(vendor: VendorSignature): void {
    this.vendorSignatures.push(vendor);
  }

  /**
   * Update vendor signature
   */
  public updateVendor(id: string, updates: Partial<VendorSignature>): boolean {
    const index = this.vendorSignatures.findIndex(v => v.id === id);
    if (index !== -1) {
      this.vendorSignatures[index] = { ...this.vendorSignatures[index], ...updates };
      return true;
    }
    return false;
  }
}

// Export singleton instance
export const vendorIdentifier = new VendorIdentifier();

// Export interface for use in other modules
export type { VendorMatch };