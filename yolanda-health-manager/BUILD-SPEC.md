# BUILD-SPEC: Yolanda Evans Health Management System

**Version:** 1.0.0
**Target Platform:** macOS (Apple Silicon M1 Max native)
**Mission:** Build a secure, local-first Electron desktop application to aggregate, visualize, and analyze medical data for Yolanda Evans, enabling better health management and care coordination.

---

## EXECUTIVE SUMMARY

This specification defines the implementation of a desktop health management system that:
1. **Fetches** medical data from UPMC FHIR APIs (labs, conditions, medications, procedures)
2. **Displays** DICOM imaging studies (111 MRI files from VA Health system)
3. **Provides** AI-powered health assistant using xAI/Grok for plain-English medical explanations
4. **Stores** all data locally with encryption, zero cloud dependencies
5. **Operates** as a native macOS app optimized for Apple Silicon

**Primary User:** Family caregiver managing complex medical conditions
**Data Sources:** UPMC Health Plan FHIR R4 API, local DICOM files, PDF medical records
**Security Model:** OAuth2 tokens in macOS Keychain, SQLite with encryption, no network egress except UPMC API

---

## I. SYSTEM ARCHITECTURE

### 1.1 Technology Stack

```yaml
Application Framework:
  - Electron 28+ (native ARM64 build)
  - React 18.2+ (renderer process UI)
  - TypeScript 5+ (type safety for medical data)

Backend Services (Main Process):
  - Node.js 20+ LTS
  - Express 4.18+ (localhost API server)
  - better-sqlite3 9.2+ (local database)
  - node-fhir-client 2.5+ (UPMC API integration)

Python Bridge (Child Process):
  - Python 3.11+ (native ARM64)
  - xai-sdk (AI assistant - Grok API)
  - pydicom 2.4+ (DICOM processing)
  - Pillow 10.2+ (image conversion)

Frontend Libraries:
  - Cornerstone.js 2.6+ (DICOM viewer)
  - Recharts 2.10+ (lab trend visualization)
  - Tailwind CSS 3.4+ (medical-grade accessible UI)
  - date-fns 3.0+ (timeline calculations)

Security:
  - keytar 7.9+ (macOS Keychain integration)
  - SQLCipher (database encryption)
  - Electron context isolation enabled
  - CSP headers enforced
```

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ELECTRON RENDERER PROCESS                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │   Timeline   │  │ DICOM Viewer │  │   AI Chat Panel    │    │
│  │   Component  │  │ (Cornerstone)│  │   (xAI Grok)       │    │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘    │
│         │                 │                     │                │
│         └─────────────────┴─────────────────────┘                │
│                           │                                      │
│                    Electron IPC (contextBridge)                  │
│                           │                                      │
├───────────────────────────┼──────────────────────────────────────┤
│                    ELECTRON MAIN PROCESS                         │
│         ┌─────────────────┴─────────────────┐                   │
│         │                                   │                   │
│    ┌────▼────┐  ┌──────────┐  ┌────────────▼───────┐           │
│    │ Express │  │  SQLite  │  │  Python Bridge     │           │
│    │   API   │  │ Database │  │  (child_process)   │           │
│    └────┬────┘  └────┬─────┘  └────────┬───────────┘           │
│         │            │                  │                       │
│    ┌────▼────────────▼──────────────────▼───────┐               │
│    │         Data Orchestration Layer          │               │
│    │  - FHIR client (OAuth2 + token refresh)  │               │
│    │  - DICOM file loader (pydicom bridge)    │               │
│    │  - AI context builder (xAI SDK)          │               │
│    │  - Keychain access (keytar)              │               │
│    └────┬──────────────────────┬────────────────┘               │
│         │                      │                                │
└─────────┼──────────────────────┼────────────────────────────────┘
          │                      │
    ┌─────▼──────┐      ┌────────▼────────┐
    │ UPMC FHIR  │      │  xAI/Grok API   │
    │   API      │      │  (grok-beta)    │
    │ (OAuth2)   │      └─────────────────┘
    └────────────┘
```

### 1.3 Data Flow

```
User Action → Renderer Process → IPC → Main Process → Backend Service
                                                            ↓
                                                    External API / Local File
                                                            ↓
                                                      SQLite Cache
                                                            ↓
                                                    IPC Response
                                                            ↓
                                              Renderer Update (React)
```

---

## II. CORE FEATURES & IMPLEMENTATION

### 2.1 FHIR Data Integration

**Objective:** Fetch and sync medical records from UPMC Health Plan FHIR R4 API.

**Registration Requirements:**
- Register at: https://www.upmchealthplan.com/interop/api-access/
- Obtain: Client ID, Client Secret, Subscription Key
- Redirect URI: `http://localhost:8675/oauth/callback`

**OAuth2 Flow Implementation:**

