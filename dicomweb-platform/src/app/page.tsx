"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { 
  TestTube, 
  Play, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Download,
  Share2,
  Eye,
  EyeOff,
  Zap,
  Shield,
  BarChart3,
  Search,
  Upload
} from "lucide-react";

const testFormSchema = z.object({
  pacsUrl: z.string().url("Please enter a valid URL"),
  username: z.string().optional(),
  password: z.string().optional(),
  protocols: z.array(z.enum(["QIDO", "WADO", "STOW"])).min(1, "Select at least one protocol"),
  timeout: z.number().min(5).max(300),
  verbose: z.boolean(),
  isPublic: z.boolean(),
  organization: z.string().optional(),
  contactName: z.string().optional(),
  contactEmail: z.string().email().optional(),
});

type TestFormData = z.infer<typeof testFormSchema>;

export default function HomePage() {
  const [isRunning, setIsRunning] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<TestFormData>({
    resolver: zodResolver(testFormSchema),
    defaultValues: {
      protocols: ["QIDO", "WADO"],
      timeout: 30,
      verbose: false,
      isPublic: true, // Auto-check share results publicly
    },
  });

  const watchedProtocols = watch("protocols");

  const onSubmit = async (data: TestFormData) => {
    setIsRunning(true);
    
    try {
      // Start test execution via API
      const response = await fetch("/api/tests/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to start test");
      }

      const result = await response.json();
      
      // Poll for results
      pollForResults(result.testRunId);
    } catch (error) {
      console.error("Test failed:", error);
      alert("Test execution failed. Please check your PACS URL and try again.");
      setIsRunning(false);
    }
  };

  const pollForResults = async (testRunId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/tests/status/${testRunId}`);
        const result = await response.json();
        
        if (result.status === 'COMPLETED' || result.status === 'FAILED') {
          clearInterval(pollInterval);
          setTestResults(result);
          setShowResults(true);
          setIsRunning(false);
        }
      } catch (error) {
        console.error("Error polling for results:", error);
        clearInterval(pollInterval);
        setIsRunning(false);
        alert("Failed to get test results");
      }
    }, 2000);
  };

  const protocols = [
    {
      id: "QIDO" as const,
      name: "QIDO-RS",
      description: "Query operations for finding DICOM objects",
      tests: 24,
      icon: Search,
    },
    {
      id: "WADO" as const,
      name: "WADO-RS", 
      description: "Retrieve operations for downloading DICOM objects",
      tests: 18,
      icon: Download,
    },
    {
      id: "STOW" as const,
      name: "STOW-RS",
      description: "Store operations for uploading DICOM objects",
      tests: 12,
      icon: Upload,
    },
  ];

  if (showResults && testResults) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <TestResultsView results={testResults} onNewTest={() => setShowResults(false)} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg">
              <TestTube className="h-10 w-10 text-white" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            DICOMweb Test
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8">
            Test your PACS system for DICOM Part 18 compliance in minutes
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {/* PACS Endpoint Configuration */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                PACS System Configuration
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    PACS DICOMweb Endpoint URL *
                  </label>
                  <input
                    {...register("pacsUrl")}
                    type="url"
                    placeholder="https://your-pacs-server.com/dicomweb"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                  {errors.pacsUrl && (
                    <p className="mt-1 text-sm text-red-600">{errors.pacsUrl.message}</p>
                  )}
                  <p className="mt-1 text-sm text-gray-500">
                    The full URL to your PACS DICOMweb endpoint
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    {...register("username")}
                    type="text"
                    placeholder="pacs_user"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      {...register("password")}
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Protocol Selection */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Test Protocols
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {protocols.map((protocol) => (
                  <div
                    key={protocol.id}
                    className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
                      watchedProtocols.includes(protocol.id)
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                    onClick={() => {
                      const current = watchedProtocols;
                      const updated = current.includes(protocol.id)
                        ? current.filter((p) => p !== protocol.id)
                        : [...current, protocol.id];
                      // Would need to update form value here
                    }}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <protocol.icon className="h-8 w-8 text-blue-600" />
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={watchedProtocols.includes(protocol.id)}
                          onChange={() => {}}
                          className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {protocol.name}
                    </h3>
                    <p className="text-gray-600 text-sm mb-3">
                      {protocol.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">
                        {protocol.tests} tests
                      </span>
                      {watchedProtocols.includes(protocol.id) && (
                        <CheckCircle className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {errors.protocols && (
                <p className="mt-2 text-sm text-red-600">{errors.protocols.message}</p>
              )}
            </div>

            {/* Quick Options */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Options
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Timeout (seconds)
                  </label>
                  <input
                    {...register("timeout", { valueAsNumber: true })}
                    type="number"
                    min="5"
                    max="300"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      {...register("verbose")}
                      type="checkbox"
                      className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label className="ml-3 text-sm text-gray-700">
                      Verbose logging
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      {...register("isPublic")}
                      type="checkbox"
                      defaultChecked={true}
                      className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label className="ml-3 text-sm text-gray-700">
                      Share results publicly (for leaderboard)
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6">
              <button
                type="submit"
                disabled={isRunning}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-4 px-8 rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Running Tests...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Start DICOMweb Conformance Test</span>
                  </>
                )}
              </button>
              
              {!isRunning && (
                <p className="mt-3 text-sm text-gray-500 text-center">
                  Test will take approximately 2-5 minutes depending on your PACS response time
                </p>
              )}
            </div>
          </form>
        </div>

        {/* Quick Links */}
        <div className="mt-8 text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/results"
              className="inline-flex items-center px-6 py-3 bg-white hover:bg-gray-50 text-blue-600 font-semibold rounded-lg border-2 border-blue-600 shadow-lg transition-all duration-200"
            >
              <BarChart3 className="mr-2 h-5 w-5" />
              View Test Results
            </Link>
            <Link
              href="/leaderboard"
              className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg shadow-lg transition-all duration-200"
            >
              <CheckCircle className="mr-2 h-5 w-5" />
              Vendor Leaderboard
            </Link>
            <Link
              href="/about"
              className="inline-flex items-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg shadow-lg transition-all duration-200"
            >
              <Shield className="mr-2 h-5 w-5" />
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Test Results Component (same as before but compact)
function TestResultsView({ results, onNewTest }: { results: any; onNewTest: () => void }) {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl">
            <CheckCircle className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Test Complete
        </h1>
        <p className="text-xl text-gray-600">
          DICOMweb conformance assessment for {results.pacsUrl}
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {results.complianceScore}%
            </div>
            <div className="text-sm text-gray-600">Compliance Score</div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {results.passedTests}
            </div>
            <div className="text-sm text-gray-600">Tests Passed</div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">
              {results.failedTests}
            </div>
            <div className="text-sm text-gray-600">Tests Failed</div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-600 mb-2">
              {results.conformanceLevel}
            </div>
            <div className="text-sm text-gray-600">Conformance Level</div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">
          <Download className="mr-2 h-5 w-5" />
          Download PDF Report
        </button>
        <button
          onClick={onNewTest}
          className="inline-flex items-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg"
        >
          <Play className="mr-2 h-5 w-5" />
          Run New Test
        </button>
      </div>
    </div>
  );
}
