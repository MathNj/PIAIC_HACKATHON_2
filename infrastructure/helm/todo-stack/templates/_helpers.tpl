{{/*
Expand the name of the chart.
*/}}
{{- define "todo-stack.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-stack.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-stack.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-stack.labels" -}}
helm.sh/chart: {{ include "todo-stack.chart" . }}
{{ include "todo-stack.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: {{ .Values.global.labels.app }}
environment: {{ .Values.global.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-stack.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-stack.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
AI Ops annotations
*/}}
{{- define "todo-stack.aiOpsAnnotations" -}}
ai-ops/enabled: "true"
ai-ops/tools: "kubectl-ai,kagent"
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-stack.backendLabels" -}}
{{ include "todo-stack.labels" . }}
tier: backend
version: {{ .Chart.AppVersion }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-stack.frontendLabels" -}}
{{ include "todo-stack.labels" . }}
tier: frontend
version: {{ .Chart.AppVersion }}
{{- end }}