```typescript
// src/main/fhir/oauth.ts
import { BrowserWindow } from 'electron';
import express from 'express';
import keytar from 'keytar';

const OAUTH_CONFIG = {
  authorizationEndpoint: 'https://apis.upmchp.com/authorize',
  tokenEndpoint: 'https://apis.upmchp.com/token',
  clientId: process.env.UPMC_CLIENT_ID,
  clientSecret: process.env.UPMC_CLIENT_SECRET,
  redirectUri: 'http://localhost:8675/oauth/callback',
  scopes: ['patient/*.read', 'launch/patient']
};

export async function initiateOAuthFlow(): Promise<void> {
  // 1. Start local callback server
  const app = express();
  const server = app.listen(8675);

  // 2. Generate authorization URL with PKCE
  const state = crypto.randomBytes(32).toString('hex');
  const codeVerifier = crypto.randomBytes(32).toString('base64url');
  const codeChallenge = crypto.createHash('sha256')
    .update(codeVerifier)
    .digest('base64url');

  const authUrl = new URL(OAUTH_CONFIG.authorizationEndpoint);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('client_id', OAUTH_CONFIG.clientId);
  authUrl.searchParams.set('redirect_uri', OAUTH_CONFIG.redirectUri);
  authUrl.searchParams.set('scope', OAUTH_CONFIG.scopes.join(' '));
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');

  // 3. Open system browser (not Electron window - more secure)
  const { shell } = require('electron');
  await shell.openExternal(authUrl.toString());

  // 4. Handle callback
  app.get('/oauth/callback', async (req, res) => {
    try {
      if (req.query.state !== state) {
        throw new Error('State mismatch - potential CSRF attack');
      }

      const code = req.query.code as string;

      // 5. Exchange code for tokens
      const tokenResponse = await fetch(OAUTH_CONFIG.tokenEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          code,
          redirect_uri: OAUTH_CONFIG.redirectUri,
          client_id: OAUTH_CONFIG.clientId,
          client_secret: OAUTH_CONFIG.clientSecret,
          code_verifier: codeVerifier
        })
      });

      const tokens = await tokenResponse.json();

      // 6. Store tokens in macOS Keychain
      await keytar.setPassword('yolanda-health', 'upmc_access_token', tokens.access_token);
      await keytar.setPassword('yolanda-health', 'upmc_refresh_token', tokens.refresh_token);
      await keytar.setPassword('yolanda-health', 'upmc_token_expiry',
        String(Date.now() + tokens.expires_in * 1000));

      res.send('<h1>Success!</h1><p>You can close this window.</p>');
      server.close();
    } catch (error) {
      res.status(500).send(`<h1>Error</h1><p>${error.message}</p>`);
      server.close();
    }
  });
}

export async function getAccessToken(): Promise<string> {
  const token = await keytar.getPassword('yolanda-health', 'upmc_access_token');
  const expiry = await keytar.getPassword('yolanda-health', 'upmc_token_expiry');

  // Check if token expired
  if (Date.now() >= parseInt(expiry)) {
    await refreshAccessToken();
    return getAccessToken(); // Recursive call after refresh
  }

  return token;
}

async function refreshAccessToken(): Promise<void> {
  const refreshToken = await keytar.getPassword('yolanda-health', 'upmc_refresh_token');

  const response = await fetch(OAUTH_CONFIG.tokenEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: OAUTH_CONFIG.clientId,
      client_secret: OAUTH_CONFIG.clientSecret
    })
  });

  const tokens = await response.json();

  await keytar.setPassword('yolanda-health', 'upmc_access_token', tokens.access_token);
  await keytar.setPassword('yolanda-health', 'upmc_token_expiry',
    String(Date.now() + tokens.expires_in * 1000));
}
```

**FHIR Data Sync:**

```typescript
// src/main/fhir/sync.ts
import Client from 'fhir-kit-client';
import { db } from '../database/sqlite';

const fhirClient = new Client({
  baseUrl: 'https://apis.upmchp.com/FHIR/R4',
  customHeaders: {
    'Ocp-Apim-Subscription-Key': process.env.UPMC_SUBSCRIPTION_KEY
  }
});

export async function syncMedicalData(): Promise<void> {
  const accessToken = await getAccessToken();
  fhirClient.bearerToken = accessToken;

  // 1. Fetch Patient resource
  const patient = await fhirClient.read({ resourceType: 'Patient', id: 'self' });
  db.upsertPatient(patient);

  // 2. Fetch Conditions (diagnoses)
  const conditions = await fhirClient.search({
    resourceType: 'Condition',
    searchParams: { patient: patient.id, _count: 100 }
  });
  db.upsertConditions(conditions.entry.map(e => e.resource));

  // 3. Fetch Observations (labs, vitals)
  const observations = await fhirClient.search({
    resourceType: 'Observation',
    searchParams: {
      patient: patient.id,
      category: 'laboratory',
      _sort: '-date',
      _count: 500
    }
  });
  db.upsertObservations(observations.entry.map(e => e.resource));

  // 4. Fetch MedicationRequest
  const medications = await fhirClient.search({
    resourceType: 'MedicationRequest',
    searchParams: { patient: patient.id, _count: 100 }
  });
  db.upsertMedications(medications.entry.map(e => e.resource));

  // 5. Fetch Procedures
  const procedures = await fhirClient.search({
    resourceType: 'Procedure',
    searchParams: { patient: patient.id, _count: 100 }
  });
  db.upsertProcedures(procedures.entry.map(e => e.resource));

  // Store last sync timestamp
  db.setMetadata('last_sync', new Date().toISOString());
}
```

