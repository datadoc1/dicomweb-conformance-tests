import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Download,
  Share2,
  ExternalLink,
  Calendar,
  BarChart3,
  TrendingUp,
  Trophy,
  Users,
  Target,
  Medal
} from 'lucide-react';
import Link from 'next/link';

export default async function ResultsPage() {
  // Get recent public test results
  const recentResults = await prisma.testRun.findMany({
    where: {
      isPublic: true,
      status: 'COMPLETED',
    },
    include: {
      pacs: {
        include: {
          vendor: true
        }
      },
      testResults: {
        take: 10, // Limit for preview
        orderBy: {
          timestamp: 'desc'
        }
      },
      recommendations: {
        take: 3 // Limit recommendations for preview
      }
    },
    orderBy: {
      endTime: 'desc'
    },
    take: 20
  });

  // Get leaderboard data
  const leaderboardData = await fetch(`${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/api/leaderboard`, {
    cache: 'no-cache'
  }).then(res => res.json());

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl">
              <Trophy className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            DICOMweb Test Results & Vendor Leaderboard
          </h1>
          <p className="text-xl text-gray-600">
            Real-time PACS conformance assessments and vendor performance rankings
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-blue-600 mb-2">
              {leaderboardData.data?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Vendors Tracked</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {leaderboardData.totalTests || 0}
            </div>
            <div className="text-sm text-gray-600">Total Tests Run</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {recentResults.length}
            </div>
            <div className="text-sm text-gray-600">Recent Tests</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-orange-600 mb-2">
              {leaderboardData.data?.[0] ? `${leaderboardData.data[0].averageComplianceScore.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Top Score</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
          >
            <BarChart3 className="mr-2 h-5 w-5" />
            Run New Test
          </Link>
        </div>

        {/* Vendor Leaderboard Section */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-blue-50">
            <div className="flex items-center">
              <Trophy className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">
                Vendor Performance Leaderboard
              </h2>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Monthly rankings based on community test results
            </p>
          </div>
          
          {leaderboardData.data && leaderboardData.data.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vendor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Compliance Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tests Run
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Testers
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Share
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leaderboardData.data.map((entry: any, index: number) => (
                    <tr key={entry.id} className={index < 3 ? 'bg-gradient-to-r from-yellow-50 to-orange-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {index === 0 && <Medal className="h-5 w-5 text-yellow-500 mr-2" />}
                          {index === 1 && <Medal className="h-5 w-5 text-gray-400 mr-2" />}
                          {index === 2 && <Medal className="h-5 w-5 text-orange-500 mr-2" />}
                          <span className="text-sm font-medium text-gray-900">
                            #{entry.overallRank}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {entry.vendor.name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {entry.vendor.description}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-bold ${
                          entry.averageComplianceScore >= 80 ? 'text-green-600' :
                          entry.averageComplianceScore >= 70 ? 'text-blue-600' :
                          entry.averageComplianceScore >= 60 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {entry.averageComplianceScore.toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.totalTestsRun}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.uniqueTesters}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.marketShare}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center">
              <Trophy className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No leaderboard data yet
              </h3>
              <p className="text-gray-600">
                Leaderboard will populate as more PACS systems are tested.
              </p>
            </div>
          )}
        </div>

        {/* Recent Test Results Section */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-green-50">
            <div className="flex items-center">
              <Users className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">
                Recent Test Results
              </h2>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Latest community-submitted PACS assessments
            </p>
          </div>
          
          {recentResults.length === 0 ? (
            <div className="p-12 text-center">
              <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No test results yet
              </h3>
              <p className="text-gray-600 mb-6">
                Be the first to test your PACS system and share the results with the community.
              </p>
              <Link
                href="/"
                className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
              >
                Start Your First Test
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {recentResults.map((result) => (
                <ResultCard key={result.id} result={result} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultCard({ result }: { result: any }) {
  const getStatusColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusBg = (score: number) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 75) return 'bg-blue-50 border-blue-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {result.pacs.vendor?.name || 'Unknown Vendor'} PACS
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBg(result.complianceScore)}`}>
              {result.conformanceLevel}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-2">
            {result.pacs.endpointUrl}
          </p>
          <div className="flex items-center text-sm text-gray-500 space-x-4">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              {formatDate(result.endTime!)}
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {result.totalDuration?.toFixed(1)}s
            </div>
            {result.organization && (
              <div className="flex items-center">
                <ExternalLink className="h-4 w-4 mr-1" />
                {result.organization}
              </div>
            )}
          </div>
        </div>
        
        <div className="text-right">
          <div className={`text-3xl font-bold mb-1 ${getStatusColor(result.complianceScore)}`}>
            {result.complianceScore.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">
            {result.passedTests}/{result.totalTests} passed
          </div>
        </div>
      </div>

      {/* Quick Protocol Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        {['QIDO', 'WADO', 'STOW'].map((protocol) => {
          const protocolResults = result.testResults.filter((t: any) => t.protocol === protocol);
          const passed = protocolResults.filter((t: any) => t.status === 'PASS').length;
          const total = protocolResults.length;
          const percentage = total > 0 ? (passed / total) * 100 : 0;
          
          return (
            <div key={protocol} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-900 mb-1">
                {protocol}-RS
              </div>
              <div className="text-sm text-gray-600">
                {passed}/{total} ({percentage.toFixed(0)}%)
              </div>
            </div>
          );
        })}
      </div>

      {/* Test Summary */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-6 text-sm">
          <div className="flex items-center text-green-600">
            <CheckCircle className="h-4 w-4 mr-1" />
            {result.passedTests} passed
          </div>
          <div className="flex items-center text-red-600">
            <XCircle className="h-4 w-4 mr-1" />
            {result.failedTests} failed
          </div>
          <div className="flex items-center text-yellow-600">
            <AlertTriangle className="h-4 w-4 mr-1" />
            {result.skippedTests} skipped
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button className="inline-flex items-center px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded">
            <Download className="h-4 w-4 mr-1" />
            PDF
          </button>
        </div>
      </div>

      {/* Quick Recommendations Preview */}
      {result.recommendations && result.recommendations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Key Recommendations:</h4>
          <div className="space-y-1">
            {result.recommendations.slice(0, 2).map((rec: any, index: number) => (
              <p key={index} className="text-sm text-gray-600">
                • {rec.title}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}