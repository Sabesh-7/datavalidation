import React, { useState } from "react";
import {
  ClipboardCheck,
  UploadCloud,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Play,
  Filter,
  RefreshCw,
  Eye,
  Edit3,
  Plus,
  Search,
  Zap,
  ShieldAlert,
  Database,
  ArrowRight,
  Sparkles,
  Info
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface InconsistencyRecord {
  id: string;
  householdId: string;
  surveyName: string;
  enumerator: string;
  district: string;
  state: string;
  field: string;
  ruleCategory: "Existential" | "Referential" | "Logical" | "Range";
  ruleId: string;
  description: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  status: "Flagged" | "Under Review" | "Resolved";
  value: string;
}

export default function DataValidationWorkbench() {
  const [activeTab, setActiveTab] = useState("interactive");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("All");

  const [records, setRecords] = useState<InconsistencyRecord[]>([
    {
      id: "REC-101",
      householdId: "HH-2026-9941",
      surveyName: "PLFS 2026",
      enumerator: "Ramesh Kumar (ENUM-401)",
      district: "Patna",
      state: "Bihar",
      field: "employment_status",
      ruleCategory: "Logical",
      ruleId: "RULE_LOGICAL_AGE_EMP",
      description: "Respondent marked 'Employed' but Age is recorded as 12",
      severity: "Critical",
      status: "Flagged",
      value: "Employed (Age: 12)"
    },
    {
      id: "REC-102",
      householdId: "HH-2026-8812",
      surveyName: "HCES 2026",
      enumerator: "Anita Roy (ENUM-112)",
      district: "Lucknow",
      state: "Uttar Pradesh",
      field: "monthly_expenditure",
      ruleCategory: "Logical",
      ruleId: "RULE_LOGICAL_INC_EXP",
      description: "Monthly Expenditure (₹95,000) exceeds 5x Income (₹15,000)",
      severity: "High",
      status: "Flagged",
      value: "Exp: ₹95,000 | Inc: ₹15,000"
    },
    {
      id: "REC-103",
      householdId: "HH-2026-7734",
      surveyName: "PLFS 2026",
      enumerator: "Suresh P (ENUM-305)",
      district: "Jaipur",
      state: "Rajasthan",
      field: "occupation_code",
      ruleCategory: "Referential",
      ruleId: "RULE_REF_NCO",
      description: "Occupation code '9999' not found in NCO-2015 dictionary",
      severity: "High",
      status: "Flagged",
      value: "Code: 9999"
    }
  ]);

  const [simRecord, setSimRecord] = useState({
    householdId: "HH-2026-9900",
    stateCode: "10",
    districtCode: "140",
    age: "14",
    empStatus: "Employed",
    income: "20000",
    expenditure: "110000",
    occCode: "9999"
  });

  const [simResults, setSimResults] = useState<any[]>([]);

  const handleRunSimValidation = () => {
    const violations = [];
    const ageNum = parseFloat(simRecord.age);
    if (ageNum < 15 && simRecord.empStatus.toLowerCase() === "employed") {
      violations.push({
        ruleId: "RULE_LOGICAL_AGE_EMP",
        category: "Logical",
        message: `Child labor logic violation: Age is ${simRecord.age} but status is 'Employed'`,
        severity: "Critical"
      });
    }

    const inc = parseFloat(simRecord.income);
    const exp = parseFloat(simRecord.expenditure);
    if (inc > 0 && exp > inc * 5) {
      violations.push({
        ruleId: "RULE_LOGICAL_INC_EXP",
        category: "Logical",
        message: `Financial Ratio Anomaly: Expenditure (₹${exp}) is > 5x Income (₹${inc})`,
        severity: "High"
      });
    }

    if (simRecord.occCode === "9999") {
      violations.push({
        ruleId: "RULE_REF_NCO",
        category: "Referential",
        message: `Occupation Code '9999' is invalid in NCO-2015 Taxonomy`,
        severity: "High"
      });
    }

    setSimResults(violations);
  };

  const handleResolveRecord = (id: string) => {
    setRecords(prev =>
      prev.map(r => (r.id === id ? { ...r, status: "Resolved" } : r))
    );
  };

  const filteredRecords = records.filter(r => {
    const matchesSearch =
      r.householdId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = selectedSeverity === "All" || r.severity === selectedSeverity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-[#003366] via-[#004e8c] to-[#002244] text-white p-6 rounded-xl shadow-lg border border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge className="bg-[#f39c12] text-white font-bold px-2.5 py-0.5 text-xs">
              MoSPI HSD Module
            </Badge>
            <span className="text-xs text-blue-200 uppercase tracking-widest">
              Data Validation Platform
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-extrabold tracking-tight">
            Data Validation & Inconsistency Workbench
          </h1>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
        <TabsList className="grid grid-cols-2 bg-slate-100 p-1.5 rounded-lg border border-slate-200">
          <TabsTrigger value="interactive" className="data-[state=active]:bg-[#003366] data-[state=active]:text-white font-bold">
            Interactive Workbench
          </TabsTrigger>
          <TabsTrigger value="batch" className="data-[state=active]:bg-[#003366] data-[state=active]:text-white font-bold">
            Batch Processing
          </TabsTrigger>
        </TabsList>

        <TabsContent value="interactive" className="space-y-6">
          <Card className="border border-slate-200 shadow-sm bg-white">
            <CardHeader className="bg-slate-50 border-b border-slate-200 py-4">
              <CardTitle className="text-lg font-bold text-[#003366]">Interactive Real-Time Rule Simulator</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="text-xs font-bold">Age</label>
                  <Input value={simRecord.age} onChange={e => setSimRecord({ ...simRecord, age: e.target.value })} />
                </div>
                <div>
                  <label className="text-xs font-bold">Status</label>
                  <Input value={simRecord.empStatus} onChange={e => setSimRecord({ ...simRecord, empStatus: e.target.value })} />
                </div>
                <div>
                  <label className="text-xs font-bold">Income</label>
                  <Input value={simRecord.income} onChange={e => setSimRecord({ ...simRecord, income: e.target.value })} />
                </div>
                <div>
                  <label className="text-xs font-bold">Expenditure</label>
                  <Input value={simRecord.expenditure} onChange={e => setSimRecord({ ...simRecord, expenditure: e.target.value })} />
                </div>
              </div>

              <Button onClick={handleRunSimValidation} className="bg-[#003366] text-white font-bold">
                Run Validation
              </Button>

              {simResults.length > 0 && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="text-xs font-bold text-red-700">Violations Detected ({simResults.length}):</h4>
                  <ul className="text-xs text-red-900 mt-1">
                    {simResults.map((v, i) => (
                      <li key={i}>[{v.severity}] {v.message}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="batch" className="space-y-6">
          <Card className="border border-slate-200 bg-white">
            <CardHeader><CardTitle>Batch Processing</CardTitle></CardHeader>
            <CardContent><p className="text-xs">Upload Parquet/CSV dataset for multi-threaded validation.</p></CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