### 2.2 SQLite Database Schema

```sql
-- src/main/database/schema.sql

-- Patient information
CREATE TABLE patients (
  id TEXT PRIMARY KEY,
  family_name TEXT,
  given_name TEXT,
  birth_date TEXT,
  gender TEXT,
  raw_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Medical conditions (diagnoses)
CREATE TABLE conditions (
  id TEXT PRIMARY KEY,
  patient_id TEXT REFERENCES patients(id),
  code TEXT,            -- ICD-10 code
  display TEXT,         -- "Thyroid nodule"
  clinical_status TEXT, -- "active", "resolved"
  onset_date TEXT,
  recorded_date TEXT,
  raw_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conditions_patient ON conditions(patient_id);
CREATE INDEX idx_conditions_date ON conditions(recorded_date DESC);

-- Laboratory observations
CREATE TABLE observations (
  id TEXT PRIMARY KEY,
  patient_id TEXT REFERENCES patients(id),
  code TEXT,              -- LOINC code (e.g., "2823-3" for Potassium)
  display TEXT,           -- "Potassium"
  value_quantity REAL,    -- 3.4
  value_unit TEXT,        -- "mmol/L"
  value_string TEXT,      -- For non-numeric values
  reference_low REAL,     -- 3.5
  reference_high REAL,    -- 5.0
  status TEXT,            -- "final", "preliminary"
  issued_date TEXT,       -- ISO 8601
  category TEXT,          -- "laboratory", "vital-signs"
  interpretation TEXT,    -- "L" (low), "N" (normal), "H" (high)
  raw_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_observations_patient ON observations(patient_id);
CREATE INDEX idx_observations_date ON observations(issued_date DESC);
CREATE INDEX idx_observations_code ON observations(code);

-- Medications
CREATE TABLE medications (
  id TEXT PRIMARY KEY,
  patient_id TEXT REFERENCES patients(id),
  medication_code TEXT,
  medication_display TEXT,
  status TEXT,              -- "active", "completed"
  intent TEXT,              -- "order", "plan"
  authored_date TEXT,
  dosage_text TEXT,
  raw_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medications_patient ON medications(patient_id);

-- Procedures
CREATE TABLE procedures (
  id TEXT PRIMARY KEY,
  patient_id TEXT REFERENCES patients(id),
  code TEXT,
  display TEXT,           -- "Fine-needle aspiration biopsy"
  status TEXT,            -- "completed", "in-progress"
  performed_date TEXT,
  raw_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_procedures_patient ON procedures(patient_id);
CREATE INDEX idx_procedures_date ON procedures(performed_date DESC);

-- DICOM imaging studies
CREATE TABLE imaging_studies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id TEXT REFERENCES patients(id),
  study_instance_uid TEXT UNIQUE,
  study_date TEXT,
  study_description TEXT,  -- "MRI Lumbar Spine"
  modality TEXT,           -- "MR", "CT", "XR"
  series_count INTEGER,
  file_path TEXT,          -- Path to DICOM directory
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE imaging_series (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  study_id INTEGER REFERENCES imaging_studies(id),
  series_instance_uid TEXT UNIQUE,
  series_number INTEGER,
  series_description TEXT,  -- "SAG T2 LDNE SHD"
  instance_count INTEGER,
  file_paths TEXT,          -- JSON array of DICOM file paths
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- AI chat history
CREATE TABLE chat_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id TEXT REFERENCES patients(id),
  role TEXT CHECK(role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  context_snapshot TEXT,   -- JSON of relevant medical data at time of chat
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_patient ON chat_messages(patient_id);
CREATE INDEX idx_chat_date ON chat_messages(created_at DESC);

-- Application metadata
CREATE TABLE metadata (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 DICOM Viewer Implementation

**Objective:** Display 111 MRI DICOM files with measurement/annotation tools.

```typescript
// src/renderer/components/DicomViewer.tsx
import React, { useEffect, useRef, useState } from 'react';
import * as cornerstone from 'cornerstone-core';
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import * as cornerstoneTools from 'cornerstone-tools';
import * as dicomParser from 'dicom-parser';

// Initialize cornerstone
cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
cornerstoneTools.external.cornerstone = cornerstone;

interface DicomViewerProps {
  studyId: number;
}

