/**
 * LegalMetriX - Client Application Logic
 * Packaged Commodity Compliance, Authenticity & PDF Report System (Phase 1, 2 & 3)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements - Single Mode
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const previewContainer = document.getElementById('previewContainer');
  const previewImg = document.getElementById('previewImg');
  const previewFilename = document.getElementById('previewFilename');
  const previewMeta = document.getElementById('previewMeta');
  const clearBtn = document.getElementById('clearBtn');

  // Elements - Dual Mode
  const modeSingleTab = document.getElementById('modeSingleTab');
  const modeDualTab = document.getElementById('modeDualTab');
  const singleUploadSection = document.getElementById('singleUploadSection');
  const dualUploadSection = document.getElementById('dualUploadSection');
  const modeHelpText = document.getElementById('modeHelpText');

  const frontDropzone = document.getElementById('frontDropzone');
  const fileInputFront = document.getElementById('fileInputFront');
  const frontPreviewContainer = document.getElementById('frontPreviewContainer');
  const frontPreviewImg = document.getElementById('frontPreviewImg');
  const frontPreviewFilename = document.getElementById('frontPreviewFilename');
  const frontPreviewMeta = document.getElementById('frontPreviewMeta');
  const frontClearBtn = document.getElementById('frontClearBtn');

  const backDropzone = document.getElementById('backDropzone');
  const fileInputBack = document.getElementById('fileInputBack');
  const backPreviewContainer = document.getElementById('backPreviewContainer');
  const backPreviewImg = document.getElementById('backPreviewImg');
  const backPreviewFilename = document.getElementById('backPreviewFilename');
  const backPreviewMeta = document.getElementById('backPreviewMeta');
  const backClearBtn = document.getElementById('backClearBtn');

  // Mismatch Modal Elements
  const mismatchModalOverlay = document.getElementById('mismatchModalOverlay');
  const mismatchScoreVal = document.getElementById('mismatchScoreVal');
  const mismatchSummary = document.getElementById('mismatchSummary');
  const mismatchDiscrepanciesList = document.getElementById('mismatchDiscrepanciesList');
  const mismatchCloseBtn = document.getElementById('mismatchCloseBtn');

  // General App Elements
  const scanBtn = document.getElementById('scanBtn');
  const uploadSection = document.getElementById('uploadSection');
  const resultsContainer = document.getElementById('resultsContainer');
  const newScanBtn = document.getElementById('newScanBtn');
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');
  const printBtn = document.getElementById('printBtn');
  const geminiKeyInput = document.getElementById('geminiKeyInput');

  // Loading Overlay
  const loadingOverlay = document.getElementById('loadingOverlay');
  const loadingStageText = document.getElementById('loadingStageText');
  const progressBarFill = document.getElementById('progressBarFill');
  const loadingSubtext = document.getElementById('loadingSubtext');

  // App State
  let currentScanMode = 'single';
  let selectedFile = null;
  let selectedFileFront = null;
  let selectedFileBack = null;
  let currentReportData = null;

  // Staged loading texts
  const STAGES = [
    { text: "Preparing image & validating resolution...", pct: 15, sub: "Analyzing pixel sharpness..." },
    { text: "Multimodal AI extraction via Gemini Vision...", pct: 40, sub: "Extracting brand, product, MRP, net qty, dates..." },
    { text: "Automated Cross-Panel Coherence Gatekeeper...", pct: 60, sub: "Checking brand alignment & category continuity..." },
    { text: "Running Legal Metrology Rules 2011 engine...", pct: 75, sub: "Evaluating statutory Rule 6, 10, 11-13 clauses..." },
    { text: "Gathering web research & market evidence...", pct: 90, sub: "Checking brand existence & alternatives..." },
    { text: "Generating Inspection Report & PDF...", pct: 100, sub: "Compiling preliminary screening document..." }
  ];

  // =========================================================================
  // Mode Switcher Logic
  // =========================================================================
  function switchScanMode(mode) {
    currentScanMode = mode;
    if (mode === 'dual') {
      modeSingleTab.classList.remove('active');
      modeDualTab.classList.add('active');
      singleUploadSection.style.display = 'none';
      dualUploadSection.style.display = 'block';
      modeHelpText.textContent = 'Guided dual-view capture: Slot 1 for Front PDP (Brand & Net Qty), Slot 2 for Back Info Panel (MRP, Mfg, Ingredients).';
    } else {
      modeDualTab.classList.remove('active');
      modeSingleTab.classList.add('active');
      dualUploadSection.style.display = 'none';
      singleUploadSection.style.display = 'block';
      modeHelpText.textContent = 'Single-view capture for Principal Display Panel (PDP) or flat unfolded packaging.';
    }
    updateScanButtonState();
  }

  if (modeSingleTab) modeSingleTab.addEventListener('click', () => switchScanMode('single'));
  if (modeDualTab) modeDualTab.addEventListener('click', () => switchScanMode('dual'));

  function updateScanButtonState() {
    if (currentScanMode === 'single') {
      scanBtn.disabled = !selectedFile;
    } else {
      scanBtn.disabled = !(selectedFileFront && selectedFileBack);
    }
  }

  // =========================================================================
  // Dropzone Setup Helpers
  // =========================================================================
  function bindDropzoneEvents(zoneElem, onFileSelected) {
    if (!zoneElem) return;
    ['dragenter', 'dragover'].forEach(eventName => {
      zoneElem.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        zoneElem.classList.add('dragover');
      });
    });
    ['dragleave', 'drop'].forEach(eventName => {
      zoneElem.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        zoneElem.classList.remove('dragover');
      });
    });
    zoneElem.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        onFileSelected(dt.files[0]);
      }
    });
  }

  // Single Panel Dropzone
  bindDropzoneEvents(dropzone, handleFileSelection);
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    if (!file.type.match('image.*')) {
      alert('Please upload a valid image file (JPG, JPEG, PNG, or WEBP).');
      return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFilename.textContent = file.name;
      previewMeta.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB • ${file.type}`;
      previewContainer.style.display = 'block';
      updateScanButtonState();
    };
    reader.readAsDataURL(file);
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      selectedFile = null;
      if (fileInput) fileInput.value = '';
      previewContainer.style.display = 'none';
      updateScanButtonState();
    });
  }

  // Dual Panel: Slot 1 Front PDP
  bindDropzoneEvents(frontDropzone, handleFrontSelection);
  if (fileInputFront) {
    fileInputFront.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFrontSelection(e.target.files[0]);
      }
    });
  }

  function handleFrontSelection(file) {
    if (!file.type.match('image.*')) {
      alert('Please upload a valid image file (JPG, JPEG, PNG, or WEBP).');
      return;
    }
    selectedFileFront = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      frontPreviewImg.src = e.target.result;
      frontPreviewFilename.textContent = file.name;
      frontPreviewMeta.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB • Front PDP`;
      frontPreviewContainer.style.display = 'block';
      updateScanButtonState();
    };
    reader.readAsDataURL(file);
  }

  if (frontClearBtn) {
    frontClearBtn.addEventListener('click', () => {
      selectedFileFront = null;
      if (fileInputFront) fileInputFront.value = '';
      frontPreviewContainer.style.display = 'none';
      updateScanButtonState();
    });
  }

  // Dual Panel: Slot 2 Back Info
  bindDropzoneEvents(backDropzone, handleBackSelection);
  if (fileInputBack) {
    fileInputBack.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleBackSelection(e.target.files[0]);
      }
    });
  }

  function handleBackSelection(file) {
    if (!file.type.match('image.*')) {
      alert('Please upload a valid image file (JPG, JPEG, PNG, or WEBP).');
      return;
    }
    selectedFileBack = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      backPreviewImg.src = e.target.result;
      backPreviewFilename.textContent = file.name;
      backPreviewMeta.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB • Back Info`;
      backPreviewContainer.style.display = 'block';
      updateScanButtonState();
    };
    reader.readAsDataURL(file);
  }

  if (backClearBtn) {
    backClearBtn.addEventListener('click', () => {
      selectedFileBack = null;
      if (fileInputBack) fileInputBack.value = '';
      backPreviewContainer.style.display = 'none';
      updateScanButtonState();
    });
  }

  function resetUploadState() {
    selectedFile = null;
    selectedFileFront = null;
    selectedFileBack = null;
    if (fileInput) fileInput.value = '';
    if (fileInputFront) fileInputFront.value = '';
    if (fileInputBack) fileInputBack.value = '';
    previewContainer.style.display = 'none';
    frontPreviewContainer.style.display = 'none';
    backPreviewContainer.style.display = 'none';
    updateScanButtonState();
  }

  // =========================================================================
  // Mismatch Modal Handling
  // =========================================================================
  function showMismatchModal(coherence, message) {
    if (!mismatchModalOverlay) return;
    if (coherence) {
      mismatchScoreVal.textContent = `${coherence.coherence_score !== undefined ? coherence.coherence_score : 0}%`;
      mismatchSummary.textContent = coherence.verdict_summary || message || "Conflicting product panels detected.";
      mismatchDiscrepanciesList.innerHTML = '';
      const list = coherence.discrepancies || [];
      if (list.length > 0) {
        list.forEach(disc => {
          const li = document.createElement('li');
          li.textContent = disc;
          mismatchDiscrepanciesList.appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.textContent = "Discrepancy detected in product brand identity, commodity category, or pack size.";
        mismatchDiscrepanciesList.appendChild(li);
      }
    } else {
      mismatchScoreVal.textContent = "0%";
      mismatchSummary.textContent = message || "Cross-panel mismatch detected.";
      mismatchDiscrepanciesList.innerHTML = '<li>Cross-commodity inspection blocked to prevent label contamination.</li>';
    }
    mismatchModalOverlay.style.display = 'flex';
  }

  if (mismatchCloseBtn) {
    mismatchCloseBtn.addEventListener('click', () => {
      mismatchModalOverlay.style.display = 'none';
    });
  }

  if (mismatchModalOverlay) {
    mismatchModalOverlay.addEventListener('click', (e) => {
      if (e.target === mismatchModalOverlay) {
        mismatchModalOverlay.style.display = 'none';
      }
    });
  }

  // =========================================================================
  // 1. LIVE CAMERA SCANNER LOGIC
  // =========================================================================
  let activeMediaStream = null;
  let currentCameraTarget = 'single'; // 'single', 'front', 'back'

  const cameraModalOverlay = document.getElementById('cameraModalOverlay');
  const cameraVideo = document.getElementById('cameraVideo');
  const cameraCanvas = document.getElementById('cameraCanvas');
  const cameraSnapBtn = document.getElementById('cameraSnapBtn');
  const cameraCancelBtn = document.getElementById('cameraCancelBtn');
  const cameraCloseXBtn = document.getElementById('cameraCloseXBtn');
  const cameraSourceSelect = document.getElementById('cameraSourceSelect');
  const cameraSlotTarget = document.getElementById('cameraSlotTarget');

  const openCameraSingleBtn = document.getElementById('openCameraSingleBtn');
  const openCameraFrontBtn = document.getElementById('openCameraFrontBtn');
  const openCameraBackBtn = document.getElementById('openCameraBackBtn');

  async function openCamera(target) {
    currentCameraTarget = target;
    if (cameraSlotTarget) {
      if (target === 'front') cameraSlotTarget.textContent = 'Target: Slot 1 (Front PDP)';
      else if (target === 'back') cameraSlotTarget.textContent = 'Target: Slot 2 (Back Info Panel)';
      else cameraSlotTarget.textContent = 'Target: Single Panel';
    }

    if (cameraModalOverlay) cameraModalOverlay.style.display = 'flex';

    try {
      if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        if (cameraSourceSelect) {
          cameraSourceSelect.innerHTML = '';
          videoDevices.forEach((dev, idx) => {
            const opt = document.createElement('option');
            opt.value = dev.deviceId;
            opt.textContent = dev.label || `Camera ${idx + 1}`;
            cameraSourceSelect.appendChild(opt);
          });
        }
      }
      startCameraStream(cameraSourceSelect ? cameraSourceSelect.value : null);
    } catch (err) {
      console.warn("Camera device query error:", err);
      startCameraStream();
    }
  }

  async function startCameraStream(deviceId) {
    if (activeMediaStream) {
      activeMediaStream.getTracks().forEach(t => t.stop());
    }

    const constraints = {
      video: deviceId
        ? { deviceId: { exact: deviceId } }
        : { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } },
      audio: false
    };

    try {
      activeMediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      if (cameraVideo) {
        cameraVideo.srcObject = activeMediaStream;
        await cameraVideo.play();
      }
    } catch (err) {
      alert("Unable to access camera: " + err.message + "\nPlease grant camera permissions or upload an image file.");
      closeCamera();
    }
  }

  function closeCamera() {
    if (activeMediaStream) {
      activeMediaStream.getTracks().forEach(t => t.stop());
      activeMediaStream = null;
    }
    if (cameraVideo) cameraVideo.srcObject = null;
    if (cameraModalOverlay) cameraModalOverlay.style.display = 'none';
  }

  if (openCameraSingleBtn) openCameraSingleBtn.addEventListener('click', () => openCamera('single'));
  if (openCameraFrontBtn) openCameraFrontBtn.addEventListener('click', () => openCamera('front'));
  if (openCameraBackBtn) openCameraBackBtn.addEventListener('click', () => openCamera('back'));

  if (cameraCancelBtn) cameraCancelBtn.addEventListener('click', closeCamera);
  if (cameraCloseXBtn) cameraCloseXBtn.addEventListener('click', closeCamera);
  if (cameraSourceSelect) {
    cameraSourceSelect.addEventListener('change', () => {
      startCameraStream(cameraSourceSelect.value);
    });
  }

  if (cameraSnapBtn) {
    cameraSnapBtn.addEventListener('click', () => {
      if (!cameraVideo || !activeMediaStream) return;
      const vw = cameraVideo.videoWidth || 1280;
      const vh = cameraVideo.videoHeight || 720;
      cameraCanvas.width = vw;
      cameraCanvas.height = vh;
      const ctx = cameraCanvas.getContext('2d');
      ctx.drawImage(cameraVideo, 0, 0, vw, vh);

      cameraCanvas.toBlob((blob) => {
        if (!blob) return;
        const file = new File([blob], `camera_scan_${Date.now()}.jpg`, { type: 'image/jpeg' });
        if (currentCameraTarget === 'front') {
          handleFrontSelection(file);
        } else if (currentCameraTarget === 'back') {
          handleBackSelection(file);
        } else {
          handleFileSelection(file);
        }
        closeCamera();
      }, 'image/jpeg', 0.95);
    });
  }

  // =========================================================================
  // 2. STATUTORY LEGAL NOTICE & SEIZURE MEMO GENERATOR
  // =========================================================================
  const generateNoticeBtn = document.getElementById('generateNoticeBtn');
  const noticeModalOverlay = document.getElementById('noticeModalOverlay');
  const noticeCloseBtn = document.getElementById('noticeCloseBtn');
  const noticeCopyBtn = document.getElementById('noticeCopyBtn');
  const noticePrintBtn = document.getElementById('noticePrintBtn');

  const noticeRefNo = document.getElementById('noticeRefNo');
  const noticeDate = document.getElementById('noticeDate');
  const noticeAddressee = document.getElementById('noticeAddressee');
  const noticeProductName = document.getElementById('noticeProductName');
  const noticeBrand = document.getElementById('noticeBrand');
  const noticeViolationsBody = document.getElementById('noticeViolationsBody');

  function openStatutoryNoticeModal() {
    if (!currentReportData) {
      alert("No inspection report available. Please scan a product first.");
      return;
    }

    const report = currentReportData;
    const extracted = report.extracted_data || {};
    if (noticeRefNo) noticeRefNo.textContent = `LMD/SZ/${report.inspection_id || '2026'}/ENF`;
    if (noticeDate) noticeDate.textContent = report.timestamp || new Date().toLocaleString('en-IN');
    if (noticeAddressee) noticeAddressee.textContent = extracted.manufacturer || extracted.packer || extracted.importer || "To the Manufacturer / Packer / Importer of the pre-packaged commodity";
    if (noticeProductName) noticeProductName.textContent = extracted.product_name || "Packaged Commodity";
    if (noticeBrand) noticeBrand.textContent = extracted.brand || "Unspecified Brand";

    // Violations list
    if (noticeViolationsBody) {
      noticeViolationsBody.innerHTML = '';
      const checks = report.compliance_checks || [];
      const nonCompliant = checks.filter(c => c.status === 'fail' || c.status === 'review');

      if (nonCompliant.length > 0) {
        nonCompliant.forEach((chk, idx) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>${idx + 1}</strong></td>
            <td><strong style="color:#60a5fa;">${escapeHtml(chk.rule_reference)}</strong></td>
            <td>${escapeHtml(chk.field_name)}<div style="font-size:0.74rem; color:#94a3b8; margin-top:2px;">Expected: ${escapeHtml(chk.expected)}</div></td>
            <td style="color:${chk.status === 'fail' ? '#f87171' : '#fbbf24'}; font-weight:600;">
              ${escapeHtml(chk.reason)}
            </td>
          `;
          noticeViolationsBody.appendChild(tr);
        });
      } else {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td colspan="4" style="text-align:center; color:#34d399; padding:18px;">
            No statutory contraventions observed during this preliminary screening. Packaging declarations satisfy the Legal Metrology (Packaged Commodities) Rules, 2011.
          </td>
        `;
        noticeViolationsBody.appendChild(tr);
      }
    }

    if (noticeModalOverlay) noticeModalOverlay.style.display = 'flex';
  }

  if (generateNoticeBtn) generateNoticeBtn.addEventListener('click', openStatutoryNoticeModal);
  if (noticeCloseBtn) noticeCloseBtn.addEventListener('click', () => { if (noticeModalOverlay) noticeModalOverlay.style.display = 'none'; });
  if (noticePrintBtn) noticePrintBtn.addEventListener('click', () => { window.print(); });
  if (noticeCopyBtn) {
    noticeCopyBtn.addEventListener('click', () => {
      const area = document.getElementById('printableNoticeArea');
      if (area) {
        navigator.clipboard.writeText(area.innerText).then(() => {
          alert("Statutory Legal Notice text copied to clipboard!");
        });
      }
    });
  }

  // =========================================================================
  // 3. RULEBOOK NAVIGATOR MODAL LOGIC
  // =========================================================================
  const openRulebookBtn = document.getElementById('openRulebookBtn');
  const rulebookModalOverlay = document.getElementById('rulebookModalOverlay');
  const rulebookCloseBtn = document.getElementById('rulebookCloseBtn');
  const ruleSearchInput = document.getElementById('ruleSearchInput');
  const ruleCategoryChips = document.getElementById('ruleCategoryChips');
  const calcPackWeight = document.getElementById('calcPackWeight');
  const calcNormalVal = document.getElementById('calcNormalVal');
  const calcMouldedVal = document.getElementById('calcMouldedVal');
  const rulesListContainer = document.getElementById('rulesListContainer');

  let cachedRulesData = [];
  let selectedRuleCategory = 'all';

  // Table-I Calculator
  if (calcPackWeight) {
    calcPackWeight.addEventListener('change', () => {
      const val = parseInt(calcPackWeight.value, 10);
      if (val <= 50) {
        calcNormalVal.textContent = '1.0 mm minimum';
        calcMouldedVal.textContent = '2.0 mm minimum';
      } else if (val <= 200) {
        calcNormalVal.textContent = '2.0 mm minimum';
        calcMouldedVal.textContent = '4.0 mm minimum';
      } else if (val <= 1000) {
        calcNormalVal.textContent = '4.0 mm minimum';
        calcMouldedVal.textContent = '6.0 mm minimum';
      } else {
        calcNormalVal.textContent = '6.0 mm minimum';
        calcMouldedVal.textContent = '6.0 mm minimum';
      }
    });
  }

  async function loadRulebookData() {
    if (cachedRulesData.length === 0) {
      try {
        const res = await fetch('/api/rules');
        const data = await res.json();
        cachedRulesData = data.rules || [];
      } catch (e) {
        console.error("Failed to load rules:", e);
      }
    }
    renderRulebookCards();
  }

  function renderRulebookCards(query = '') {
    if (!rulesListContainer) return;
    rulesListContainer.innerHTML = '';
    const q = (query || '').toLowerCase().trim();

    const filtered = cachedRulesData.filter(r => {
      // Category filter
      if (selectedRuleCategory === 'mandatory' && !r.mandatory) return false;
      if (selectedRuleCategory === 'table1' && r.id !== 'LM_TABLE_I') return false;
      if (selectedRuleCategory === 'usp' && r.id !== 'LM_USP') return false;
      if (selectedRuleCategory === 'penalties' && r.id !== 'LM_PENALTY') return false;

      // Text search
      if (q) {
        const text = `${r.field} ${r.rule_reference} ${r.description} ${r.id}`.toLowerCase();
        return text.includes(q);
      }
      return true;
    });

    if (filtered.length === 0) {
      rulesListContainer.innerHTML = '<div style="color:#94a3b8; text-align:center; padding:24px;">No matching statutory clauses found.</div>';
      return;
    }

    filtered.forEach(r => {
      const card = document.createElement('div');
      card.className = 'rule-card-item';
      let pillClass = 'pill-info';
      if (r.severity === 'high' || r.severity === 'critical') pillClass = 'pill-high';
      else if (r.severity === 'medium') pillClass = 'pill-medium';

      card.innerHTML = `
        <div class="rule-card-header">
          <span class="rule-ref-tag">${escapeHtml(r.rule_reference)}</span>
          <span class="rule-severity-pill ${pillClass}">${escapeHtml((r.severity || 'rule').toUpperCase())}</span>
        </div>
        <div class="rule-card-title">${escapeHtml(r.field)}</div>
        <div class="rule-card-desc">${escapeHtml(r.description)}</div>
      `;
      rulesListContainer.appendChild(card);
    });
  }

  if (openRulebookBtn) {
    openRulebookBtn.addEventListener('click', () => {
      if (rulebookModalOverlay) rulebookModalOverlay.style.display = 'flex';
      loadRulebookData();
    });
  }

  if (rulebookCloseBtn) {
    rulebookCloseBtn.addEventListener('click', () => {
      if (rulebookModalOverlay) rulebookModalOverlay.style.display = 'none';
    });
  }

  if (ruleSearchInput) {
    ruleSearchInput.addEventListener('input', (e) => {
      renderRulebookCards(e.target.value);
    });
  }

  if (ruleCategoryChips) {
    ruleCategoryChips.querySelectorAll('.rule-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        ruleCategoryChips.querySelectorAll('.rule-chip').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedRuleCategory = btn.getAttribute('data-category');
        renderRulebookCards(ruleSearchInput ? ruleSearchInput.value : '');
      });
    });
  }

  // Preset Buttons Listener
  document.querySelectorAll('.preset-card').forEach(card => {
    card.addEventListener('click', () => {
      const presetId = card.getAttribute('data-preset');
      runDemoPreset(presetId);
    });
  });

  // Tab Switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Action: Scan Product Image (Single or Dual)
  scanBtn.addEventListener('click', () => {
    const formData = new FormData();

    if (currentScanMode === 'dual') {
      if (!selectedFileFront || !selectedFileBack) return;
      formData.append('scan_mode', 'dual');
      formData.append('image_front', selectedFileFront);
      formData.append('image_back', selectedFileBack);
    } else {
      if (!selectedFile) return;
      formData.append('scan_mode', 'single');
      formData.append('image', selectedFile);
    }

    const customKey = geminiKeyInput ? geminiKeyInput.value.trim() : '';
    if (customKey) {
      formData.append('gemini_key', customKey);
    }

    startProgressSimulation();

    fetch('/api/inspect', {
      method: 'POST',
      body: formData
    })
      .then(async (res) => {
        const data = await res.json();
        return { status: res.status, data };
      })
      .then(({ status, data }) => {
        finishProgress(() => {
          if (status === 422 || data.error_type === 'PANEL_MISMATCH') {
            showMismatchModal(data.coherence, data.message);
          } else if (data.success) {
            renderInspectionResults(data.report, data.image_url);
          } else {
            alert(`Inspection Error: ${data.error || data.message || 'Unknown error occurred'}`);
          }
        });
      })
      .catch(err => {
        finishProgress(() => {
          alert(`Network or Server Error: ${err.message}`);
        });
      });
  });

  // Action: Run Demo Preset
  function runDemoPreset(presetId) {
    startProgressSimulation();
    fetch(`/api/demo/${presetId}`, { method: 'POST' })
      .then(async (res) => {
        const data = await res.json();
        return { status: res.status, data };
      })
      .then(({ status, data }) => {
        finishProgress(() => {
          if (status === 422 || data.error_type === 'PANEL_MISMATCH') {
            showMismatchModal(data.coherence, data.message);
          } else if (data.success) {
            renderInspectionResults(data.report, data.image_url);
          } else {
            alert(`Demo Error: ${data.error || data.message}`);
          }
        });
      })
      .catch(err => {
        finishProgress(() => {
          alert(`Failed to load demo preset: ${err.message}`);
        });
      });
  }

  // Progress Animation
  let progressInterval = null;
  function startProgressSimulation() {
    loadingOverlay.style.display = 'flex';
    let currentStageIndex = 0;
    progressBarFill.style.width = '5%';

    const updateStage = () => {
      if (currentStageIndex < STAGES.length) {
        const stage = STAGES[currentStageIndex];
        loadingStageText.textContent = stage.text;
        progressBarFill.style.width = `${stage.pct}%`;
        loadingSubtext.textContent = stage.sub;
        currentStageIndex++;
      }
    };

    updateStage();
    progressInterval = setInterval(updateStage, 700);
  }

  function finishProgress(callback) {
    clearInterval(progressInterval);
    progressBarFill.style.width = '100%';
    setTimeout(() => {
      loadingOverlay.style.display = 'none';
      if (callback) callback();
    }, 400);
  }

  // Render Inspection Results
  function renderInspectionResults(report, imageUrl) {
    currentReportData = report;
    uploadSection.style.display = 'none';
    resultsContainer.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Legal Metrology Screening Card
    const reportScore = document.getElementById('reportScore');
    const reportStatus = document.getElementById('reportStatus');
    const scoreCircle = document.getElementById('scoreCircle');
    const passedCount = document.getElementById('passedCount');
    const reviewCount = document.getElementById('reviewCount');
    const failedCount = document.getElementById('failedCount');
    const inspTimestamp = document.getElementById('inspTimestamp');
    const inspId = document.getElementById('inspId');

    reportScore.textContent = `${report.automated_screening_score}%`;
    inspTimestamp.textContent = report.timestamp;
    inspId.textContent = report.inspection_id;

    passedCount.textContent = report.passed_checks;
    reviewCount.textContent = report.review_checks;
    failedCount.textContent = report.failed_checks;

    reportStatus.className = 'status-pill';
    if (report.overall_status.includes('PASS')) {
      reportStatus.classList.add('status-pass');
      reportStatus.textContent = 'PRELIMINARY PASS';
      scoreCircle.style.borderColor = '#10b981';
      scoreCircle.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.4)';
    } else if (report.overall_status.includes('FAIL')) {
      reportStatus.classList.add('status-fail');
      reportStatus.textContent = 'FAIL / DEFICIENCIES DETECTED';
      scoreCircle.style.borderColor = '#ef4444';
      scoreCircle.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.4)';
    } else {
      reportStatus.classList.add('status-review');
      reportStatus.textContent = 'REVIEW REQUIRED';
      scoreCircle.style.borderColor = '#f59e0b';
      scoreCircle.style.boxShadow = '0 0 20px rgba(245, 158, 11, 0.4)';
    }

    // Authenticity Risk Card
    const auth = report.authenticity || {};
    const riskScoreVal = document.getElementById('riskScoreVal');
    const riskStatusPill = document.getElementById('riskStatusPill');
    const riskScoreCircle = document.getElementById('riskScoreCircle');
    const riskSummaryText = document.getElementById('riskSummaryText');

    const riskScore = auth.risk_score !== undefined ? auth.risk_score : 50;
    riskScoreVal.textContent = riskScore.toString();
    riskSummaryText.textContent = auth.assessment_summary || 'Authenticity risk evaluation completed.';

    riskStatusPill.className = 'status-pill';
    if (auth.risk_level === 'LOW') {
      riskStatusPill.classList.add('status-low-risk');
      riskStatusPill.textContent = 'LOW RISK';
      riskScoreCircle.style.borderColor = '#34d399';
      riskScoreCircle.style.boxShadow = '0 0 20px rgba(52, 211, 153, 0.4)';
    } else if (auth.risk_level === 'HIGH') {
      riskStatusPill.classList.add('status-high-risk');
      riskStatusPill.textContent = 'HIGH RISK';
      riskScoreCircle.style.borderColor = '#f87171';
      riskScoreCircle.style.boxShadow = '0 0 20px rgba(248, 113, 113, 0.4)';
    } else {
      riskStatusPill.classList.add('status-med-risk');
      riskStatusPill.textContent = auth.risk_level || 'REVIEW REQUIRED';
      riskScoreCircle.style.borderColor = '#fbbf24';
      riskScoreCircle.style.boxShadow = '0 0 20px rgba(251, 191, 36, 0.4)';
    }

    // Render Authenticity Signals Checklist in Header
    const authSignalsListHeader = document.getElementById('authSignalsListHeader');
    authSignalsListHeader.innerHTML = '';
    (auth.signals || []).slice(0, 4).forEach(sig => {
      const sigItem = document.createElement('div');
      sigItem.style.fontSize = '0.78rem';
      sigItem.style.display = 'flex';
      sigItem.style.justifyContent = 'space-between';
      sigItem.style.alignItems = 'center';

      let color = sig.status === 'pass' ? '#34d399' : (sig.status === 'fail' ? '#f87171' : '#fbbf24');

      sigItem.innerHTML = `
        <span style="color: #cbd5e1;">${escapeHtml(sig.label)}</span>
        <span style="color: ${color}; font-weight:700; font-size:0.75rem; letter-spacing:0.04em;">${escapeHtml(sig.status.toUpperCase())}</span>
      `;
      authSignalsListHeader.appendChild(sigItem);
    });

    // Tab 1: Compliance Table
    const tableBody = document.getElementById('complianceTableBody');
    tableBody.innerHTML = '';
    report.compliance_checks.forEach(check => {
      const tr = document.createElement('tr');
      let badgeClass = 'status-review';
      let badgeText = 'REVIEW';
      const st = (check.status || '').toLowerCase();
      if (st === 'pass') {
        badgeClass = 'status-pass';
        badgeText = 'PASS';
      } else if (st === 'fail') {
        badgeClass = 'status-fail';
        badgeText = 'FAIL';
      } else if (st === 'missing') {
        badgeClass = 'status-fail';
        badgeText = 'MISSING';
      } else if (st === 'non_standard' || st === 'non-standard') {
        badgeClass = 'status-review';
        badgeText = 'NON-STANDARD';
      } else if (st === 'potentially_misleading') {
        badgeClass = 'status-review';
        badgeText = 'MISLEADING';
      }

      tr.innerHTML = `
        <td>
          <span class="field-title">${escapeHtml(check.field_name)}</span>
          <span class="rule-ref">${escapeHtml(check.rule_reference)}</span>
        </td>
        <td>
          <span class="table-badge ${badgeClass}">${badgeText}</span>
        </td>
        <td>
          <div class="${check.detected_value ? 'val-detected' : 'val-missing'}">
            ${escapeHtml(check.detected_value || 'Not detected')}
          </div>
          ${check.evidence ? `<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;"><strong>Evidence:</strong> ${escapeHtml(check.evidence)}</div>` : ''}
        </td>
        <td>
          <div style="font-size: 0.85rem; color: #cbd5e1;">${escapeHtml(check.reason)}</div>
          <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">Expected: ${escapeHtml(check.expected)}</div>
        </td>
      `;
      tableBody.appendChild(tr);
    });

    // Tab 2: Authenticity Grid & Web Evidence
    const authSignalsGrid = document.getElementById('authSignalsGrid');
    authSignalsGrid.innerHTML = '';
    (auth.signals || []).forEach(sig => {
      const card = document.createElement('div');
      card.className = 'info-card';
      let badgeClass = sig.status === 'pass' ? 'status-pass' : (sig.status === 'fail' ? 'status-fail' : 'status-review');
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <div class="info-label" style="margin:0;">${escapeHtml(sig.label)}</div>
          <span class="table-badge ${badgeClass}">${escapeHtml(sig.status.toUpperCase())}</span>
        </div>
        <div class="info-value" style="font-size:0.85rem; color:#cbd5e1;">${escapeHtml(sig.reason)}</div>
      `;
      authSignalsGrid.appendChild(card);
    });

    const authReasonsList = document.getElementById('authReasonsList');
    authReasonsList.innerHTML = '';
    (auth.reasons || []).forEach(r => {
      const li = document.createElement('li');
      li.style.marginBottom = '6px';
      li.style.color = '#e2e8f0';
      li.style.fontSize = '0.88rem';
      li.textContent = r;
      authReasonsList.appendChild(li);
    });

    const webSourcesContainer = document.getElementById('webSourcesContainer');
    webSourcesContainer.innerHTML = '';
    const sources = auth.sources || [];
    if (sources.length > 0) {
      sources.forEach(src => {
        const item = document.createElement('div');
        item.className = 'source-item';
        let badgeClass = 'source-badge-web';
        let badgeLabel = 'Web Result';
        if (src.source_type === 'official') {
          badgeClass = 'source-badge-official';
          badgeLabel = 'Official Brand Site';
        } else if (src.source_type === 'retailer') {
          badgeClass = 'source-badge-retailer';
          badgeLabel = 'Major Retailer';
        }

        const tags = (src.matched_attributes || []).map(t => `<span class="chip" style="font-size:0.7rem; padding:2px 8px;">${escapeHtml(t)}</span>`).join(' ');

        item.innerHTML = `
          <div class="source-header">
            <span class="source-title">${escapeHtml(src.title)}</span>
            <span class="source-badge ${badgeClass}">${badgeLabel}</span>
          </div>
          <div class="source-snippet">${escapeHtml(src.snippet)}</div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
            <div>${tags}</div>
            ${src.url ? `<a href="${escapeHtml(src.url)}" target="_blank" class="source-link">View Reference Source &rarr;</a>` : ''}
          </div>
        `;
        webSourcesContainer.appendChild(item);
      });
    } else {
      webSourcesContainer.innerHTML = `
        <div class="disclaimer-card" style="margin-top:0;">
          No matching web reference sources corroborated. Unverified brand or product line.
        </div>
      `;
    }

    // Tab: Dual-Panel Coherence Verification
    const tabBtnCoherence = document.getElementById('tabBtnCoherence');
    const coherenceContainer = document.getElementById('coherenceContainer');
    const coherence = report.coherence;

    if (coherence && coherence.is_dual_panel) {
      if (tabBtnCoherence) tabBtnCoherence.style.display = 'inline-block';
      if (coherenceContainer) {
        let statusClass = 'coherence-score-pass';
        if (coherence.status === 'WARNING') {
          statusClass = 'coherence-score-warning';
        }

        coherenceContainer.innerHTML = `
          <div class="coherence-overview-card">
            <div class="coherence-header-split">
              <div>
                <span class="slot-badge slot-badge-front" style="margin-bottom:6px;">Cross-Panel Gatekeeper Passed</span>
                <h3 style="margin:4px 0 6px 0; font-size:1.25rem; color:#f8fafc;">${escapeHtml(coherence.verdict_title)}</h3>
                <p style="margin:0; font-size:0.88rem; color:#94a3b8; max-width:700px; line-height:1.5;">${escapeHtml(coherence.verdict_summary)}</p>
              </div>
              <div class="coherence-score-tag ${statusClass}">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>${coherence.coherence_score}% Coherence</span>
              </div>
            </div>

            <!-- 4-Attribute Corroboration Matrix -->
            <div class="coherence-matrix-grid">
              <div class="coherence-item-card">
                <span class="coherence-item-title">Brand Identity Continuity</span>
                <div class="coherence-item-status" style="color: ${coherence.brand_match ? '#34d399' : '#f87171'};">
                  ${coherence.brand_match ? 'Corroborated' : 'Discrepancy'}
                </div>
                <div class="coherence-item-detail">Front PDP and Back Info panel share identical brand authority (${escapeHtml(report.extracted_data.brand || 'Detected')}).</div>
              </div>

              <div class="coherence-item-card">
                <span class="coherence-item-title">Commodity Category Match</span>
                <div class="coherence-item-status" style="color: ${coherence.category_match ? '#34d399' : '#f87171'};">
                  ${coherence.category_match ? 'Aligned' : 'Incompatible'}
                </div>
                <div class="coherence-item-detail">Both panels verified in identical regulatory classification (${escapeHtml(report.extracted_data.generic_name || 'Food / Packaged Commodity')}).</div>
              </div>

              <div class="coherence-item-card">
                <span class="coherence-item-title">Pack Size & Net Quantity</span>
                <div class="coherence-item-status" style="color: #34d399;">
                  Harmonized (${escapeHtml(report.extracted_data.net_quantity || 'Verified')})
                </div>
                <div class="coherence-item-detail">Net quantity declarations cross-checked without volumetric conflict.</div>
              </div>

              <div class="coherence-item-card">
                <span class="coherence-item-title">Cross-Panel Merging</span>
                <div class="coherence-item-status" style="color: #38bdf8;">
                  Complete Consolidation
                </div>
                <div class="coherence-item-detail">Front PDP (Brand, Title, Net Qty) unified with Back Info (MRP, Dates, Ingredients, FSSAI).</div>
              </div>
            </div>
          </div>

          <!-- Dual Panel Discrepancies / Verification Notes -->
          <div class="info-card">
            <div class="info-label" style="color:#38bdf8;">Gatekeeper Verification Log</div>
            <div class="info-value" style="font-size:0.86rem; color:#cbd5e1; line-height:1.6;">
              ${(coherence.discrepancies && coherence.discrepancies.length > 0)
                ? `<ul style="margin:6px 0 0 18px; padding:0;">${coherence.discrepancies.map(d => `<li>${escapeHtml(d)}</li>`).join('')}</ul>`
                : 'Zero cross-panel conflicts detected. Automated Mismatch Prevention Gatekeeper confirms both photographs originate from the same physical packaged commodity.'}
            </div>
          </div>
        `;
      }
    } else {
      if (tabBtnCoherence) tabBtnCoherence.style.display = 'none';
    }

    // Tab: Alternate Products
    const alternatesGrid = document.getElementById('alternatesGrid');
    const alternatesCountBadge = document.getElementById('alternatesCountBadge');
    const alternates = report.alternate_products || [];

    if (alternatesCountBadge) {
      alternatesCountBadge.textContent = `${alternates.length} Alternative${alternates.length === 1 ? '' : 's'} Available`;
    }

    if (alternatesGrid) {
      if (alternates.length > 0) {
        alternatesGrid.innerHTML = '';
        alternates.forEach(alt => {
          const card = document.createElement('div');
          card.className = 'alt-card';

          let typeClass = 'alt-type-competitor';
          const stype = (alt.similarity_type || '').toLowerCase();
          if (stype.includes('health')) typeClass = 'alt-type-healthier';
          else if (stype.includes('economy') || stype.includes('value')) typeClass = 'alt-type-economy';
          else if (stype.includes('variant') || stype.includes('line')) typeClass = 'alt-type-variant';

          const highlightsHtml = (alt.highlights || []).map(h => `<span class="alt-chip">${escapeHtml(h)}</span>`).join('');

          card.innerHTML = `
            <div>
              <div class="alt-card-header">
                <span class="alt-brand-badge">${escapeHtml(alt.brand || 'Brand')}</span>
                <span class="alt-type-pill ${typeClass}">${escapeHtml(alt.similarity_type || 'Market Alternative')}</span>
              </div>
              <div class="alt-title">${escapeHtml(alt.name)}</div>
              <div class="alt-category">${escapeHtml(alt.category || 'Consumer Commodity')} • Pack: <strong>${escapeHtml(alt.net_quantity || 'Standard')}</strong></div>

              <div class="alt-price-box">
                <div>
                  <span style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; display:block;">Reference Price</span>
                  <span class="alt-price-val">${escapeHtml(alt.estimated_mrp || 'Standard MRP')}</span>
                </div>
                ${alt.unit_price ? `
                  <div style="text-align:right;">
                    <span style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; display:block;">Unit Rate</span>
                    <span class="alt-unit-price">${escapeHtml(alt.unit_price)}</span>
                  </div>
                ` : ''}
              </div>

              <div class="alt-highlights-list">
                ${highlightsHtml}
              </div>
            </div>

            <div class="alt-footer-row">
              <div class="alt-retailer-tag">
                ${escapeHtml(alt.source_retailer || 'Blinkit / Zepto / BigBasket')}
              </div>
              <a href="${escapeHtml(alt.source_url || `https://www.google.com/search?q=${encodeURIComponent((alt.brand||'') + ' ' + alt.name)}`)}" target="_blank" class="alt-link-btn">
                View Product &rarr;
              </a>
            </div>
          `;
          alternatesGrid.appendChild(card);
        });
      } else {
        alternatesGrid.innerHTML = `
          <div class="disclaimer-card" style="grid-column: 1 / -1; margin-top:0;">
            No alternative products identified for this specialized commodity.
          </div>
        `;
      }
    }

    // Tab: Nutritional Details
    const nutritionContainer = document.getElementById('nutritionContainer');
    const nut = report.nutrition || {};

    if (nutritionContainer) {
      if (!nut || nut.is_food_product === false) {
        nutritionContainer.innerHTML = `
          <div class="non-food-card">
            <div class="non-food-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 12h6M12 9v6"/></svg>
            </div>
            <div class="non-food-title">Non-Food Consumer Commodity</div>
            <div class="non-food-text">
              ${escapeHtml(nut.summary_verdict || 'This product is classified under non-food personal care / cosmetic / household commodities. Under FSSAI and Legal Metrology regulations, food nutritional tables are exempt.')}
            </div>
            <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:18px;">
              ${(nut.highlights || ['Exempt from FSSAI Nutritional Table', 'Subject to Legal Metrology Rule 6 Declarations', 'Mandatory Net Content & Batch Details Apply']).map(h => `<span class="chip" style="background:rgba(255,255,255,0.08);">${escapeHtml(h)}</span>`).join('')}
            </div>
            <div style="font-size:0.75rem; color:#64748b; font-style:italic;">
              Note: Cosmetic and chemical safety guidelines apply. Refer to the 'Safety & Disclaimers' tab for extracted allergen and caution stamps.
            </div>
          </div>
        `;
      } else {
        // Find top macros for traffic light cards: Sugars, Sat Fat, Sodium, Energy / Trans Fat
        const items = nut.items || [];
        const sugarItem = items.find(i => i.name.toLowerCase().includes('sugar')) || { name: 'Total Sugars', value: 'N/A', indicator_level: 'NORMAL', per_unit: 'per 100g' };
        const satFatItem = items.find(i => i.name.toLowerCase().includes('sat') && i.name.toLowerCase().includes('fat')) || { name: 'Saturated Fat', value: 'N/A', indicator_level: 'NORMAL', per_unit: 'per 100g' };
        const sodiumItem = items.find(i => i.name.toLowerCase().includes('sodium') || i.name.toLowerCase().includes('salt')) || { name: 'Sodium', value: 'N/A', indicator_level: 'NORMAL', per_unit: 'per 100g' };
        const energyItem = items.find(i => i.name.toLowerCase().includes('energy') || i.name.toLowerCase().includes('calorie')) || { name: 'Energy', value: 'N/A', indicator_level: 'NORMAL', per_unit: 'per 100g' };

        const keyNutrients = [energyItem, sugarItem, satFatItem, sodiumItem];

        const trafficCardsHtml = keyNutrients.map(k => {
          const level = (k.indicator_level || 'NORMAL').toUpperCase();
          let cardClass = 'traffic-normal';
          let badgeClass = 'badge-normal';
          if (level === 'HIGH') {
            cardClass = 'traffic-high';
            badgeClass = 'badge-high';
          } else if (level === 'MODERATE') {
            cardClass = 'traffic-moderate';
            badgeClass = 'badge-moderate';
          } else if (level === 'LOW') {
            cardClass = 'traffic-low';
            badgeClass = 'badge-low';
          }

          return `
            <div class="traffic-card ${cardClass}">
              <div class="traffic-top-row">
                <span class="traffic-nutrient-name">${escapeHtml(k.name)}</span>
                <span class="traffic-badge ${badgeClass}">${escapeHtml(level)}</span>
              </div>
              <div class="traffic-val">${escapeHtml(k.value)}</div>
              <div class="traffic-per-unit">${escapeHtml(k.per_unit || 'per 100g')} ${k.daily_value_percent ? `• ${escapeHtml(k.daily_value_percent)} RDA` : ''}</div>
            </div>
          `;
        }).join('');

        const tableRowsHtml = items.map(it => {
          const level = (it.indicator_level || 'NORMAL').toUpperCase();
          let badgeClass = 'badge-normal';
          if (level === 'HIGH') badgeClass = 'badge-high';
          else if (level === 'MODERATE') badgeClass = 'badge-moderate';
          else if (level === 'LOW') badgeClass = 'badge-low';

          return `
            <tr>
              <td style="font-weight:600; color:#e2e8f0;">${escapeHtml(it.name)}</td>
              <td style="font-family:monospace; font-weight:700; color:#38bdf8;">${escapeHtml(it.value)}</td>
              <td style="color:#94a3b8; font-size:0.78rem;">${escapeHtml(it.per_unit || 'per 100g')}</td>
              <td>${it.daily_value_percent ? `<span class="chip" style="font-size:0.72rem; padding:2px 8px;">${escapeHtml(it.daily_value_percent)}</span>` : '<span style="color:#64748b;">-</span>'}</td>
              <td><span class="traffic-badge ${badgeClass}">${escapeHtml(level)}</span></td>
            </tr>
          `;
        }).join('');

        const highlightsChips = (nut.highlights || []).map(h => `<span class="chip" style="background:rgba(56,189,248,0.1); border-color:rgba(56,189,248,0.3); color:#bae6fd;">${escapeHtml(h)}</span>`).join(' ');

        nutritionContainer.innerHTML = `
          <div class="nut-hero-banner">
            <div>
              <div class="nut-hero-title">${escapeHtml(nut.summary_verdict || 'Nutritional Declarations Matrix')}</div>
              <div class="nut-hero-desc">Front-of-pack statutory nutrient analysis evaluated according to FSSAI guidelines.</div>
              ${highlightsChips ? `<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">${highlightsChips}</div>` : ''}
            </div>
            <div class="nut-serving-badge">
              <div class="nut-serving-label">Serving Reference</div>
              <div class="nut-serving-val">${escapeHtml(nut.serving_size || '100 g')}</div>
              ${nut.servings_per_container ? `<div style="font-size:0.72rem; color:#94a3b8;">${escapeHtml(nut.servings_per_container)}</div>` : ''}
            </div>
          </div>

          <div>
            <h4 style="font-size:0.95rem; color:#94a3b8; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
              FSSAI Front-of-Pack Nutritional Evaluation
            </h4>
            <div class="traffic-cards-grid">
              ${trafficCardsHtml}
            </div>
          </div>

          <div class="nut-table-card">
            <div style="padding:14px 18px; border-bottom:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
              <strong style="color:#f8fafc; font-size:0.92rem;">Detailed Nutritional Information (Declared per 100g / Serving)</strong>
              <span style="font-size:0.72rem; color:#94a3b8;">Source: Scanned Package Panel</span>
            </div>
            <div style="overflow-x:auto;">
              <table class="nut-table">
                <thead>
                  <tr>
                    <th style="width:30%;">Nutrient Component</th>
                    <th style="width:20%;">Declared Amount</th>
                    <th style="width:18%;">Basis</th>
                    <th style="width:16%;">% Daily Value (RDA)</th>
                    <th style="width:16%;">FSSAI Indicator</th>
                  </tr>
                </thead>
                <tbody>
                  ${tableRowsHtml || '<tr><td colspan="5" style="text-align:center; color:#94a3b8;">No detailed nutritional table isolated.</td></tr>'}
                </tbody>
              </table>
            </div>
          </div>

          <div class="disclaimer-card" style="margin-top:0;">
            ${escapeHtml(nut.disclaimer || 'Nutritional values extracted from label declarations. Actual nutritional laboratory assays may vary within standard statutory tolerances (+/- 10%).')}
          </div>
        `;
      }
    }

    // Tab 3: Extracted Info Grid
    const info = report.extracted_data;
    const infoGrid = document.getElementById('infoGrid');
    infoGrid.innerHTML = `
      <div class="info-card">
        <div class="info-label">Product Name / Commodity</div>
        <div class="info-value">${escapeHtml(info.product_name || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Brand Name</div>
        <div class="info-value">${escapeHtml(info.brand || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Manufacturer / Packer Details</div>
        <div class="info-value">${escapeHtml(info.manufacturer || info.packer || info.importer || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Net Quantity</div>
        <div class="info-value">${escapeHtml(info.net_quantity || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Maximum Retail Price (MRP)</div>
        <div class="info-value">${escapeHtml(info.mrp || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Manufacturing / Packing Date</div>
        <div class="info-value">${escapeHtml(info.manufacturing_date || info.packing_date || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Consumer Care Information</div>
        <div class="info-value">${escapeHtml(info.consumer_care || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Country of Origin</div>
        <div class="info-value">${escapeHtml(info.country_of_origin || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Unit Sale Price (USP)</div>
        <div class="info-value">${escapeHtml(info.unit_sale_price || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Batch / Lot Number</div>
        <div class="info-value">${escapeHtml(info.batch_number || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Barcode (EAN / UPC)</div>
        <div class="info-value">${escapeHtml(info.barcode || 'Not detected')}</div>
      </div>
      <div class="info-card">
        <div class="info-label">Certification Marks (FSSAI/ISI)</div>
        <div class="info-chips-wrapper">
          ${(info.certification_marks && info.certification_marks.length > 0)
            ? info.certification_marks.map(c => `<span class="chip">${escapeHtml(c)}</span>`).join('')
            : '<span style="color:#64748b; font-size:0.85rem;">None isolated</span>'}
        </div>
      </div>
      <div class="info-card" style="grid-column: 1 / -1;">
        <div class="info-label">Ingredients & Safety Warnings</div>
        <div class="info-value" style="font-size:0.85rem; margin-bottom: 8px;">
          <strong>Ingredients:</strong> ${escapeHtml(info.ingredients || 'Not detected on visible side')}
        </div>
        <div class="info-chips-wrapper">
          ${(info.warnings && info.warnings.length > 0)
            ? info.warnings.map(w => `<span class="chip" style="border-color: rgba(239, 68, 68, 0.4); color: #fca5a5;">${escapeHtml(w)}</span>`).join('')
            : '<span style="color:#64748b; font-size:0.85rem;">No allergen / caution warnings detected</span>'}
        </div>
      </div>
    `;

    // Tab 4: Readability Grid
    const readGrid = document.getElementById('readabilityGrid');
    const read = report.readability;
    const regionHeights = read.region_text_heights || {};
    let regionRowsHtml = Object.entries(regionHeights).map(([k, v]) => `
      <div style="display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:4px; font-family:monospace; padding:3px 6px; background:rgba(0,0,0,0.25); border-radius:4px;">
        <span style="color:#94a3b8;">${escapeHtml(k)}</span>
        <span style="color:#60a5fa; font-weight:600;">${escapeHtml(v)}</span>
      </div>
    `).join('');

    readGrid.innerHTML = `
      <div class="metric-card">
        <div class="metric-title">Visual Readability Status</div>
        <div class="metric-val" style="color: ${read.status === 'pass' ? '#34d399' : '#fbbf24'}; text-transform: uppercase;">
          ${escapeHtml(read.status)}
        </div>
        <div class="metric-desc">${escapeHtml(read.summary)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Physical Font Size Scale</div>
        <div class="metric-val" style="color: #fbbf24;">NOT CALIBRATED</div>
        <div class="metric-desc">Visual scale uncalibrated without physical ruler reference</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Image Quality & Sharpness</div>
        <div class="metric-val">${escapeHtml(read.sharpness_score.toString())}</div>
        <div class="metric-desc">${read.sharpness_score > 40 ? 'GOOD (High Edge Clarity)' : 'MODERATE / REVIEW'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Declaration Text Region Heights</div>
        <div style="margin-top:6px;">
          ${regionRowsHtml || `<div class="metric-val">~${escapeHtml((read.estimated_text_height_px || 32).toString())} px</div>`}
        </div>
      </div>
    `;
    document.getElementById('fontDisclaimer').textContent = read.physical_font_size_note;

    // Tab 5: Visual Evidence
    const evidenceImg = document.getElementById('evidenceProductImg');
    evidenceImg.src = imageUrl;
    renderEvidenceTab(info.regions || []);
  }

  // Debug mode state and resize handler
  let activeRegionsList = [];
  let isDebugCoordsEnabled = false;

  const debugCoordsToggle = document.getElementById('debugCoordsToggle');
  if (debugCoordsToggle) {
    debugCoordsToggle.addEventListener('change', (e) => {
      isDebugCoordsEnabled = e.target.checked;
      renderEvidenceTab(activeRegionsList);
    });
  }

  window.addEventListener('resize', () => {
    if (activeRegionsList && activeRegionsList.length > 0) {
      renderBoundingOverlays(activeRegionsList);
    }
  });

  function renderEvidenceTab(regions) {
    activeRegionsList = regions || [];
    const evidenceImg = document.getElementById('evidenceProductImg');
    const evidenceList = document.getElementById('evidenceList');
    evidenceList.innerHTML = '';

    if (!regions || regions.length === 0) {
      evidenceList.innerHTML = `
        <div class="evidence-item">
          <div style="font-size:0.85rem; color:#94a3b8;">
            Declaration text extracted from whole-label scan.
          </div>
        </div>
      `;
      renderBoundingOverlays([]);
      return;
    }

    regions.forEach((r, idx) => {
      const regionId = `region_${idx + 1}`;
      const hasCoords = r.x !== null && r.y !== null && r.width !== null && r.height !== null && r.x !== undefined;
      
      const card = document.createElement('div');
      card.className = 'evidence-item';
      card.setAttribute('data-region-id', regionId);

      let debugHtml = '';
      if (isDebugCoordsEnabled) {
        let nw = evidenceImg.naturalWidth || 800;
        let nh = evidenceImg.naturalHeight || 600;
        let x_norm = hasCoords ? (r.x > 1.0 ? (r.x <= 100.0 ? r.x / 100.0 : r.x / nw) : r.x) : 'N/A';
        let y_norm = hasCoords ? (r.y > 1.0 ? (r.y <= 100.0 ? r.y / 100.0 : r.y / nh) : r.y) : 'N/A';
        let w_norm = hasCoords ? (r.width > 1.0 ? (r.width <= 100.0 ? r.width / 100.0 : r.width / nw) : r.width) : 'N/A';
        let h_norm = hasCoords ? (r.height > 1.0 ? (r.height <= 100.0 ? r.height / 100.0 : r.height / nh) : r.height) : 'N/A';

        let cw = evidenceImg.clientWidth || 0;
        let ch = evidenceImg.clientHeight || 0;
        let dispX = (typeof x_norm === 'number' && cw) ? Math.round(x_norm * cw) : 'N/A';
        let dispY = (typeof y_norm === 'number' && ch) ? Math.round(y_norm * ch) : 'N/A';
        let dispW = (typeof w_norm === 'number' && cw) ? Math.round(w_norm * cw) : 'N/A';
        let dispH = (typeof h_norm === 'number' && ch) ? Math.round(h_norm * ch) : 'N/A';

        debugHtml = `
          <div style="margin-top:8px; padding-top:6px; border-top:1px dashed var(--border-color); font-family:monospace; font-size:0.72rem; color:#94a3b8; line-height:1.4;">
            <div><strong>Debug Info (${regionId}):</strong></div>
            <div>Original Coords: x=${r.x}, y=${r.y}, w=${r.width}, h=${r.height}</div>
            <div>Normalized (0-1): x=${typeof x_norm==='number'?x_norm.toFixed(3):x_norm}, y=${typeof y_norm==='number'?y_norm.toFixed(3):y_norm}, w=${typeof w_norm==='number'?w_norm.toFixed(3):w_norm}, h=${typeof h_norm==='number'?h_norm.toFixed(3):h_norm}</div>
            <div>Displayed (px): x=${dispX}px, y=${dispY}px, w=${dispW}px, h=${dispH}px</div>
            <div>Image Natural Dim: ${nw} x ${nh} px | Displayed: ${cw} x ${ch} px</div>
          </div>
        `;
      }

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <strong style="color:#60a5fa; font-size:0.85rem;">${escapeHtml(r.label)}</strong>
          <span style="font-size:0.7rem; color:${hasCoords ? '#34d399' : '#fbbf24'}; font-weight:600;">
            ${hasCoords ? `Region #${idx + 1}` : 'Annotation: Not available'}
          </span>
        </div>
        <div style="font-size:0.85rem; color:#e2e8f0; font-family:monospace; background:rgba(0,0,0,0.3); padding:4px 8px; border-radius:4px;">
          ${escapeHtml(r.text)}
        </div>
        ${debugHtml}
      `;

      // Two-way hover highlight
      card.addEventListener('mouseenter', () => {
        card.classList.add('active-highlight');
        const targetBox = document.querySelector(`.bbox-overlay[data-region-id="${regionId}"]`);
        if (targetBox) targetBox.classList.add('active-highlight');
      });
      card.addEventListener('mouseleave', () => {
        card.classList.remove('active-highlight');
        const targetBox = document.querySelector(`.bbox-overlay[data-region-id="${regionId}"]`);
        if (targetBox) targetBox.classList.remove('active-highlight');
      });

      evidenceList.appendChild(card);
    });

    renderBoundingOverlays(regions);
  }

  function renderBoundingOverlays(regions) {
    const img = document.getElementById('evidenceProductImg');
    const overlayContainer = document.getElementById('boundingOverlayContainer');
    if (!img || !overlayContainer) return;

    overlayContainer.innerHTML = '';
    if (!img.complete || !img.naturalWidth || !img.naturalHeight) {
      img.onload = () => renderBoundingOverlays(regions);
      return;
    }

    const nw = img.naturalWidth;
    const nh = img.naturalHeight;
    const cw = img.clientWidth;
    const ch = img.clientHeight;

    if (!cw || !ch) return;

    const placedLabels = [];

    regions.forEach((r, idx) => {
      const regionId = `region_${idx + 1}`;
      if (r.x === null || r.y === null || r.width === null || r.height === null || r.x === undefined) {
        return; // Do NOT fabricate fake coordinates if unavailable!
      }

      let x_norm, y_norm, w_norm, h_norm;

      if (r.x > 1.0) {
        if (r.x <= 100.0) {
          x_norm = r.x / 100.0;
          y_norm = r.y / 100.0;
          w_norm = r.width / 100.0;
          h_norm = r.height / 100.0;
        } else {
          x_norm = r.x / nw;
          y_norm = r.y / nh;
          w_norm = r.width / nw;
          h_norm = r.height / nh;
        }
      } else {
        x_norm = r.x;
        y_norm = r.y;
        w_norm = r.width;
        h_norm = r.height;
      }

      // Clamp coordinates within 0 to 1
      x_norm = Math.max(0, Math.min(1, x_norm));
      y_norm = Math.max(0, Math.min(1, y_norm));
      w_norm = Math.max(0.01, Math.min(1 - x_norm, w_norm));
      h_norm = Math.max(0.01, Math.min(1 - y_norm, h_norm));

      const displayX = x_norm * cw;
      const displayY = y_norm * ch;
      const displayW = w_norm * cw;
      const displayH = h_norm * ch;

      const box = document.createElement('div');
      box.className = 'bbox-overlay';
      box.setAttribute('data-region-id', regionId);
      box.style.left = `${displayX}px`;
      box.style.top = `${displayY}px`;
      box.style.width = `${displayW}px`;
      box.style.height = `${displayH}px`;

      const lbl = document.createElement('div');
      lbl.className = 'bbox-label';
      lbl.textContent = r.label;

      let labelTop = -22;
      placedLabels.forEach(prev => {
        if (Math.abs(prev.x - displayX) < 75 && Math.abs(prev.y - displayY) < 22) {
          labelTop = -38;
        }
      });
      placedLabels.push({ x: displayX, y: displayY });
      lbl.style.top = `${labelTop}px`;

      box.appendChild(lbl);

      // Two-way hover highlight
      box.addEventListener('mouseenter', () => {
        box.classList.add('active-highlight');
        const targetCard = document.querySelector(`.evidence-item[data-region-id="${regionId}"]`);
        if (targetCard) {
          targetCard.classList.add('active-highlight');
          targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });
      box.addEventListener('mouseleave', () => {
        box.classList.remove('active-highlight');
        const targetCard = document.querySelector(`.evidence-item[data-region-id="${regionId}"]`);
        if (targetCard) targetCard.classList.remove('active-highlight');
      });

      overlayContainer.appendChild(box);
    });
  }

  // Download PDF Report Action

  downloadPdfBtn.addEventListener('click', () => {
    if (!currentReportData || !currentReportData.inspection_id) {
      alert("No inspection report available to download.");
      return;
    }
    const pdfUrl = `/api/report/pdf/${currentReportData.inspection_id}`;
    window.open(pdfUrl, '_blank');
  });

  // Scan Another Product Reset
  newScanBtn.addEventListener('click', () => {
    resultsContainer.style.display = 'none';
    uploadSection.style.display = 'block';
    resetUploadState();
    // Reset active tab to compliance table
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    const firstTabBtn = document.querySelector('.tab-btn[data-tab="tabCompliance"]');
    const firstTabPane = document.getElementById('tabCompliance');
    if (firstTabBtn) firstTabBtn.classList.add('active');
    if (firstTabPane) firstTabPane.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // Print Web Summary
  printBtn.addEventListener('click', () => {
    window.print();
  });

  function escapeHtml(str) {
    if (!str) return '';
    return str.toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
