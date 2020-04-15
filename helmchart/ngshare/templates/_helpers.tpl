{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "ngshare.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ngshare.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ngshare.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "ngshare.labels" -}}
helm.sh/chart: {{ include "ngshare.chart" . }}
{{ include "ngshare.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "ngshare.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ngshare.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- $_ := set . "ngshare_random_token" (randAlphaNum 32) -}}
{{- define "ngshare.getToken" -}}
{{- if .Values.ngshare.hub_api_token -}}
{{- .Values.ngshare.hub_api_token -}}
{{- else if (get . "ngshare_random_token") -}}
{{- get . "ngshare_random_token" -}}
{{- else -}}
{{- $_ := set . "ngshare_random_token" (randAlphaNum 32) -}}
{{- get . "ngshare_random_token" -}}
{{- end -}}
{{- end -}}