export const DicomViewer: React.FC<DicomViewerProps> = ({ studyId }) => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [currentSeries, setCurrentSeries] = useState<number>(0);
  const [currentImage, setCurrentImage] = useState<number>(0);
  const [seriesList, setSeriesList] = useState<any[]>([]);
  const [imageIds, setImageIds] = useState<string[]>([]);

  useEffect(() => {
    // Fetch series list for this study
    window.electron.invoke('dicom:getSeriesList', studyId)
      .then(series => {
        setSeriesList(series);
        if (series.length > 0) {
          loadSeries(series[0]);
        }
      });
  }, [studyId]);

  const loadSeries = async (series: any) => {
    const filePaths = JSON.parse(series.file_paths);
    const ids = filePaths.map(path => `dicomfile://${path}`);
    setImageIds(ids);
    setCurrentImage(0);

    if (elementRef.current && ids.length > 0) {
      cornerstone.enable(elementRef.current);

      // Load first image
      const image = await cornerstone.loadImage(ids[0]);
      cornerstone.displayImage(elementRef.current, image);

      // Enable tools
      const WwwcTool = cornerstoneTools.WwwcTool;
      const ZoomTool = cornerstoneTools.ZoomTool;
      const PanTool = cornerstoneTools.PanTool;
      const LengthTool = cornerstoneTools.LengthTool;
      const AngleTool = cornerstoneTools.AngleTool;

      cornerstoneTools.addTool(WwwcTool);
      cornerstoneTools.addTool(ZoomTool);
      cornerstoneTools.addTool(PanTool);
      cornerstoneTools.addTool(LengthTool);
      cornerstoneTools.addTool(AngleTool);

      cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 }); // Left click
      cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 2 }); // Right click
      cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 4 });  // Middle click
    }
  };

  const navigateImage = async (delta: number) => {
    const newIndex = Math.max(0, Math.min(imageIds.length - 1, currentImage + delta));
    setCurrentImage(newIndex);

    if (elementRef.current) {
      const image = await cornerstone.loadImage(imageIds[newIndex]);
      cornerstone.displayImage(elementRef.current, image);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Series selector */}
      <div className="bg-gray-800 p-2 flex gap-2 overflow-x-auto">
        {seriesList.map((series, idx) => (
          <button
            key={series.id}
            onClick={() => { setCurrentSeries(idx); loadSeries(series); }}
            className={`px-3 py-1 rounded ${currentSeries === idx ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            {series.series_description}
          </button>
        ))}
      </div>

      {/* DICOM viewport */}
      <div className="flex-1 relative bg-black">
        <div ref={elementRef} className="w-full h-full" />

        {/* Image counter overlay */}
        <div className="absolute top-2 left-2 bg-black/50 text-white px-2 py-1 rounded">
          Image {currentImage + 1} / {imageIds.length}
        </div>

        {/* Window/Level preset buttons */}
        <div className="absolute top-2 right-2 flex gap-2">
          <button className="bg-gray-700 px-3 py-1 rounded text-sm">Soft Tissue</button>
          <button className="bg-gray-700 px-3 py-1 rounded text-sm">Bone</button>
          <button className="bg-gray-700 px-3 py-1 rounded text-sm">Brain</button>
        </div>
      </div>

      {/* Navigation controls */}
      <div className="bg-gray-800 p-2 flex justify-center gap-4">
        <button onClick={() => navigateImage(-1)} className="px-4 py-2 bg-blue-600 rounded">
          ← Previous
        </button>
        <button onClick={() => navigateImage(1)} className="px-4 py-2 bg-blue-600 rounded">
          Next →
        </button>
      </div>

      {/* Tool controls */}
      <div className="bg-gray-800 p-2 flex gap-2">
        <button className="px-3 py-1 bg-gray-700 rounded">Length</button>
        <button className="px-3 py-1 bg-gray-700 rounded">Angle</button>
        <button className="px-3 py-1 bg-gray-700 rounded">Annotate</button>
        <button className="px-3 py-1 bg-gray-700 rounded">Reset</button>
      </div>
    </div>
  );
};
```

**DICOM Loading via Python Bridge:**

```python
# src/python/dicom_loader.py
import sys
import json
import pydicom
from pathlib import Path

def get_dicom_metadata(file_path: str) -> dict:
    """Extract DICOM metadata without loading pixel data."""
    ds = pydicom.dcmread(file_path, stop_before_pixels=True)

    return {
        'studyInstanceUID': str(ds.StudyInstanceUID),
        'seriesInstanceUID': str(ds.SeriesInstanceUID),
        'studyDate': str(ds.StudyDate),
        'studyDescription': str(ds.get('StudyDescription', '')),
        'seriesNumber': int(ds.SeriesNumber),
        'seriesDescription': str(ds.get('SeriesDescription', '')),
        'modality': str(ds.Modality),
        'instanceNumber': int(ds.InstanceNumber)
    }

def scan_dicom_directory(directory: str) -> dict:
    """Scan directory and organize DICOM files by study/series."""
    studies = {}

    for dcm_file in Path(directory).rglob('*'):
        if dcm_file.is_file():
            try:
                meta = get_dicom_metadata(str(dcm_file))
                study_uid = meta['studyInstanceUID']
                series_uid = meta['seriesInstanceUID']

                if study_uid not in studies:
                    studies[study_uid] = {
                        'studyDate': meta['studyDate'],
                        'studyDescription': meta['studyDescription'],
                        'series': {}
                    }

                if series_uid not in studies[study_uid]['series']:
                    studies[study_uid]['series'][series_uid] = {
                        'seriesNumber': meta['seriesNumber'],
                        'seriesDescription': meta['seriesDescription'],
                        'modality': meta['modality'],
                        'files': []
                    }

                studies[study_uid]['series'][series_uid]['files'].append({
                    'path': str(dcm_file),
                    'instanceNumber': meta['instanceNumber']
                })
            except Exception as e:
                # Skip non-DICOM files
                continue

    # Sort files by instance number
    for study in studies.values():
        for series in study['series'].values():
            series['files'].sort(key=lambda x: x['instanceNumber'])

    return studies

if __name__ == '__main__':
    command = sys.argv[1]

    if command == 'scan':
        directory = sys.argv[2]
        result = scan_dicom_directory(directory)
        print(json.dumps(result))
    elif command == 'metadata':
        file_path = sys.argv[2]
        result = get_dicom_metadata(file_path)
        print(json.dumps(result))
```

### 2.4 AI Health Assistant

**Objective:** Provide conversational medical explanations using xAI Grok.

```python
# src/python/ai_assistant.py
import os
import json
import sys
from openai import OpenAI  # xAI uses OpenAI-compatible API

client = OpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)

def build_medical_context(patient_data: dict) -> str:
    """Build context string from patient's medical data."""
    context_parts = [
        "You are a medical information assistant for Yolanda Evans.",
        "Provide explanations in plain English, avoiding medical jargon when possible.",
        "Always cite specific data points when answering questions.",
        "",
        "## Patient Information",
        f"Name: {patient_data.get('name', 'Yolanda Evans')}",
        f"DOB: {patient_data.get('birthDate', 'N/A')}",
        "",
        "## Active Conditions"
    ]

    for condition in patient_data.get('conditions', []):
        context_parts.append(
            f"- {condition['display']} (Status: {condition['status']}, "
            f"Since: {condition.get('onsetDate', 'unknown')})"
        )

    context_parts.extend(["", "## Recent Laboratory Results"])

    for obs in patient_data.get('recentLabs', []):
        ref_range = f"{obs.get('refLow', '?')}-{obs.get('refHigh', '?')} {obs['unit']}"
        flag = "🔴" if obs.get('interpretation') in ['L', 'H'] else "✅"
        context_parts.append(
            f"{flag} {obs['display']}: {obs['value']} {obs['unit']} "
            f"(Normal: {ref_range}) - {obs['date']}"
        )

    context_parts.extend(["", "## Recent Procedures"])

    for proc in patient_data.get('recentProcedures', []):
        context_parts.append(f"- {proc['display']} on {proc['date']}")

    context_parts.extend([
        "",
        "## Guidelines",
        "- Do not provide medical advice or treatment recommendations",
        "- Encourage patient to discuss concerns with their healthcare provider",
        "- Explain test results and medical terminology clearly",
        "- Acknowledge when information is outside your scope"
    ])

    return "\n".join(context_parts)

def chat(user_message: str, patient_data: dict, conversation_history: list) -> str:
    """Generate AI response with medical context."""

    system_context = build_medical_context(patient_data)

    messages = [
        {"role": "system", "content": system_context}
    ]

    # Add conversation history (last 10 messages)
    messages.extend(conversation_history[-10:])

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error communicating with AI service: {str(e)}"

if __name__ == '__main__':
    # Read stdin for patient data and user message
    input_data = json.loads(sys.stdin.read())

    response = chat(
        user_message=input_data['message'],
        patient_data=input_data['patientData'],
        conversation_history=input_data['history']
    )

    print(json.dumps({"response": response}))
```

**IPC Handler in Main Process:**

```typescript
// src/main/ipc/ai-chat.ts
import { ipcMain } from 'electron';
import { spawn } from 'child_process';
import { db } from '../database/sqlite';

ipcMain.handle('ai:sendMessage', async (event, message: string) => {
  // 1. Get patient data from database
  const patientData = {
    name: 'Yolanda Evans',
    birthDate: db.getPatientBirthDate(),
    conditions: db.getActiveConditions(),
    recentLabs: db.getRecentObservations(30), // Last 30 days
    recentProcedures: db.getRecentProcedures(90) // Last 90 days
  };

  // 2. Get conversation history
  const history = db.getChatHistory(20); // Last 20 messages

  // 3. Call Python AI assistant
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [
      'src/python/ai_assistant.py'
    ], {
      env: {
        ...process.env,
        XAI_API_KEY: process.env.XAI_API_KEY
      }
    });

    const inputData = JSON.stringify({
      message,
      patientData,
      history: history.map(h => ({ role: h.role, content: h.content }))
    });

    python.stdin.write(inputData);
    python.stdin.end();

    let outputData = '';
    python.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        const result = JSON.parse(outputData);

        // 4. Save to chat history
        db.insertChatMessage('user', message, JSON.stringify(patientData));
        db.insertChatMessage('assistant', result.response, null);

        resolve(result.response);
      } else {
        reject(new Error('Python process failed'));
      }
    });
  });
});
```

### 2.5 Timeline Visualization

```typescript
// src/renderer/components/Timeline.tsx
import React, { useEffect, useState } from 'react';
import { format, parseISO } from 'date-fns';

interface TimelineEvent {
  id: string;
  type: 'lab' | 'procedure' | 'condition' | 'medication';
  date: string;
  title: string;
  details: string;
  isAbnormal?: boolean;
}

export const Timeline: React.FC = () => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    window.electron.invoke('timeline:getEvents').then(setEvents);
  }, []);

  return (
    <div className="p-4 overflow-y-auto">
      <h2 className="text-2xl font-bold mb-4">Medical Timeline</h2>

      <div className="relative border-l-2 border-gray-300 ml-4">
        {events.map(event => (
          <div key={event.id} className="mb-8 ml-6">
            {/* Timeline dot */}
            <div className={`absolute w-4 h-4 rounded-full -left-2 border-2 border-white ${
              event.isAbnormal ? 'bg-red-500' :
              event.type === 'procedure' ? 'bg-blue-500' :
              event.type === 'medication' ? 'bg-green-500' :
              'bg-gray-400'
            }`} />

            {/* Event card */}
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg">{event.title}</h3>
                <span className="text-sm text-gray-500">
                  {format(parseISO(event.date), 'MMM dd, yyyy')}
                </span>
              </div>

              <p className="text-gray-700">{event.details}</p>

              <div className="mt-2">
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                  event.type === 'lab' ? 'bg-purple-100 text-purple-800' :
                  event.type === 'procedure' ? 'bg-blue-100 text-blue-800' :
                  event.type === 'condition' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {event.type.toUpperCase()}
                </span>

                {event.isAbnormal && (
                  <span className="ml-2 inline-block px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                    ABNORMAL
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## III. SECURITY IMPLEMENTATION

### 3.1 Security Checklist

- ✅ **OAuth2 with PKCE** for FHIR API authentication
- ✅ **macOS Keychain** for token storage (never in localStorage)
- ✅ **SQLCipher** for database encryption at rest
- ✅ **Context isolation** enabled in Electron
- ✅ **Node integration** disabled in renderer process
- ✅ **CSP headers** enforced
- ✅ **No remote content** loading (all assets bundled)
- ✅ **IPC whitelisting** (explicit allowed channels only)
- ✅ **Audit logging** for data access
- ✅ **FileVault** requirement check on startup

### 3.2 Electron Security Configuration

```typescript
// src/main/main.ts
import { app, BrowserWindow } from 'electron';
import * as path from 'path';

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,        // CRITICAL: Disable Node in renderer
      contextIsolation: true,         // CRITICAL: Enable context isolation
      sandbox: true,                  // Enable sandbox
      preload: path.join(__dirname, 'preload.js'),
      devTools: process.env.NODE_ENV === 'development'
    }
  });

  // CSP headers
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; " +
          "script-src 'self'; " +
          "style-src 'self' 'unsafe-inline'; " +
          "img-src 'self' data:; " +
          "connect-src 'self' https://apis.upmchp.com https://api.x.ai; " +
          "font-src 'self'; " +
          "object-src 'none'; " +
          "base-uri 'self'"
        ]
      }
    });
  });

  // Prevent navigation to external sites
  mainWindow.webContents.on('will-navigate', (event) => {
    event.preventDefault();
  });

  mainWindow.loadFile('index.html');
};

