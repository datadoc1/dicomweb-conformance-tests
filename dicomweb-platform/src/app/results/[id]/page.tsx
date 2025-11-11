"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { createClient } from "@supabase/supabase-js";
import { 
  Download, 
  FileText, 
  Mail, 
  Share2, 
  BarChart3, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  Calendar,
  Globe,
  Server,
  User,
  Building,
  ExternalLink,
  Trophy
} from "lucide-react";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface TestResult {
  id: string;
  pacsUrl: string;
  status: string;
  startTime: string;
  endTime: string;
  complianceScore: number;
  passedTests: number;
  failedTests: number;
  totalTests: number;
  conformanceLevel: string;
  averageResponseTime: number;
  totalDuration: number;
  organization?: string;
  contactName?: string;
  contactEmail?: string;
  testResults: Array<{
    testName: string;
    protocol: string;
    status: string;
    message: string;
    timestamp: string;
  }>;
  vendorInfo?: {
    name: string;
    website?: string;
  };
}

export default function TestResultPage() {
  const params = useParams();
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTestResult();
  }, [params.id]);

  const fetchTestResult = async () => {
    try {
      setLoading(true);
      
      // Try to fetch from Supabase first
      const { data, error } = await supabase
        .from('test_runs')
        .select(`
          *,
          test_results:test_results (
            test_name,
            protocol,
            status,
            message,
            timestamp
          )
        `)
        .eq('id', params.id)
        .single();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      if (data) {
        setTestResult(data);
      } else {
        // Fallback to mock data for development
        setTestResult(getMockTestResult(params.id as string));
      }
    } catch (err) {
      console.error('Error fetching test result:', err);
      setError('Failed to load test result');
    } finally {
      setLoading(false);
    }
  };

  const getMockTestResult = (id: string): TestResult => {
    return {
      id,
      pacsUrl: `https://pacs.example${id}.com/dicomweb`,
      status: 'COMPLETED',
      startTime: new Date(Date.now() - 180000).toISOString(),
      endTime: new Date().toISOString(),
      complianceScore: 87.5,
      passedTests: 42,
      failedTests: 6,
      totalTests: 48,
      conformanceLevel: 'GOOD',
      averageResponseTime: 1.23,
      totalDuration: 180,
      organization: 'Sample Hospital',
      contactName: 'Dr. John Doe',
      contactEmail: 'john.doe@hospital.com',
      testResults: [
        {
          testName: 'QIDO-RS Query Studies',
          protocol: 'QIDO',
          status: 'PASS',
          message: 'Successfully retrieved study list',
          timestamp: new Date().toISOString()
        },
        {
          testName: 'WADO-RS Retrieve Instance',
          protocol: 'WADO',
          status: 'PASS',
          message: 'DICOM instance retrieved successfully',
          timestamp: new Date().toISOString()
        },
        {
          testName: 'STOW-RS Store Series',
          protocol: 'STOW',
          status: 'FAIL',
          message: 'Failed to store DICOM series: HTTP 500',
          timestamp: new Date().toISOString()
        }
      ],
      vendorInfo: {
        name: 'Example PACS Vendor',
        website: 'https://vendor.com'
      }
    };
  };

  const handleDownloadPDF = async () => {
    if (!testResult) return;
    
    try {
      // Generate PDF using a library like jsPDF
      const { jsPDF } = await import('jspdf');
      const pdf = new jsPDF();
      
      // Add content to PDF
      pdf.setFontSize(20);
      pdf.text('DICOMweb Conformance Test Report', 20, 30);
      
      pdf.setFontSize(12);
      pdf.text(`PACS URL: ${testResult.pacsUrl}`, 20, 50);
      pdf.text(`Test Date: ${new Date(testResult.startTime).toLocaleDateString()}`, 20, 60);
      pdf.text(`Compliance Score: ${testResult.complianceScore}%`, 20, 70);
      pdf.text(`Conformance Level: ${testResult.conformanceLevel}`, 20, 80);
      pdf.text(`Tests Passed: ${testResult.passedTests}/${testResult.totalTests}`, 20, 90);
      
      // Add test results
      let yPos = 110;
      pdf.text('Test Results:', 20, yPos);
      yPos += 10;
      
      testResult.testResults.slice(0, 20).forEach((result) => {
        pdf.text(`• ${result.testName}: ${result.status}`, 25, yPos);
        yPos += 8;
      });
      
      pdf.save(`dicomweb-test-report-${testResult.id}.pdf`);
    } catch (err) {
      console.error('Error generating PDF:', err);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  const handleDownloadJSON = async () => {
    if (!testResult) return;
    
    const jsonData = {
      testResult,
      generatedAt: new Date().toISOString(),
      tool: 'DICOMweb Conformance Test Suite',
      version: '1.0.0'
    };
    
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dicomweb-test-results-${testResult.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleGenerateEmail = () => {
    if (!testResult) return;
    
    const subject = encodeURIComponent(`DICOMweb Compliance Assessment Results for ${testResult.pacsUrl}`);
    const body = encodeURIComponent(`
Dear ${testResult.vendorInfo?.name || '[PACS Vendor Name]'},

I hope this message finds you well. I am writing to share the results of a comprehensive DICOMweb compliance assessment conducted on ${new Date(testResult.startTime).toLocaleDateString()} for our PACS system at ${testResult.pacsUrl}.

## Assessment Overview

We recently conducted a thorough evaluation of our PACS system's DICOMweb implementation using industry-standard testing tools. This assessment evaluated all three core DICOMweb protocols:

• QIDO-RS (Query Based on ID with RESTful Services)
• WADO-RS (Web Access to DICOM Objects via RESTful Services)  
• STOW-RS (Store Over The Web with RESTful Services)

## Key Findings

**Overall Compliance Score:** ${testResult.complianceScore}%
**Conformance Level:** ${testResult.conformanceLevel}

Our assessment identified several areas where your DICOMweb implementation excels, as well as some opportunities for improvement to ensure full compliance with DICOMweb standards.

## Business Impact

DICOMweb compliance is increasingly important for:
• Interoperability with modern healthcare systems
• Integration with AI/ML imaging workflows
• Meeting regulatory and security requirements
• Supporting telemedicine and remote diagnostics
• Enabling research collaborations and data sharing

We value our partnership and look forward to working together to ensure our PACS system meets the highest standards for DICOMweb compliance.

Please direct your response to:
${testResult.contactName || '[Your Name]'}
${testResult.organization || '[Your Organization]'}
${testResult.contactEmail || '[Your Email]'}

Thank you for your continued support.

Best regards,
${testResult.contactName || '[Your Name]'}
${testResult.organization || '[Your Organization]'}
    `);
    
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  const handleShare = () => {
    if (!testResult) return;
    
    const shareData = {
      title: `DICOMweb Test Results - ${testResult.complianceScore}% Compliance`,
      text: `PACS: ${testResult.pacsUrl} scored ${testResult.complianceScore}% compliance in DICOMweb testing. ${testResult.passedTests}/${testResult.totalTests} tests passed.`,
      url: window.location.href
    };
    
    if (navigator.share) {
      navigator.share(shareData);
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('Test result link copied to clipboard!');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASS':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'FAIL':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'SKIP':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PASS':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'FAIL':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'SKIP':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test results...</p>
        </div>
      </div>
    );
  }

  if (error || !testResult) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Test Result Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The requested test result could not be found.'}</p>
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
          >
            <BarChart3 className="mr-2 h-5 w-5" />
            Start New Test
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl">
              <Trophy className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Test Complete
          </h1>
          <p className="text-xl text-gray-600">
            DICOMweb conformance assessment for {testResult.pacsUrl}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {testResult.complianceScore}%
            </div>
            <div className="text-sm text-gray-600">Compliance Score</div>
            <div className="text-xs text-gray-500 mt-1">
              {testResult.conformanceLevel} Conformance
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {testResult.passedTests}
            </div>
            <div className="text-sm text-gray-600">Tests Passed</div>
            <div className="text-xs text-gray-500 mt-1">
              of {testResult.totalTests} total
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">
              {testResult.failedTests}
            </div>
            <div className="text-sm text-gray-600">Tests Failed</div>
            <div className="text-xs text-gray-500 mt-1">
              Need attention
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-3xl font-bold text-gray-600 mb-2">
              {testResult.totalDuration}s
            </div>
            <div className="text-sm text-gray-600">Test Duration</div>
            <div className="text-xs text-gray-500 mt-1">
              {testResult.averageResponseTime.toFixed(1)}s avg response
            </div>
          </div>
        </div>

        {/* Test Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Test Details */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Details</h2>
            <div className="space-y-3">
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <div className="text-sm text-gray-600">PACS URL</div>
                  <div className="font-medium">{testResult.pacsUrl}</div>
                </div>
              </div>
              
              {testResult.vendorInfo && (
                <div className="flex items-center">
                  <Server className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600">Vendor</div>
                    <div className="font-medium">{testResult.vendorInfo.name}</div>
                  </div>
                </div>
              )}
              
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <div className="text-sm text-gray-600">Test Date</div>
                  <div className="font-medium">
                    {new Date(testResult.startTime).toLocaleString()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <div className="text-sm text-gray-600">Duration</div>
                  <div className="font-medium">
                    {Math.floor(testResult.totalDuration / 60)}m {testResult.totalDuration % 60}s
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-3">
              {testResult.organization && (
                <div className="flex items-center">
                  <Building className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600">Organization</div>
                    <div className="font-medium">{testResult.organization}</div>
                  </div>
                </div>
              )}
              
              {testResult.contactName && (
                <div className="flex items-center">
                  <User className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600">Contact</div>
                    <div className="font-medium">{testResult.contactName}</div>
                  </div>
                </div>
              )}
              
              {testResult.contactEmail && (
                <div className="flex items-center">
                  <Mail className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600">Email</div>
                    <div className="font-medium">{testResult.contactEmail}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Test Results */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Test Results Details</h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {testResult.testResults.map((result, index) => (
              <div key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(result.status)}
                      <h3 className="text-lg font-medium text-gray-900">
                        {result.testName}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(result.status)}`}>
                        {result.protocol}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mb-2">
                      {result.message}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(result.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleDownloadPDF}
            className="inline-flex items-center px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg"
          >
            <Download className="mr-2 h-5 w-5" />
            Download PDF Report
          </button>
          
          <button
            onClick={handleDownloadJSON}
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
          >
            <FileText className="mr-2 h-5 w-5" />
            Download JSON Data
          </button>
          
          <button
            onClick={handleGenerateEmail}
            className="inline-flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg"
          >
            <Mail className="mr-2 h-5 w-5" />
            Generate Vendor Email
          </button>
          
          <button
            onClick={handleShare}
            className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg"
          >
            <Share2 className="mr-2 h-5 w-5" />
            Share Results
          </button>
        </div>

        {/* Navigation */}
        <div className="mt-8 text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
            >
              <BarChart3 className="mr-2 h-5 w-5" />
              Run New Test
            </Link>
            <Link
              href="/results"
              className="inline-flex items-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg"
            >
              <Globe className="mr-2 h-5 w-5" />
              View Other Results
            </Link>
            <Link
              href="/leaderboard"
              className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg"
            >
              <Trophy className="mr-2 h-5 w-5" />
              Vendor Leaderboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}