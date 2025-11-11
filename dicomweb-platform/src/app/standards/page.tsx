"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import mapping from "../../../../DICOM_CONFORMANCE_MAPPING.json";

type RequirementLevel = "SHALL" | "SHOULD" | "MAY";
type Protocol = "QIDO" | "WADO" | "STOW";

interface MappingRequirement {
  dicom_section?: string;
  requirement?: string;
  test_id?: string;
  test_name?: string;
  classification?: "mandatory" | "recommended" | "optional";
  description?: string;
}

interface MappingFile {
  conformance_classification: {
    mandatory: { keyword: RequirementLevel; description: string; color_code: string };
    recommended: { keyword: RequirementLevel; description: string; color_code: string };
    optional: { keyword: RequirementLevel; description: string; color_code: string };
  };
  protocols: {
    qido?: {
      section: string;
      official_reference: string;
      endpoints: Record<string, { requirements?: MappingRequirement[] }>;
    };
    wado?: {
      section: string;
      official_reference: string;
      endpoints: Record<string, { requirements?: MappingRequirement[] }>;
    };
    stow?: {
      section: string;
      official_reference: string;
      endpoints: Record<string, { requirements?: MappingRequirement[] }>;
    };
  };
}

interface WeightedRule {
  weight: number;
  label: string;
  description: string;
}

const defaultWeightedRules: Record<RequirementLevel, WeightedRule> = {
  SHALL: {
    weight: 3,
    label: "Mandatory",
    description:
      "SHALL requirements are mandatory. Any failure directly reduces core conformance.",
  },
  SHOULD: {
    weight: 1,
    label: "Recommended",
    description:
      "SHOULD requirements are strongly recommended. Missing support is not fatal, but reduces best-practice score.",
  },
  MAY: {
    weight: 0.25,
    label: "Optional",
    description:
      "MAY requirements are optional. Implementations get positive credit if supported; absence does not hurt core score.",
  },
};

type SortKey = "protocol" | "test_id" | "level" | "classification" | "dicom_section";

interface Row {
  protocol: Protocol;
  test_id: string;
  test_name: string;
  dicom_section: string;
  level: RequirementLevel;
  classification: "mandatory" | "recommended" | "optional";
  description: string;
  spec_url: string;
}

function normalizeLevel(classification: "mandatory" | "recommended" | "optional"): RequirementLevel {
  switch (classification) {
    case "mandatory":
      return "SHALL";
    case "recommended":
      return "SHOULD";
    case "optional":
    default:
      return "MAY";
  }
}

function buildRows(data: MappingFile): Row[] {
  const rows: Row[] = [];

  const pushFromProtocol = (
    protocolKey: "qido" | "wado" | "stow",
    protocolName: Protocol
  ) => {
    const p = data.protocols[protocolKey];
    if (!p) return;
    const specBase = p.official_reference || "";

    Object.values(p.endpoints || {}).forEach((endpoint) => {
      (endpoint.requirements || []).forEach((req) => {
        if (!req.test_id || !req.classification) return;

        const level = normalizeLevel(req.classification);
        rows.push({
          protocol: protocolName,
          test_id: req.test_id,
          test_name: req.test_name || "",
          dicom_section: req.dicom_section || p.section,
          level,
          classification: req.classification,
          description: req.description || req.requirement || "",
          spec_url: specBase,
        });
      });
    });
  };

  pushFromProtocol("qido", "QIDO");
  pushFromProtocol("wado", "WADO");
  pushFromProtocol("stow", "STOW");

  // Ensure deterministic order by default (protocol, test_id)
  rows.sort((a, b) => {
    if (a.protocol !== b.protocol) return a.protocol.localeCompare(b.protocol);
    return a.test_id.localeCompare(b.test_id);
  });

  return rows;
}