app.whenReady().then(() => {
  // Check FileVault status (macOS)
  const { execSync } = require('child_process');
  try {
    const fvStatus = execSync('fdesetup status').toString();
    if (!fvStatus.includes('FileVault is On')) {
      console.warn('WARNING: FileVault is not enabled. Medical data should be encrypted at rest.');
    }
  } catch (e) {
    console.error('Could not check FileVault status');
  }

  createWindow();
});
```

### 3.3 IPC Security

```typescript
// src/main/preload.ts
import { contextBridge, ipcRenderer } from 'electron';

// Whitelist of allowed IPC channels
const ALLOWED_CHANNELS = {
  invoke: [
    'timeline:getEvents',
    'fhir:sync',
    'fhir:getObservations',
    'dicom:getSeriesList',
    'dicom:getSeries',
    'ai:sendMessage'
  ],
  on: [
    'sync:progress',
    'sync:complete'
  ]
};

contextBridge.exposeInMainWorld('electron', {
  invoke: (channel: string, ...args: any[]) => {
    if (!ALLOWED_CHANNELS.invoke.includes(channel)) {
      throw new Error(`IPC channel ${channel} not allowed`);
    }
    return ipcRenderer.invoke(channel, ...args);
  },
  on: (channel: string, callback: Function) => {
    if (!ALLOWED_CHANNELS.on.includes(channel)) {
      throw new Error(`IPC channel ${channel} not allowed`);
    }
    ipcRenderer.on(channel, (event, ...args) => callback(...args));
  }
});
```

---

## IV. BUILD & DEPLOYMENT

### 4.1 Development Setup

```bash
# Clone repository
cd ~/IdeaProjects/yolanda-evans

