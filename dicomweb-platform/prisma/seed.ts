import { PrismaClient } from '../src/generated/prisma/index.js'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding database...')

  // Create sample vendors
  const agfa = await prisma.vendor.create({
    data: {
      name: 'AGFA HealthCare',
      website: 'https://www.agfa.com/',
      description: 'Leading provider of imaging and IT solutions for healthcare'
    }
  })

  const ge = await prisma.vendor.create({
    data: {
      name: 'GE Healthcare',
      website: 'https://www.ge.com/healthcare/',
      description: 'Medical imaging and healthcare technology solutions'
    }
  })

  const philips = await prisma.vendor.create({
    data: {
      name: 'Philips Healthcare',
      website: 'https://www.philips.com/healthcare/',
      description: 'Health technology company focused on improving health outcomes'
    }
  })

  const fuji = await prisma.vendor.create({
    data: {
      name: 'FUJIFILM Healthcare',
      website: 'https://www.fujifilm.com/healthcare/',
      description: 'Medical imaging and healthcare solutions'
    }
  })

  // Create sample PACS systems
  const pacs1 = await prisma.pACS.create({
    data: {
      name: 'AGFA Enterprise PACS',
      endpointUrl: 'https://pacs.example-agfa.com/dicomweb/',
      vendorId: agfa.id,
      description: 'AGFA Enterprise PACS v8.0',
      version: '8.0.1',
      location: 'Test Environment',
      isPublic: true
    }
  })

  const pacs2 = await prisma.pACS.create({
    data: {
      name: 'GE AW Server',
      endpointUrl: 'https://pacs.example-ge.com/dicomweb/',
      vendorId: ge.id,
      description: 'GE Advantage Workstation Server',
      version: '4.0',
      location: 'Demo Environment',
      isPublic: true
    }
  })

  const pacs3 = await prisma.pACS.create({
    data: {
      name: 'Philips iView',
      endpointUrl: 'https://pacs.example-philips.com/dicomweb/',
      vendorId: philips.id,
      description: 'Philips iView Enterprise',
      version: '3.5',
      location: 'Development Environment',
      isPublic: true
    }
  })

  // Create sample test runs
  const testRun1 = await prisma.testRun.create({
    data: {
      pacsId: pacs1.id,
      runIdentifier: 'test-run-agfa-001',
      status: 'COMPLETED',
      startTime: new Date('2024-11-01T10:00:00Z'),
      endTime: new Date('2024-11-01T10:15:32Z'),
      protocolsTested: 'QIDO,WADO,STOW',
      timeout: 30,
      verbose: true,
      totalTests: 156,
      passedTests: 98,
      failedTests: 45,
      skippedTests: 13,
      complianceScore: 62.8,
      conformanceLevel: 'INTERMEDIATE',
      averageResponseTime: 2.3,
      maxResponseTime: 8.7,
      minResponseTime: 0.4,
      totalDuration: 932,
      isPublic: true,
      shareToken: 'abc123def456',
      socialMediaShared: true,
      sharedAt: new Date('2024-11-01T11:00:00Z'),
      contactEmail: 'test@hospital.org',
      organization: 'St. Mary\'s Hospital',
      contactName: 'Dr. John Smith'
    }
  })

  const testRun2 = await prisma.testRun.create({
    data: {
      pacsId: pacs2.id,
      runIdentifier: 'test-run-ge-002',
      status: 'COMPLETED',
      startTime: new Date('2024-11-02T14:30:00Z'),
      endTime: new Date('2024-11-02T14:42:15Z'),
      protocolsTested: 'QIDO,WADO,STOW',
      timeout: 30,
      verbose: true,
      totalTests: 156,
      passedTests: 132,
      failedTests: 18,
      skippedTests: 6,
      complianceScore: 84.6,
      conformanceLevel: 'ADVANCED',
      averageResponseTime: 1.8,
      maxResponseTime: 5.2,
      minResponseTime: 0.3,
      totalDuration: 735,
      isPublic: true,
      shareToken: 'xyz789uvw012',
      socialMediaShared: false,
      contactEmail: 'admin@clinic.com',
      organization: 'City Medical Clinic',
      contactName: 'Dr. Sarah Johnson'
    }
  })

  const testRun3 = await prisma.testRun.create({
    data: {
      pacsId: pacs3.id,
      runIdentifier: 'test-run-philips-003',
      status: 'COMPLETED',
      startTime: new Date('2024-11-03T09:15:00Z'),
      endTime: new Date('2024-11-03T09:28:45Z'),
      protocolsTested: 'QIDO,WADO,STOW',
      timeout: 30,
      verbose: true,
      totalTests: 156,
      passedTests: 112,
      failedTests: 32,
      skippedTests: 12,
      complianceScore: 71.8,
      conformanceLevel: 'INTERMEDIATE',
      averageResponseTime: 2.1,
      maxResponseTime: 6.8,
      minResponseTime: 0.5,
      totalDuration: 825,
      isPublic: true,
      shareToken: 'def456ghi789',
      socialMediaShared: true,
      sharedAt: new Date('2024-11-03T10:00:00Z'),
      contactEmail: 'it@hospital.com',
      organization: 'Regional Health System',
      contactName: 'Mike Thompson'
    }
  })

  // Create sample test results
  await prisma.testResult.create({
    data: {
      testRunId: testRun1.id,
      testId: 'QIDO_001',
      testName: 'QIDO-RS Basic Query',
      protocol: 'QIDO',
      status: 'PASS',
      message: 'Query executed successfully',
      dicomSection: 'PS3.18:6.4.1',
      requirement: 'SHALL',
      classification: 'mandatory'
    }
  })

  await prisma.testResult.create({
    data: {
      testRunId: testRun1.id,
      testId: 'WADO_001',
      testName: 'WADO-RS Image Retrieval',
      protocol: 'WADO',
      status: 'FAIL',
      message: 'Connection timeout after 5 seconds',
      dicomSection: 'PS3.18:6.5.2',
      requirement: 'SHALL',
      classification: 'mandatory'
    }
  })

  await prisma.testResult.create({
    data: {
      testRunId: testRun2.id,
      testId: 'QIDO_001',
      testName: 'QIDO-RS Basic Query',
      protocol: 'QIDO',
      status: 'PASS',
      message: 'Query executed successfully',
      dicomSection: 'PS3.18:6.4.1',
      requirement: 'SHALL',
      classification: 'mandatory'
    }
  })

  await prisma.testResult.create({
    data: {
      testRunId: testRun2.id,
      testId: 'STOW_001',
      testName: 'STOW-RS Storage',
      protocol: 'STOW',
      status: 'PASS',
      message: 'Storage completed successfully',
      dicomSection: 'PS3.18:6.7.1',
      requirement: 'SHALL',
      classification: 'mandatory'
    }
  })

  // Create leaderboard entries
  await prisma.leaderboardEntry.create({
    data: {
      vendorId: ge.id,
      period: 'MONTHLY',
      periodStart: new Date('2024-11-01T00:00:00Z'),
      periodEnd: new Date('2024-11-30T23:59:59Z'),
      averageComplianceScore: 84.6,
      totalTestsRun: 156,
      uniqueTesters: 23,
      overallRank: 1,
      qidoRank: 1,
      wadoRank: 2,
      stowRank: 1,
      performanceRank: 1
    }
  })

  await prisma.leaderboardEntry.create({
    data: {
      vendorId: philips.id,
      period: 'MONTHLY',
      periodStart: new Date('2024-11-01T00:00:00Z'),
      periodEnd: new Date('2024-11-30T23:59:59Z'),
      averageComplianceScore: 71.8,
      totalTestsRun: 156,
      uniqueTesters: 31,
      overallRank: 2,
      qidoRank: 2,
      wadoRank: 3,
      stowRank: 2,
      performanceRank: 3
    }
  })

  await prisma.leaderboardEntry.create({
    data: {
      vendorId: agfa.id,
      period: 'MONTHLY',
      periodStart: new Date('2024-11-01T00:00:00Z'),
      periodEnd: new Date('2024-11-30T23:59:59Z'),
      averageComplianceScore: 62.8,
      totalTestsRun: 156,
      uniqueTesters: 47,
      overallRank: 3,
      qidoRank: 3,
      wadoRank: 4,
      stowRank: 4,
      performanceRank: 4
    }
  })

  await prisma.leaderboardEntry.create({
    data: {
      vendorId: fuji.id,
      period: 'MONTHLY',
      periodStart: new Date('2024-11-01T00:00:00Z'),
      periodEnd: new Date('2024-11-30T23:59:59Z'),
      averageComplianceScore: 78.2,
      totalTestsRun: 156,
      uniqueTesters: 18,
      overallRank: 4,
      qidoRank: 4,
      wadoRank: 1,
      stowRank: 3,
      performanceRank: 2
    }
  })

  // Create sharing links
  await prisma.sharingLink.create({
    data: {
      testRunId: testRun1.id,
      shortCode: 'abc123def456',
      clicks: 23,
      isActive: true
    }
  })

  await prisma.sharingLink.create({
    data: {
      testRunId: testRun2.id,
      shortCode: 'xyz789uvw012',
      clicks: 12,
      isActive: true
    }
  })

  console.log('Database seeded successfully!')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    await prisma.$disconnect()
    process.exit(1)
  })