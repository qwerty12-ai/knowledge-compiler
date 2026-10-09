import { AnalyzeForm } from "@/components/analysis/analyze-form";
import {
  PageContainer,
  SectionHeader,
} from "@/components/ui/primitives";

export default function NewAnalysisPage() {
  return (
    <PageContainer>
      <div className="max-w-5xl space-y-8">
        <SectionHeader
          eyebrow="New analysis"
          title="Analyze a repository."
          description="Give the compiler a repository to interrogate. It will discover structure, collect evidence, generate claims, and measure how strongly the evidence supports them."
        />

        <AnalyzeForm />
      </div>
    </PageContainer>
  );
}