# Install Node dependencies
npm install

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with:
# - UPMC_CLIENT_ID
# - UPMC_CLIENT_SECRET
# - UPMC_SUBSCRIPTION_KEY
# - XAI_API_KEY

# Initialize database
npm run db:init

# Import DICOM files
npm run dicom:import ../VA-Health/0001/01

# Start development server
npm run dev
```

### 4.2 Build Configuration

```json
// package.json (relevant scripts)
{
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc -p tsconfig.main.json && electron .",
    "build": "npm run build:renderer && npm run build:main",
    "build:renderer": "vite build",
    "build:main": "tsc -p tsconfig.main.json",
    "package": "electron-builder --mac --arm64",
    "db:init": "node scripts/init-database.js",
    "dicom:import": "node scripts/import-dicom.js"
  },
  "build": {
    "appId": "com.yolandacare.healthmanager",
    "productName": "Yolanda Health Manager",
    "mac": {
      "target": {
        "target": "dmg",
        "arch": ["arm64"]
      },
      "category": "public.app-category.healthcare-fitness",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "files": [
      "dist/**/*",
      "src/python/**/*",
      "package.json"
    ],
    "extraResources": [
      {
        "from": ".venv",
        "to": "python-runtime"
      }
    ]
  }
}
```

### 4.3 Production Build

```bash
# Clean build
rm -rf dist/ out/

