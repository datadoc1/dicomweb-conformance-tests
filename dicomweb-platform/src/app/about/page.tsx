import Link from "next/link";
import { 
  Heart, 
  Shield, 
  BarChart3, 
  TestTube, 
  Users, 
  Trophy, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  ExternalLink,
  ArrowRight,
  Star,
  Zap,
  Globe
} from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                <Heart className="h-10 w-10 text-white" />
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Break PACS Vendor Lock-in
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto">
              Professional DICOMweb compliance testing platform. Test your PACS system, 
              compare vendors, and hold them accountable with objective conformance data.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/"
                className="inline-flex items-center px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105"
              >
                <TestTube className="mr-2 h-5 w-5" />
                Test Your PACS Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="/leaderboard"
                className="inline-flex items-center px-8 py-4 bg-white hover:bg-gray-50 text-blue-600 font-semibold rounded-lg border-2 border-blue-600 shadow-lg transition-all duration-200 hover:shadow-xl"
              >
                <Trophy className="mr-2 h-5 w-5" />
                View Leaderboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              The Healthcare Interoperability Crisis
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Modern healthcare depends on DICOMweb compliance, yet many PACS systems 
              are non-compliant, creating serious operational and financial problems.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <AlertTriangle className="h-8 w-8 text-red-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Integration Failures
              </h3>
              <p className="text-gray-600">
                Modern healthcare systems can't communicate with your non-compliant PACS, 
                creating expensive workarounds and manual processes.
              </p>
            </div>

            <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
              <Zap className="h-8 w-8 text-orange-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI/ML Roadblocks
              </h3>
              <p className="text-gray-600">
                Advanced imaging AI tools require DICOMweb access. Non-compliant PACS 
                systems block the future of medical imaging.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <Globe className="h-8 w-8 text-blue-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Telemedicine Gaps
              </h3>
              <p className="text-gray-600">
                Remote diagnostic capabilities are limited when your PACS doesn't support 
                modern web-based image access standards.
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <Shield className="h-8 w-8 text-yellow-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Security Vulnerabilities
              </h3>
              <p className="text-gray-600">
                Non-compliant systems are harder to secure and maintain, creating 
                regulatory and cybersecurity risks.
              </p>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <TrendingUp className="h-8 w-8 text-purple-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Hidden Costs
              </h3>
              <p className="text-gray-600">
                Manual workarounds and custom integrations cost hospitals millions 
                annually in development and maintenance.
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <Users className="h-8 w-8 text-green-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Regulatory Risks
              </h3>
              <p className="text-gray-600">
                Increasing regulatory requirements mandate interoperability. 
                Non-compliant systems put you at risk.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Solution */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Our Solution: Objective DICOMweb Testing
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We provide unshakeable credibility through DICOM Part 18 standard mapping, 
              making vendor excuses impossible.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="space-y-8">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Shield className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Unshakeable Credibility
                    </h3>
                    <p className="text-gray-600">
                      Every test maps to DICOM Part 18 (PS3.18) with explicit classification 
                      of MANDATORY, RECOMMENDED, or OPTIONAL requirements.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <BarChart3 className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Performance Baselines
                    </h3>
                    <p className="text-gray-600">
                      Measure response latency, throughput, and reliability. 
                      A PACS that replies in 5 seconds is "technically compliant" but useless for clinical integration.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Users className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Community Pressure
                    </h3>
                    <p className="text-gray-600">
                      Public leaderboard and viral sharing infrastructure creates 
                      community-driven vendor accountability.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <Zap className="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Zero-Friction Testing
                    </h3>
                    <p className="text-gray-600">
                      Web dashboard allows PACS admins to test with just a URL and 
                      credentials. No installation, no complexity.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                Sample Test Report
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-medium">QIDO-RS Studies Endpoint</span>
                  </div>
                  <span className="text-green-600 font-semibold">PASS</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-medium">WADO-RS Metadata</span>
                  </div>
                  <span className="text-green-600 font-semibold">PASS</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    <span className="font-medium">STOW-RS Store</span>
                  </div>
                  <span className="text-red-600 font-semibold">FAIL</span>
                </div>
              </div>
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Overall Compliance</span>
                  <span className="text-2xl font-bold text-blue-600">76%</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Reference: DICOM Part 18, Section 6.7 (STOW-RS Requirements)
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Success Stories */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Real Impact Stories
            </h2>
            <p className="text-xl text-gray-600">
              Healthcare organizations breaking vendor lock-in through objective testing
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-8 border border-blue-100">
              <div className="flex items-center mb-4">
                <div className="flex -space-x-2">
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                </div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "We discovered our $2M PACS system was only 60% DICOMweb compliant. 
                The test results gave us the leverage we needed to get the vendor to fix 
                the issues during our support contract renewal."
              </blockquote>
              <div className="text-sm font-semibold text-gray-900">
                - Hospital IT Director
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-8 border border-green-100">
              <div className="flex items-center mb-4">
                <div className="flex -space-x-2">
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                </div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "The automated vendor email template saved us weeks of work. We sent 
                the test results to our PACS vendor and they scheduled an emergency 
                patch within 48 hours."
              </blockquote>
              <div className="text-sm font-semibold text-gray-900">
                - PACS Administrator
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-8 border border-purple-100">
              <div className="flex items-center mb-4">
                <div className="flex -space-x-2">
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                  <Star className="h-5 w-5 text-yellow-400 fill-current" />
                </div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "Before deploying AI diagnostic tools, we ran these tests and discovered 
                our PACS couldn't handle the DICOMweb load. We upgraded to a compliant 
                system and avoided a costly project failure."
              </blockquote>
              <div className="text-sm font-semibold text-gray-900">
                - Healthcare IT Consultant
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Three steps to break vendor lock-in and get objective compliance data
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Test Your PACS
              </h3>
              <p className="text-gray-600">
                Enter your PACS DICOMweb endpoint URL and credentials. Our tests run 
                against all three DICOMweb protocols (QIDO, WADO, STOW) in minutes.
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full">
                  <span className="text-2xl font-bold text-purple-600">2</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Get Professional Reports
              </h3>
              <p className="text-gray-600">
                Receive detailed PDF reports with specific DICOM Part 18 violations, 
                performance metrics, and vendor-ready recommendations.
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
                  <span className="text-2xl font-bold text-green-600">3</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Share & Hold Vendors Accountable
              </h3>
              <p className="text-gray-600">
                Share results on the leaderboard, social media, and with your vendor. 
                Generate one-click reports that force accountability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Break Vendor Lock-in?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Start testing your PACS system today and get objective data to hold 
            vendors accountable for their DICOMweb compliance claims.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="inline-flex items-center px-8 py-4 bg-white hover:bg-gray-50 text-blue-600 font-semibold rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl"
            >
              <TestTube className="mr-2 h-5 w-5" />
              Start Free Test
            </Link>
            <Link
              href="/leaderboard"
              className="inline-flex items-center px-8 py-4 bg-blue-700 hover:bg-blue-800 text-white font-semibold rounded-lg border-2 border-white shadow-lg transition-all duration-200 hover:shadow-xl"
            >
              <Trophy className="mr-2 h-5 w-5" />
              View Leaderboard
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}