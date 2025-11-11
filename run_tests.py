#!/usr/bin/env python3
"""
DICOMweb Conformance Test Suite - Main Runner

This is the main entry point for the DICOMweb conformance test suite.
It provides a command-line interface to run tests and generate reports.
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from dicomweb_tests.base import TestResult
from dicomweb_tests.qido_tests import QIDOTest
from dicomweb_tests.wado_tests import WADOTest
from dicomweb_tests.stow_tests import STOWTest
from dicomweb_tests.conformance_report import ConformanceReportGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DICOMweb Conformance Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python run_tests.py --pacs-url https://server/dicomweb
  
  # With authentication
  python run_tests.py --pacs-url https://server/dicomweb --username user --password pass
  
  # Custom output format
  python run_tests.py --pacs-url https://server/dicomweb --output-format json
  
  # Verbose output
  python run_tests.py --pacs-url https://server/dicomweb --verbose
  
  # Protocol-specific tests
  python run_tests.py --pacs-url https://server/dicomweb --protocols qido,wado
  
  # Custom output file
  python run_tests.py --pacs-url https://server/dicomweb --output-file my_test_results
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--pacs-url',
        required=True,
        help='Base URL of the PACS server (e.g., https://server/dicomweb)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--username',
        help='Username for authentication (if required)'
    )
    
    parser.add_argument(
        '--password',
        help='Password for authentication (if required)'
    )
    
    parser.add_argument(
        '--protocols',
        default='qido,wado,stow',
        help='Comma-separated list of protocols to test (qido,wado,stow). Default: all'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['text', 'json', 'both'],
        default='both',
        help='Output format for reports. Default: both'
    )
    
    parser.add_argument(
        '--output-file',
        help='Base filename for output files (without extension)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds. Default: 30'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output, only generate reports'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML report in addition to other formats'
    )
    
    parser.add_argument(
        '--test-data-path',
        help='Path to test data directory'
    )
    
    return parser.parse_args()


def validate_pacs_url(url):
    """Validate the PACS URL format."""
    if not url.startswith(('http://', 'https://')):
        print("Error: PACS URL must start with http:// or https://")
        return False
    
    if not url.endswith('/dicomweb'):
        print("Warning: PACS URL should typically end with '/dicomweb'")
    
    return True


def validate_credentials(username, password):
    """Validate authentication credentials."""
    if (username and not password) or (password and not username):
        print("Error: Both username and password must be provided together")
        return False
    
    return True


def parse_protocols(protocols_str):
    """Parse and validate protocol selection."""
    valid_protocols = {'qido', 'wado', 'stow'}
    requested_protocols = {p.strip().lower() for p in protocols_str.split(',')}
    
    invalid_protocols = requested_protocols - valid_protocols
    if invalid_protocols:
        print(f"Error: Invalid protocols specified: {', '.join(invalid_protocols)}")
        print(f"Valid protocols: {', '.join(valid_protocols)}")
        return None
    
    return requested_protocols


def run_test_suite(args):
    """Run the complete test suite."""
    start_time = time.time()
    
    if not args.quiet:
        print(f"{'='*60}")
        print("DICOMWEB CONFORMANCE TEST SUITE")
        print(f"{'='*60}")
        print(f"Target PACS: {args.pacs_url}")
        print(f"Protocols: {', '.join(sorted(args.protocols))}")
        if args.username:
            print("Authentication: Enabled")
        else:
            print("Authentication: None")
        print(f"Timeout: {args.timeout}s")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
    
    # Initialize test results
    all_results = []
    
    # Run QIDO-RS tests
    if 'qido' in args.protocols:
        if not args.quiet:
            print("Running QIDO-RS (Query) tests...")
        
        qido_test = QIDOTest(
            pacs_url=args.pacs_url,
            username=args.username,
            password=args.password,
            timeout=args.timeout,
            verbose=args.verbose
        )
        qido_results = qido_test.run_tests()
        all_results.extend(qido_results)
        
        if not args.quiet:
            qido_summary = qido_test.get_summary()
            print(f"QIDO-RS Results: {qido_summary['passed']}/{qido_summary['total_tests']} passed")
            print()
    
    # Run WADO-RS tests
    if 'wado' in args.protocols:
        if not args.quiet:
            print("Running WADO-RS (Retrieve) tests...")
        
        wado_test = WADOTest(
            pacs_url=args.pacs_url,
            username=args.username,
            password=args.password,
            timeout=args.timeout,
            verbose=args.verbose
        )
        wado_results = wado_test.run_tests()
        all_results.extend(wado_results)
        
        if not args.quiet:
            wado_summary = wado_test.get_summary()
            print(f"WADO-RS Results: {wado_summary['passed']}/{wado_summary['total_tests']} passed")
            print()
    
    # Run STOW-RS tests
    if 'stow' in args.protocols:
        if not args.quiet:
            print("Running STOW-RS (Store) tests...")
        
        stow_test = STOWTest(
            pacs_url=args.pacs_url,
            username=args.username,
            password=args.password,
            timeout=args.timeout,
            verbose=args.verbose
        )
        stow_results = stow_test.run_tests()
        all_results.extend(stow_results)
        
        if not args.quiet:
            stow_summary = stow_test.get_summary()
            print(f"STOW-RS Results: {stow_summary['passed']}/{stow_summary['total_tests']} passed")
            print()
    
    # Calculate overall results
    total_time = time.time() - start_time
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r.status == "PASS"])
    failed_tests = len([r for r in all_results if r.status == "FAIL"])
    skipped_tests = len([r for r in all_results if r.status == "SKIP"])
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if not args.quiet:
        print(f"{'='*60}")
        print("TEST SUITE COMPLETE")
        print(f"{'='*60}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print()
    
    # Generate reports
    if not args.quiet:
        print("Generating reports...")
    
    # Initialize report generator
    report_generator = ConformanceReportGenerator()
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.output_file:
        output_base = args.output_file
    else:
        # Create default filename
        url_host = args.pacs_url.split('//')[1].split('/')[0].replace(':', '_')
        output_base = f"dicomweb_conformance_{url_host}_{timestamp}"
    
    # Generate reports with PACS metadata
    reports = report_generator.generate_reports(
        test_results=all_results,
        output_format=args.output_format,
        output_file=output_base,
        pacs_url=args.pacs_url,
        username=args.username,
        password=args.password,
    )

    # Save raw PACS metadata (if available) to a separate file
    summary_for_raw = report_generator._generate_summary(
        all_results,
        pacs_url=args.pacs_url,
        username=args.username,
        password=args.password,
    )
    pacs_meta = summary_for_raw.get("pacs_metadata") or {}
    if pacs_meta:
        raw_meta_file = f"{output_base}_pacs_metadata.json"
        try:
            with open(raw_meta_file, "w", encoding="utf-8") as f:
                json.dump(pacs_meta, f, indent=2, ensure_ascii=False)
            reports["pacs_metadata_file"] = raw_meta_file
            if not args.quiet:
                print(f"PACS metadata saved to: {raw_meta_file}")
        except Exception as e:
            if not args.quiet:
                print(f"Warning: Failed to write PACS metadata file: {e}")
    
    # Generate HTML report if requested
    if args.html:
        html_file = f"{output_base}.html"
        report_generator.export_to_html(
            test_results=all_results,
            summary=summary_for_raw,
            output_file=html_file
        )
        reports["html_file"] = html_file
        if not args.quiet:
            print(f"HTML report generated: {html_file}")
    
    # Display console summary
    if not args.quiet:
        report_generator.print_console_report(all_results, summary_for_raw)
        print()
    
    # Report file locations
    if not args.quiet:
        print("Reports generated:")
        for format_type, file_path in reports.items():
            if file_path:
                print(f"  {format_type.upper()}: {file_path}")
    
    return all_results, reports


def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate inputs
        if not validate_pacs_url(args.pacs_url):
            sys.exit(1)
        
        if not validate_credentials(args.username, args.password):
            sys.exit(1)
        
        # Parse protocols
        protocols = parse_protocols(args.protocols)
        if protocols is None:
            sys.exit(1)
        args.protocols = protocols
        
        # Run test suite
        all_results, reports = run_test_suite(args)
        
        # Exit with appropriate code
        total_tests = len(all_results)
        failed_tests = len([r for r in all_results if r.status == "FAIL"])
        
        if failed_tests > 0:
            if not args.quiet:
                print(f"\nTest suite completed with {failed_tests} failures")
            sys.exit(1)
        else:
            if not args.quiet:
                print(f"\nAll tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError running test suite: {e}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()