# Build application
npm run build

# Package for macOS (Apple Silicon)
npm run package

# Output: out/Yolanda Health Manager-1.0.0-arm64.dmg
```

### 4.4 macOS Entitlements

```xml
<!-- build/entitlements.mac.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>
  <key>com.apple.security.cs.disable-library-validation</key>
  <true/>
  <key>com.apple.security.network.client</key>
  <true/>
  <key>com.apple.security.files.user-selected.read-write</key>
  <true/>
  <key>com.apple.security.keychain-access-groups</key>
  <array>
    <string>$(AppIdentifierPrefix)com.yolandacare.healthmanager</string>
  </array>
</dict>
</plist>
```

---

## V. TESTING STRATEGY

### 5.1 Unit Tests

```typescript
// __tests__/fhir/oauth.test.ts
import { describe, it, expect, vi } from 'vitest';
import { getAccessToken, refreshAccessToken } from '../../src/main/fhir/oauth';
import * as keytar from 'keytar';

vi.mock('keytar');

describe('OAuth Token Management', () => {
  it('should return valid token if not expired', async () => {
    vi.mocked(keytar.getPassword)
      .mockResolvedValueOnce('mock_access_token')
      .mockResolvedValueOnce(String(Date.now() + 3600000)); // 1 hour future

    const token = await getAccessToken();
    expect(token).toBe('mock_access_token');
  });

  it('should refresh token if expired', async () => {
    vi.mocked(keytar.getPassword)
      .mockResolvedValueOnce('expired_token')
      .mockResolvedValueOnce(String(Date.now() - 1000)) // Expired
      .mockResolvedValueOnce('refresh_token_value');

    global.fetch = vi.fn().mockResolvedValue({
      json: async () => ({
        access_token: 'new_access_token',
        expires_in: 3600
      })
    });

    const token = await getAccessToken();
    expect(keytar.setPassword).toHaveBeenCalledWith(
      'yolanda-health',
      'upmc_access_token',
      'new_access_token'
    );
  });
});
```

### 5.2 Integration Tests

```typescript
// __tests__/integration/fhir-sync.test.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { syncMedicalData } from '../../src/main/fhir/sync';
import { db } from '../../src/main/database/sqlite';

describe('FHIR Sync Integration', () => {
  beforeAll(() => {
    db.init(':memory:'); // Use in-memory DB for tests
  });

  it('should fetch and store patient observations', async () => {
    // Mock FHIR client responses
    const mockObservations = {
      entry: [
        {
          resource: {
            id: 'obs-1',
            code: { coding: [{ code: '2823-3', display: 'Potassium' }] },
            valueQuantity: { value: 3.4, unit: 'mmol/L' },
            effectiveDateTime: '2025-10-13T10:00:00Z'
          }
        }
      ]
    };

    // ... mock setup ...

    await syncMedicalData();

    const observations = db.getObservations();
    expect(observations).toHaveLength(1);
    expect(observations[0].code).toBe('2823-3');
    expect(observations[0].value_quantity).toBe(3.4);
  });
});
```

### 5.3 End-to-End Tests

```typescript
// __tests__/e2e/timeline.spec.ts
import { test, expect } from '@playwright/test';
import { _electron as electron } from 'playwright';

