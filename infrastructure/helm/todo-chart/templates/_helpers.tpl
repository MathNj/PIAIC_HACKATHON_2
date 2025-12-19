{{/*
Expand the name of the chart.
*/}}
{{- define "todo-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-chart.fullname" -}}
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
{{- define "todo-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-chart.labels" -}}
helm.sh/chart: {{ include "todo-chart.chart" . }}
{{ include "todo-chart.selectorLabels" . }}
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
{{- define "todo-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
AI Ops annotations for kagent and kubectl-ai compatibility
*/}}
{{- define "todo-chart.aiOpsAnnotations" -}}
ai-ops/enabled: "true"
ai-ops/tools: "kubectl-ai,kagent"
description: "Todo Chatbot with AI Agent deployed on Kubernetes"
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-chart.backendLabels" -}}
{{ include "todo-chart.labels" . }}
tier: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-chart.frontendLabels" -}}
{{ include "todo-chart.labels" . }}
tier: frontend
{{- end }}
