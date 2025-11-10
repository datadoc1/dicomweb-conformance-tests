import { prisma } from '@/lib/prisma';
import { 
  Trophy, 
  Medal, 
  Award, 
  TrendingUp, 
  TrendingDown,
  Users, 
  Calendar,
  BarChart3,
  Target,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import Link from 'next/link';

export default async function LeaderboardPage() {
  // Get vendor performance data from recent tests
  const vendorData = await prisma.testRun.groupBy({
    by: ['pacsId'],
    where: {
      isPublic: true,
      status: 'COMPLETED',
      endTime: {
        gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) // Last 30 days
      }
    },
    _avg: {
      complianceScore: true,
      passedTests: true,
      failedTests: true,
      totalTests: true,
      averageResponseTime: true,
      totalDuration: true
    },
    _count: {
      id: true
    },
    _max: {
      endTime: true
    }
  });

  // Get detailed vendor information
  const vendorDetails = await prisma.pACS.findMany({
    where: {
      id: {
        in: vendorData.map(v => v.pacsId)
      }
    },
    include: {
      vendor: true
    }
  });

  // Combine and calculate leaderboard data
  const leaderboardData = vendorData.map((vendor) => {
    const details = vendorDetails.find(d => d.id === vendor.pacsId);
    const avgScore = vendor._avg.complianceScore || 0;
    const testCount = vendor._count.id;
    const lastTest = vendor._max.endTime;
    
    return {
      vendorName: details?.vendor?.name || 'Unknown Vendor',
      vendorWebsite: details?.vendor?.website,
      pacsEndpoint: details?.endpointUrl,
      pacsName: details?.name,
      avgComplianceScore: Math.round(avgScore * 10) / 10,
      totalTests: testCount,
      lastTestDate: lastTest,
      avgResponseTime: vendor._avg.averageResponseTime || 0,
      totalPassed: vendor._avg.passedTests || 0,
      totalFailed: vendor._avg.failedTests || 0,
      totalTestsRun: vendor._avg.totalTests || 0
    };
  });

  // Sort by compliance score
  const sortedLeaderboard = leaderboardData
    .sort((a, b) => b.avgComplianceScore - a.avgComplianceScore)
    .slice(0, 20); // Top 20

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-2xl">
              <Trophy className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            PACS Vendor Leaderboard
          </h1>
          <p className="text-xl text-gray-600">
            Real-world DICOMweb compliance performance from healthcare organizations worldwide
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-blue-600 mb-2">
              {sortedLeaderboard.length}
            </div>
            <div className="text-sm text-gray-600">Vendors Ranked</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {Math.round(sortedLeaderboard.reduce((sum, v) => sum + v.avgComplianceScore, 0) / 
                Math.max(sortedLeaderboard.length, 1))}%
            </div>
            <div className="text-sm text-gray-600">Avg Compliance</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {sortedLeaderboard.reduce((sum, v) => sum + v.totalTests, 0)}
            </div>
            <div className="text-sm text-gray-600">Total Tests</div>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-2xl font-bold text-orange-600 mb-2">
              {sortedLeaderboard.filter(v => v.avgComplianceScore >= 75).length}
            </div>
            <div className="text-sm text-gray-600">Excellent (75%+)</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
          >
            <Target className="mr-2 h-5 w-5" />
            Test Your PACS
          </Link>
          <Link
            href="/results"
            className="inline-flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg"
          >
            <BarChart3 className="mr-2 h-5 w-5" />
            View Results
          </Link>
        </div>

        {/* Methodology Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                How This Leaderboard Works
              </h3>
              <div className="text-blue-800 space-y-2">
                <p>• <strong>Data Source:</strong> Real DICOMweb compliance tests run by healthcare organizations worldwide</p>
                <p>• <strong>Time Period:</strong> Results from the last 30 days</p>
                <p>• <strong>Scoring:</strong> Based on DICOM Part 18 (PS3.18) standard compliance tests</p>
                <p>• <strong>Privacy:</strong> Only publicly shared results are included</p>
                <p>• <strong>Update:</strong> Rankings are recalculated daily with new test submissions</p>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Vendor Rankings (Last 30 Days)
            </h2>
          </div>
          
          {sortedLeaderboard.length === 0 ? (
            <div className="p-12 text-center">
              <Trophy className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No vendor data yet
              </h3>
              <p className="text-gray-600 mb-6">
                Be the first to test your PACS and see your vendor's performance compared to others.
              </p>
              <Link
                href="/"
                className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
              >
                Start Testing Now
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {sortedLeaderboard.map((vendor, index) => (
                <LeaderboardRow 
                  key={vendor.pacsEndpoint} 
                  rank={index + 1} 
                  vendor={vendor} 
                />
              ))}
            </div>
          )}
        </div>

        {/* Bottom CTA */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Don't See Your Vendor Listed?
            </h3>
            <p className="text-lg mb-6">
              Test your PACS system and help the healthcare community by sharing your results.
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-8 py-4 bg-white hover:bg-gray-50 text-blue-600 font-semibold rounded-lg shadow-lg transition-all duration-200"
            >
              <Target className="mr-2 h-5 w-5" />
              Test Your PACS System
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeaderboardRow({ rank, vendor }: { rank: number; vendor: any }) {
  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
    if (rank === 3) return <Award className="h-5 w-5 text-amber-600" />;
    return <span className="text-lg font-bold text-gray-500">#{rank}</span>;
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 75) return 'bg-blue-50 border-blue-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const calculatePassRate = () => {
    if (vendor.totalTestsRun === 0) return 0;
    return Math.round((vendor.totalPassed / vendor.totalTestsRun) * 100);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        {/* Rank and Vendor Info */}
        <div className="flex items-center space-x-4 flex-1">
          <div className="flex items-center justify-center w-12 h-12">
            {getRankIcon(rank)}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {vendor.vendorName}
              </h3>
              {vendor.vendorWebsite && (
                <a 
                  href={vendor.vendorWebsite} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800"
                >
                  <Users className="h-4 w-4" />
                </a>
              )}
            </div>
            <p className="text-sm text-gray-600 mb-1">
              {vendor.pacsName} • {vendor.pacsEndpoint}
            </p>
            <div className="flex items-center text-xs text-gray-500 space-x-4">
              <div className="flex items-center">
                <Calendar className="h-3 w-3 mr-1" />
                Last test: {formatDate(vendor.lastTestDate)}
              </div>
              <div className="flex items-center">
                <Target className="h-3 w-3 mr-1" />
                {vendor.totalTests} tests
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-3 w-3 mr-1" />
                {calculatePassRate()}% pass rate
              </div>
            </div>
          </div>
        </div>

        {/* Compliance Score */}
        <div className="text-center mx-6">
          <div className={`text-3xl font-bold mb-1 ${getScoreColor(vendor.avgComplianceScore)}`}>
            {vendor.avgComplianceScore}%
          </div>
          <div className="text-sm text-gray-600">
            Compliance
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="flex space-x-6 text-center">
          <div>
            <div className="text-lg font-semibold text-gray-900">
              {vendor.avgResponseTime.toFixed(1)}s
            </div>
            <div className="text-xs text-gray-600">Avg Response</div>
          </div>
          
          <div>
            <div className="text-lg font-semibold text-green-600">
              {vendor.totalPassed}
            </div>
            <div className="text-xs text-gray-600">Passed</div>
          </div>
          
          <div>
            <div className="text-lg font-semibold text-red-600">
              {vendor.totalFailed}
            </div>
            <div className="text-xs text-gray-600">Failed</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex space-x-2 ml-4">
          <button className="inline-flex items-center px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded">
            <BarChart3 className="h-4 w-4 mr-1" />
            Details
          </button>
        </div>
      </div>
    </div>
  );
}