export default function StandardsPage() {
  const [protocolFilter, setProtocolFilter] = useState<Protocol | "ALL">("ALL");
  const [levelFilter, setLevelFilter] = useState<RequirementLevel | "ALL">("ALL");
  const [sortKey, setSortKey] = useState<SortKey>("protocol");

  const data = mapping as MappingFile;
  const rows = useMemo(() => buildRows(data), [data]);

  const filtered = useMemo(
    () =>
      rows.filter((row) => {
        if (protocolFilter !== "ALL" && row.protocol !== protocolFilter) return false;
        if (levelFilter !== "ALL" && row.level !== levelFilter) return false;
        return true;
      }),
    [rows, protocolFilter, levelFilter]
  );

  const sorted = useMemo(() => {
    const copy = [...filtered];
    copy.sort((a, b) => {
      switch (sortKey) {
        case "protocol":
          if (a.protocol !== b.protocol) return a.protocol.localeCompare(b.protocol);
          return a.test_id.localeCompare(b.test_id);
        case "test_id":
          return a.test_id.localeCompare(b.test_id);
        case "level":
          return (
            defaultWeightedRules[b.level].weight - defaultWeightedRules[a.level].weight ||
            a.test_id.localeCompare(b.test_id)
          );
        case "classification":
          return a.classification.localeCompare(b.classification) || a.test_id.localeCompare(b.test_id);
        case "dicom_section":
          return a.dicom_section.localeCompare(b.dicom_section) || a.test_id.localeCompare(b.test_id);
        default:
          return 0;
      }
    });
    return copy;
  }, [filtered, sortKey]);

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          DICOMweb Standards & Scoring
        </h1>

        <p className="text-gray-700 mb-4">
          This page documents the exact DICOMweb requirements tested by this suite, how they map to the
          official DICOM Part 18 specification, and how conformance scoring is computed. Each entry below
          corresponds to a requirement defined in <code>DICOM_CONFORMANCE_MAPPING.json</code> and enforced
          by the Python test harness.
        </p>

        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6 space-y-3">
          <h2 className="text-xl font-semibold text-gray-900">Official DICOMweb References</h2>
          <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
            <li>
              QIDO-RS Search Transaction (PS3.18 Section 10.6):{" "}
              <Link
                href="https://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_10.6.html"
                target="_blank"
                className="underline"
              >
                dicom.nema.org/sect_10.6
              </Link>
            </li>
            <li>
              WADO-RS Retrieve (PS3.18 Section 10.4):{" "}
              <Link
                href="https://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_10.4.html"
                target="_blank"
                className="underline"
              >
                dicom.nema.org/sect_10.4
              </Link>
            </li>
            <li>
              STOW-RS Store (PS3.18 Section 10.5):{" "}
              <Link
                href="https://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_10.5.html"
                target="_blank"
                className="underline"
              >
                dicom.nema.org/sect_10.5
              </Link>
            </li>
            <li>
              DICOMweb Overview:{" "}
              <Link
                href="https://www.dicomstandard.org/using/dicomweb/"
                target="_blank"
                className="underline"
              >
                dicomstandard.org/using/dicomweb
              </Link>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6 space-y-2">
          <h2 className="text-xl font-semibold text-gray-900">Scoring Model</h2>
          <p className="text-sm text-gray-700">
            Each mapped requirement produces one or more concrete tests. Test results include:
            <code className="mx-1">mapping_id</code>,
            <code className="mx-1">requirement</code>,
            and
            <code className="mx-1">requirement_level</code> (SHALL/SHOULD/MAY).
            Scores are computed transparently as follows:
          </p>
          <ul className="list-disc list-inside text-sm text-gray-800 space-y-1">
            <li>
              For each requirement, we assign a base weight by level:
              <span className="ml-1 font-mono">SHALL = {defaultWeightedRules.SHALL.weight}</span>,
              <span className="ml-1 font-mono">SHOULD = {defaultWeightedRules.SHOULD.weight}</span>,
              <span className="ml-1 font-mono">MAY = {defaultWeightedRules.MAY.weight}</span>.
            </li>
            <li>
              PASS:
              earns full weight for that requirement.
            </li>
            <li>
              FAIL on a SHALL:
              subtracts the full SHALL weight from the protocol and overall score.
            </li>
            <li>
              FAIL on a SHOULD:
              treated as a negative signal (implementation is non-standard or misleading) and may reduce score.
            </li>
            <li>
              MAY:
              contributes positive credit when implemented; absence (SKIP) is neutral. Only actively wrong behavior yields a small penalty.
            </li>
            <li>
              SKIP semantics:
              - For SHALL: indicates test could not be executed (e.g., prerequisite missing); reported but not auto-passed.
              - For SHOULD/MAY: usually treated as “not implemented, but acceptable” (neutral unless configured otherwise).
            </li>
          </ul>
          <p className="text-xs text-gray-500">
            Exact numeric weights can be centrally configured (e.g. via a scoring config file) and are applied uniformly
            in the conformance report generator so that all scoring is deterministic and reproducible.
          </p>
        </div>

        <div className="flex flex-wrap gap-3 items-center mb-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">Filter by Protocol:</span>
            <select
              value={protocolFilter}
              onChange={(e) => setProtocolFilter(e.target.value as any)}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value="ALL">All</option>
              <option value="QIDO">QIDO-RS</option>
              <option value="WADO">WADO-RS</option>
              <option value="STOW">STOW-RS</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">Filter by Level:</span>
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value as any)}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value="ALL">All</option>
              <option value="SHALL">SHALL (Mandatory)</option>
              <option value="SHOULD">SHOULD (Recommended)</option>
              <option value="MAY">MAY (Optional)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">Sort by:</span>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value="protocol">Protocol & Test ID</option>
              <option value="test_id">Test ID</option>
              <option value="level">Requirement Level</option>
              <option value="classification">Classification</option>
              <option value="dicom_section">DICOM Section</option>
            </select>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="px-3 py-2 text-left">Protocol</th>
                <th className="px-3 py-2 text-left">Test ID</th>
                <th className="px-3 py-2 text-left">Name</th>
                <th className="px-3 py-2 text-left">Level</th>
                <th className="px-3 py-2 text-left">Classification</th>
                <th className="px-3 py-2 text-left">DICOM Section</th>
                <th className="px-3 py-2 text-left">Description</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((row) => {
                const rule = defaultWeightedRules[row.level];
                return (
                  <tr key={`${row.protocol}-${row.test_id}`} className="border-t border-gray-100">
                    <td className="px-3 py-2 font-mono text-xs text-gray-700">
                      {row.protocol}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs text-blue-700">
                      {row.test_id}
                    </td>
                    <td className="px-3 py-2 text-gray-900">{row.test_name}</td>
                    <td className="px-3 py-2">
                      <span
                        className="px-2 py-1 rounded-full text-xs font-semibold"
                        style={{
                          backgroundColor: "#f3f4ff",
                          color:
                            row.level === "SHALL"
                              ? "#b91c1c"
                              : row.level === "SHOULD"
                              ? "#92400e"
                              : "#166534",
                        }}
                      >
                        {row.level} · {rule.label} · w={rule.weight}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-xs text-gray-600">{row.classification}</td>
                    <td className="px-3 py-2 text-xs text-blue-700">
                      {row.spec_url ? (
                        <Link href={row.spec_url} target="_blank" className="underline">
                          {row.dicom_section}
                        </Link>
                      ) : (
                        row.dicom_section
                      )}
                    </td>
                    <td className="px-3 py-2 text-xs text-gray-700 max-w-xl">
                      {row.description}
                    </td>
                  </tr>
                );
              })}
              {sorted.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-3 py-4 text-center text-sm text-gray-500"
                  >
                    No requirements found for the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}