test('Timeline displays recent medical events', async () => {
  const app = await electron.launch({ args: ['.'] });
  const window = await app.firstWindow();

  // Navigate to timeline
  await window.click('text=Timeline');

  // Verify events are displayed
  await expect(window.locator('.timeline-event')).toHaveCount(10);

  // Verify date sorting (most recent first)
  const dates = await window.locator('.timeline-event .date').allTextContents();
  expect(dates[0]).toContain('Nov 13');
  expect(dates[9]).toContain('Aug 26');

  await app.close();
});
```

---

## VI. PROJECT MILESTONES

### Phase 1: Foundation (Weeks 1-2)
- ✅ Electron + React scaffolding
- ✅ SQLite database initialization
- ✅ Python bridge functional
- ✅ Basic UI layout (timeline, viewer, chat panels)

**Acceptance Criteria:**
- App launches without errors
- Database creates all tables successfully
- Python bridge executes test script and returns JSON
- UI renders three main panels (empty, but structured)

### Phase 2: FHIR Integration (Weeks 3-4)
- ✅ UPMC Health Plan API registration complete
- ✅ OAuth2 flow implemented and tested
- ✅ FHIR sync retrieves Patient, Condition, Observation resources
- ✅ Timeline displays real lab results

**Acceptance Criteria:**
- OAuth flow completes in system browser
- Tokens stored in Keychain
- At least 20 observations fetched and displayed
- Timeline shows events in chronological order
- Automatic token refresh works (verify after 1 hour)

### Phase 3: DICOM Viewer (Week 5)
- ✅ DICOM files imported to database
- ✅ Cornerstone.js integrated
- ✅ Series navigation functional
- ✅ Window/level adjustment works

**Acceptance Criteria:**
- All 111 DICOM files load successfully
- User can switch between 5 series
- Mouse wheel navigates through images
- Window/level presets apply correctly

### Phase 4: AI Assistant (Week 6)
- ✅ xAI API integration complete
- ✅ Chat interface functional
- ✅ AI responses cite patient data
- ✅ Conversation history persisted

**Acceptance Criteria:**
- AI responds within 5 seconds
- Responses reference specific lab values from database
- Chat history persists across app restarts
- Error handling graceful if API unavailable

### Phase 5: Polish & Deployment (Weeks 7-8)
- ✅ UI/UX refinement (accessibility, dark mode)
- ✅ Export functionality (PDF reports)
- ✅ Auto-update mechanism
- ✅ DMG installer created

**Acceptance Criteria:**
- App passes WCAG 2.1 AA accessibility audit
- PDF export includes timeline + recent labs
- DMG installs without warnings on clean M1 Mac
- Auto-update downloads and installs successfully

---

## VII. RISK MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| UPMC API rate limiting | High | Medium | Implement exponential backoff, cache aggressively, sync max 1x/hour |
| xAI API downtime | Medium | Low | Fallback to cached responses, display "AI temporarily unavailable" |
| DICOM rendering performance | Medium | Medium | Implement progressive loading, cache thumbnails, use web workers |
| OAuth token expiration during use | Low | High | Preemptive refresh at 80% token lifetime, queue requests during refresh |
| macOS security warnings on launch | High | Medium | Code sign with Apple Developer ID, notarize DMG |
| Database corruption | High | Low | Daily SQLite backup to `~/Documents/Yolanda Health Backups/` |
| Python dependency conflicts | Medium | Medium | Bundle Python runtime with app, pin all versions in requirements.txt |

---

## VIII. SUCCESS METRICS

**Technical:**
- ✅ App startup time < 3 seconds on M1 Max
- ✅ FHIR sync completes in < 30 seconds for 500 observations
- ✅ DICOM image loads in < 500ms
- ✅ AI response latency < 5 seconds (p95)
- ✅ Memory usage < 500MB at idle, < 2GB with all DICOM loaded
- ✅ Zero unhandled exceptions in production (sentry.io monitoring)

**User Experience:**
- ✅ Caregiver can answer question "What were mom's potassium levels last month?" in < 10 seconds
- ✅ Can navigate to specific MRI image showing L5-S1 herniation in < 15 seconds
- ✅ AI provides actionable explanation of thyroid biopsy results in plain English
- ✅ No need to reference paper records or multiple web portals

---

## IX. MAINTENANCE PLAN

**Monthly:**
- Review FHIR sync logs for errors
- Update dependencies (security patches only)
- Backup database to external drive

**Quarterly:**
- Review xAI API usage/costs
- Update FHIR resource mappings if UPMC changes schema
- User testing session with primary caregiver

**Annually:**
- Major dependency updates (Electron, React, Cornerstone.js)
- Re-audit security (penetration test)
- Review and archive old medical data (>2 years)

---

## X. CONCLUSION

This specification defines a **secure, local-first, caregiver-focused health management application** that consolidates fragmented medical data into a single, accessible interface. By leveraging FHIR APIs, DICOM standards, and AI assistance, the system reduces cognitive load on caregivers and improves health literacy.

**Key Differentiators:**
- 100% local data storage (zero cloud risk)
- Native Apple Silicon performance
- AI explanations grounded in actual patient data
- Professional DICOM viewer (not just image thumbnails)

**Next Steps:**
1. Review this spec with peer LLMs (Gemini, DeepSeek, Codex)
2. Incorporate feedback
3. Begin Phase 1 implementation
4. Register UPMC API credentials (critical path item)

**Estimated Total Development Time:** 8 weeks part-time (20 hrs/week)
**Estimated Total Cost:** $0 software + $25/month xAI API (estimated)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01-15
**Author:** Claude Code (Sonnet 4.5)
**Reviewer:** Pending (Gemini, Grok, DeepSeek, Codex, Copilot)
