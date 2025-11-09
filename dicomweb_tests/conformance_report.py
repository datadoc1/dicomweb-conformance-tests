"""
DICOMweb Conformance Report Generator.

This module generates comprehensive conformance reports in both human-readable
and machine-readable formats from test results. Reports include actionable
recommendations and detailed analysis for vendors and implementers.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Back, Style, init
import platform

from dicomweb_tests.base import TestResult


class ConformanceReportGenerator:
    """
    Generate comprehensive DICOMweb conformance reports.
    
    Produces both JSON (machine-readable) and formatted text (human-readable)
    reports with detailed analysis, recommendations, and actionable feedback
    for PACS vendors and healthcare IT teams.
    """
    
    def __init__(self):
        init()  # Initialize colorama for colored output
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for the report."""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_reports(self, test_results: List[TestResult], 
                        output_format: str = "both",
                        output_file: str = None) -> Dict[str, str]:
        """
        Generate conformance reports in specified format(s).
        
        Args:
            test_results: List of test results to include in report
            output_format: "json", "text", or "both"
            output_file: Optional base filename for output files
            
        Returns:
            Dictionary with generated report content and file paths
        """
        reports = {}
        
        # Generate summary statistics
        summary = self._generate_summary(test_results)
        
        # Generate JSON report
        if output_format in ["json", "both"]:
            json_report = self._generate_json_report(test_results, summary)
            reports["json"] = json_report
            
            # Write JSON file if output file specified
            if output_file:
                json_filename = f"{output_file}.json"
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(json_report, f, indent=2, ensure_ascii=False)
                reports["json_file"] = json_filename
        
        # Generate text report
        if output_format in ["text", "both"]:
            text_report = self._generate_text_report(test_results, summary)
            reports["text"] = text_report
            
            # Write text file if output file specified
            if output_file:
                text_filename = f"{output_file}.txt"
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(text_report)
                reports["text_file"] = text_filename
        
        return reports
    
    def _generate_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == "PASS"])
        failed_tests = len([r for r in test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in test_results if r.status == "SKIP"])
        
        # Protocol breakdown
        protocol_stats = {}
        for protocol in ["QIDO", "WADO", "STOW"]:
            protocol_results = [r for r in test_results if r.protocol == protocol]
            protocol_stats[protocol] = {
                "total": len(protocol_results),
                "passed": len([r for r in protocol_results if r.status == "PASS"]),
                "failed": len([r for r in protocol_results if r.status == "FAIL"]),
                "skipped": len([r for r in protocol_results if r.status == "SKIP"]),
                "pass_rate": (len([r for r in protocol_results if r.status == "PASS"]) / len(protocol_results) * 100) if protocol_results else 0
            }
        
        # Performance metrics
        response_times = [r.response_time for r in test_results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Compliance score calculation
        total_possible = total_tests - skipped_tests
        compliance_score = (passed_tests / total_possible * 100) if total_possible > 0 else 0
        
        # Critical issues
        critical_failures = [r for r in test_results if r.status == "FAIL" and any(
            keyword in r.test_name.lower() for keyword in 
            ['basic', 'metadata', 'content-type', 'authentication', 'error']
        )]
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "compliance_score": round(compliance_score, 2),
            "pass_rate": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
            "protocol_statistics": protocol_stats,
            "performance_metrics": {
                "average_response_time": round(avg_response_time, 3),
                "max_response_time": round(max_response_time, 3),
                "min_response_time": round(min_response_time, 3),
                "total_response_time": round(sum(response_times), 3)
            },
            "critical_failures": len(critical_failures),
            "conformance_level": self._determine_conformance_level(compliance_score),
            "recommendations_summary": self._generate_recommendations_summary(test_results)
        }
    
    def _determine_conformance_level(self, compliance_score: float) -> str:
        """Determine conformance level based on compliance score."""
        if compliance_score >= 90:
            return "EXCELLENT"
        elif compliance_score >= 75:
            return "GOOD"
        elif compliance_score >= 60:
            return "ACCEPTABLE"
        elif compliance_score >= 40:
            return "POOR"
        else:
            return "NON_COMPLIANT"
    
    def _generate_recommendations_summary(self, test_results: List[TestResult]) -> List[str]:
        """Generate high-level recommendations summary."""
        recommendations = []
        
        # Count failures by category
        failure_categories = {
            "basic_operations": 0,
            "authentication": 0,
            "performance": 0,
            "error_handling": 0,
            "compliance": 0
        }
        
        for result in test_results:
            if result.status == "FAIL":
                test_name_lower = result.test_name.lower()
                if "basic" in test_name_lower or "query" in test_name_lower or "retrieve" in test_name_lower or "store" in test_name_lower:
                    failure_categories["basic_operations"] += 1
                elif "auth" in test_name_lower:
                    failure_categories["authentication"] += 1
                elif "performance" in test_name_lower or "time" in test_name_lower:
                    failure_categories["performance"] += 1
                elif "error" in test_name_lower or "invalid" in test_name_lower:
                    failure_categories["error_handling"] += 1
                else:
                    failure_categories["compliance"] += 1
        
        # Generate recommendations based on failure patterns
        if failure_categories["basic_operations"] > 2:
            recommendations.append("Focus on implementing core DICOMweb operations (QIDO-RS, WADO-RS, STOW-RS)")
        
        if failure_categories["authentication"] > 0:
            recommendations.append("Review and implement proper authentication mechanisms")
        
        if failure_categories["performance"] > 1:
            recommendations.append("Optimize server performance and implement caching strategies")
        
        if failure_categories["error_handling"] > 2:
            recommendations.append("Improve error response handling and HTTP status code usage")
        
        if failure_categories["compliance"] > 3:
            recommendations.append("Review DICOMweb specification compliance and implement missing features")
        
        if not recommendations:
            recommendations.append("Continue monitoring and maintaining DICOMweb compliance")
        
        return recommendations
    
    def _generate_json_report(self, test_results: List[TestResult], summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON format report."""
        # Group results by protocol
        results_by_protocol = {}
        for protocol in ["QIDO", "WADO", "STOW"]:
            protocol_results = [r for r in test_results if r.protocol == protocol]
            results_by_protocol[protocol] = [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "response_time": r.response_time,
                    "timestamp": r.timestamp,
                    "recommendation": r.recommendation,
                    "request_details": r.request_details,
                    "response_details": r.response_details
                }
                for r in protocol_results
            ]
        
        # Sort results by status (failures first)
        for protocol in results_by_protocol:
            results_by_protocol[protocol].sort(key=lambda x: (x["status"] != "PASS", x["test_name"]))
        
        return {
            "report_metadata": {
                "report_type": "DICOMweb Conformance Test Report",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "test_suite_version": "1.0.0",
                "system_info": self.system_info
            },
            "summary": summary,
            "test_results_by_protocol": results_by_protocol,
            "all_test_results": [
                {
                    "test_name": r.test_name,
                    "protocol": r.protocol,
                    "status": r.status,
                    "message": r.message,
                    "response_time": r.response_time,
                    "timestamp": r.timestamp,
                    "recommendation": r.recommendation,
                    "request_details": r.request_details,
                    "response_details": r.response_details
                }
                for r in sorted(test_results, key=lambda x: (x.protocol, x.status != "PASS", x.test_name))
            ]
        }
    
    def _generate_text_report(self, test_results: List[TestResult], summary: Dict[str, Any]) -> str:
        """Generate human-readable text report."""
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 80,
            "DICOMWEB CONFORMANCE TEST REPORT",
            "=" * 80,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Test Suite Version: 1.0.0",
            f"Platform: {self.system_info['platform']} {self.system_info['platform_version']}",
            f"Python Version: {self.system_info['python_version']}",
            ""
        ])
        
        # Executive Summary
        report_lines.extend([
            "EXECUTIVE SUMMARY",
            "-" * 40,
            f"Total Tests Run: {summary['total_tests']}",
            f"Passed: {summary['passed_tests']} {Fore.GREEN}✓{Style.RESET_ALL}",
            f"Failed: {summary['failed_tests']} {Fore.RED}✗{Style.RESET_ALL}",
            f"Skipped: {summary['skipped_tests']} {Fore.YELLOW}⊘{Style.RESET_ALL}",
            f"Pass Rate: {summary['pass_rate']:.1f}%",
            f"Compliance Score: {summary['compliance_score']:.1f}%",
            f"Conformance Level: {self._get_conformance_level_display(summary['conformance_level'])}",
            ""
        ])
        
        # Protocol Performance
        report_lines.extend([
            "PROTOCOL PERFORMANCE BREAKDOWN",
            "-" * 40
        ])
        
        for protocol, stats in summary['protocol_statistics'].items():
            if stats['total'] > 0:
                color = Fore.GREEN if stats['pass_rate'] >= 80 else Fore.YELLOW if stats['pass_rate'] >= 60 else Fore.RED
                report_lines.append(f"{protocol}-RS:")
                report_lines.append(f"  Tests: {stats['total']} | Passed: {stats['passed']} | Failed: {stats['failed']} | Skipped: {stats['skipped']}")
                report_lines.append(f"  Pass Rate: {color}{stats['pass_rate']:.1f}%{Style.RESET_ALL}")
                report_lines.append("")
        
        # Performance Metrics
        if summary['performance_metrics']['total_response_time'] > 0:
            report_lines.extend([
                "PERFORMANCE METRICS",
                "-" * 40,
                f"Average Response Time: {summary['performance_metrics']['average_response_time']:.3f}s",
                f"Maximum Response Time: {summary['performance_metrics']['max_response_time']:.3f}s",
                f"Minimum Response Time: {summary['performance_metrics']['min_response_time']:.3f}s",
                f"Total Test Duration: {summary['performance_metrics']['total_response_time']:.3f}s",
                ""
            ])
        
        # High Priority Recommendations
        if summary['recommendations_summary']:
            report_lines.extend([
                "HIGH PRIORITY RECOMMENDATIONS",
                "-" * 40
            ])
            for i, rec in enumerate(summary['recommendations_summary'], 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Critical Issues
        critical_issues = [r for r in test_results if r.status == "FAIL" and any(
            keyword in r.test_name.lower() for keyword in 
            ['basic', 'metadata', 'content-type', 'authentication', 'error']
        )]
        
        if critical_issues:
            report_lines.extend([
                "CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION",
                "-" * 40
            ])
            for issue in critical_issues:
                report_lines.append(f"• {issue.test_name}: {issue.message}")
                if issue.recommendation:
                    report_lines.append(f"  Recommendation: {issue.recommendation}")
            report_lines.append("")
        
        # Detailed Test Results
        report_lines.extend([
            "DETAILED TEST RESULTS",
            "-" * 40
        ])
        
        for protocol in ["QIDO", "WADO", "STOW"]:
            protocol_results = [r for r in test_results if r.protocol == protocol]
            if protocol_results:
                report_lines.append(f"\n{protocol}-RS TESTS:")
                report_lines.append("-" * 20)
                
                # Create table data
                table_data = []
                for result in protocol_results:
                    status_symbol = "✓" if result.status == "PASS" else "✗" if result.status == "FAIL" else "⊘"
                    status_color = Fore.GREEN if result.status == "PASS" else Fore.RED if result.status == "FAIL" else Fore.YELLOW
                    
                    table_data.append([
                        f"{status_color}{status_symbol}{Style.RESET_ALL}",
                        result.test_name,
                        f"{result.response_time:.3f}s" if result.response_time > 0 else "N/A",
                        result.message[:60] + "..." if len(result.message) > 60 else result.message
                    ])
                
                # Add table
                if table_data:
                    table = tabulate(table_data, 
                                   headers=["Status", "Test Name", "Time", "Message"],
                                   tablefmt="simple",
                                   maxcolwidths=[5, 30, 8, 37])
                    report_lines.append(table)
        
        # Vendor-facing recommendations
        report_lines.extend([
            "",
            "VENDOR-FACING RECOMMENDATIONS",
            "-" * 40,
            "For PACS Vendors and Healthcare IT Teams:",
            "",
            "1. CRITICAL COMPLIANCE GAPS",
            "   Address any failed 'Basic' tests immediately as these indicate",
            "   fundamental DICOMweb functionality issues.",
            "",
            "2. PERFORMANCE OPTIMIZATION",
            "   If average response times exceed 2 seconds, consider:",
            "   - Database indexing optimization",
            "   - Connection pooling implementation", 
            "   - Caching frequently accessed metadata",
            "",
            "3. AUTHENTICATION & SECURITY",
            "   Ensure proper implementation of authentication mechanisms",
            "   for production healthcare environments.",
            "",
            "4. ERROR HANDLING",
            "   Implement proper HTTP status codes and error messages",
            "   to facilitate integration and troubleshooting.",
            "",
            "5. ONGOING COMPLIANCE",
            "   Run these tests regularly to maintain DICOMweb compliance",
            "   as your system evolves and scales.",
            ""
        ])
        
        # Footer
        report_lines.extend([
            "=" * 80,
            "This report was generated by the DICOMweb Conformance Test Suite",
            f"Report ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}_{platform.node().replace('-', '_')}",
            "For questions or support, please refer to the DICOMweb specification",
            "and your PACS vendor documentation.",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def _get_conformance_level_display(self, conformance_level: str) -> str:
        """Get colored display for conformance level."""
        color_map = {
            "EXCELLENT": Fore.GREEN,
            "GOOD": Fore.GREEN,
            "ACCEPTABLE": Fore.YELLOW,
            "POOR": Fore.RED,
            "NON_COMPLIANT": Fore.RED
        }
        color = color_map.get(conformance_level, Fore.WHITE)
        return f"{color}{conformance_level}{Style.RESET_ALL}"
    
    def print_console_report(self, test_results: List[TestResult], summary: Dict[str, Any]):
        """Print a condensed version of the report to console."""
        print(f"\n{Fore.CYAN}DICOMweb Conformance Test Results{Style.RESET_ALL}")
        print(f"{'='*50}")
        
        # Summary
        pass_color = Fore.GREEN if summary['pass_rate'] >= 80 else Fore.YELLOW if summary['pass_rate'] >= 60 else Fore.RED
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Pass Rate: {pass_color}{summary['pass_rate']:.1f}%{Style.RESET_ALL}")
        print(f"Compliance Score: {self._get_conformance_level_display(summary['conformance_level'])}")
        
        # Quick protocol status
        print(f"\nProtocol Status:")
        for protocol, stats in summary['protocol_statistics'].items():
            if stats['total'] > 0:
                status_color = Fore.GREEN if stats['pass_rate'] >= 80 else Fore.YELLOW if stats['pass_rate'] >= 60 else Fore.RED
                print(f"  {protocol}-RS: {status_color}{stats['pass_rate']:.1f}%{Style.RESET_ALL} ({stats['passed']}/{stats['total']})")
        
        # Critical failures
        critical_failures = [r for r in test_results if r.status == "FAIL" and any(
            keyword in r.test_name.lower() for keyword in ['basic', 'metadata', 'content-type', 'authentication']
        )]
        
        if critical_failures:
            print(f"\n{Fore.RED}Critical Issues:{Style.RESET_ALL}")
            for failure in critical_failures[:3]:  # Show first 3
                print(f"  • {failure.test_name}")
        
        if summary['recommendations_summary']:
            print(f"\n{Fore.CYAN}Key Recommendations:{Style.RESET_ALL}")
            for rec in summary['recommendations_summary'][:2]:  # Show first 2
                print(f"  • {rec}")
    
    def export_to_html(self, test_results: List[TestResult], summary: Dict[str, Any], 
                      output_file: str) -> str:
        """Export report to HTML format."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DICOMweb Conformance Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .protocol-section {{ margin: 20px 0; }}
        .test-pass {{ color: #27ae60; }}
        .test-fail {{ color: #e74c3c; }}
        .test-skip {{ color: #f39c12; }}
        .recommendation {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .critical {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DICOMweb Conformance Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Total Tests:</strong> {summary['total_tests']}</p>
        <p><strong>Passed:</strong> <span class="test-pass">{summary['passed_tests']}</span></p>
        <p><strong>Failed:</strong> <span class="test-fail">{summary['failed_tests']}</span></p>
        <p><strong>Skipped:</span> <span class="test-skip">{summary['skipped_tests']}</span></p>
        <p><strong>Pass Rate:</strong> {summary['pass_rate']:.1f}%</p>
        <p><strong>Compliance Score:</strong> {summary['compliance_score']:.1f}%</p>
        <p><strong>Conformance Level:</strong> {summary['conformance_level']}</p>
    </div>
"""
        
        # Add recommendations
        if summary['recommendations_summary']:
            html_content += """
    <div class="recommendation">
        <h2>Key Recommendations</h2>
        <ul>
"""
            for rec in summary['recommendations_summary']:
                html_content += f"            <li>{rec}</li>\n"
            html_content += "        </ul>\n    </div>\n"
        
        # Add test results tables
        for protocol in ["QIDO", "WADO", "STOW"]:
            protocol_results = [r for r in test_results if r.protocol == protocol]
            if protocol_results:
                html_content += f"""
    <div class="protocol-section">
        <h2>{protocol}-RS Test Results</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Test Name</th>
                <th>Response Time</th>
                <th>Message</th>
            </tr>
"""
                for result in protocol_results:
                    status_class = f"test-{result.status.lower()}"
                    status_symbol = "✓" if result.status == "PASS" else "✗" if result.status == "FAIL" else "⊘"
                    html_content += f"""
            <tr>
                <td class="{status_class}">{status_symbol}</td>
                <td>{result.test_name}</td>
                <td>{result.response_time:.3f}s</td>
                <td>{result.message}</td>
            </tr>
"""
                html_content += "        </table>\n    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file