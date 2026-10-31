<template>
  <div class="main-view-wrapper h-full overflow-y-auto overflow-x-hidden" :class="attrs.class">
    
    <div v-if="!isEditing && !isCompressed && !umapActive && !showFinalView" class="overview-container" :class="{ 'compressing': isCompressing }">
      
      <div class="overview-header">
        
        <button @click="hidepocket" class="compress-button" title="Hide">
  <svg class="w-5 h-5" 
       fill="none" 
       stroke="currentColor" 
       viewBox="0 0 24 24"
       :class="{ 'rotate-180': !arePocketsVisible }">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
          d="M19 9l-7 7-7-7M5 5h14M5 19h14" />
  </svg>
</button>
     -->

        <div class="header-title font-semibold text-[#407434]">
          Hierarchy View
        </div>
        <div class="button-group">
  
   
  <button 
    class="btn btn-icon-text"
    @click="uploadCsv"
    v-b-tooltip.hover 
    title="Upload a CSV file to load data"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm-2 14v-4h-2l3-3 3 3h-2v4zm2-12l4 4h-4V4z"/>
    </svg>
    <span class="btn-label">Upload</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="toggleStageModal"
    v-b-tooltip.hover
    title="Manage stages and their order"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
    </svg>
    <span class="btn-label">Stages</span>
  </button>  

  
  <button 
    class="btn btn-icon-text" 
    @click="originalApplyAll"
    v-b-tooltip.hover 
    title="Applies clustering to all pockets with one click"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-8 14l-5-5 1.41-1.41L11 14.17l6.59-6.59L19 9l-8 8z"/>
    </svg>
    <span class="btn-label">Apply</span>
  </button>

  
  <button 
    class="btn btn-icon-text" 
    @click="showSankey"
    v-b-tooltip.hover 
    title="Generates a Sankey diagram based on classification results"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M3 6h8c2 0 3 1 4 2.5s2 2.5 4 2.5h4v2h-4c-2 0-3-1-4-2.5s-2-2.5-4-2.5H3v-2zm0 6h6c2 0 3 1 4 2.5s2 2.5 4 2.5h4v2h-4c-2 0-3-1-4-2.5s-2-2.5-4-2.5H3v-2z"/>
    </svg>
    <span class="btn-label">Linkage</span>
  </button>

  
  <button 
    class="btn btn-icon-text" 
    @click="toggleCollectMemo"
    v-b-tooltip.hover 
    :title="showCollectCode ? 'Switch to Memo panel' : 'Switch to Collect Code view'"
  >
    <svg v-if="showCollectCode" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M19 3H4.99c-1.11 0-1.98.9-1.98 2L3 19c0 1.1.88 2 1.99 2H19c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 12h-4c0 1.66-1.35 3-3 3s-3-1.34-3-3H4.99V5H19v10z"/>
    </svg>
    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-1 9h-4v3l-3-4 3-4v3h4v2z"/>
    </svg>
    <span class="btn-label">{{ showCollectCode ? 'Memo' : 'Collect' }}</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    :class="{ active: showFinalView }"
    @click="toggleFinalView"
    v-b-tooltip.hover 
    title="Toggle Final Linkage View"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z"/>
    </svg>
    <span class="btn-label">Final</span>
  </button>
</div>
      </div>

      
      <div v-if="showStageModal" class="stage-modal-overlay">
        <div class="stage-modal-container">
          <div class="stage-modal-header">
            <h3>Manage Stages</h3>
            <button @click="toggleStageModal" class="close-button">×</button>
          </div>
          <div class="stage-list" ref="stageList">
            <div 
              v-for="(stage, index) in stageOrder" 
              :key="stage" 
              class="stage-item"
              draggable="true"
              @dragstart="dragStart($event, index)"
              @dragover.prevent
              @drop="drop($event, index)"
            >
              {{ stage }}
            </div>
          </div>
        </div>
      </div>

      
      <div v-if="!arePocketsVisible" class="umap-overview-bar">
        <div class="umap-overview-codes">
          <label
            v-for="code in allUniqueCodeNames"
            :key="code"
            class="umap-overview-item"
          >
            <input type="checkbox" v-model="umapCodeSelection[code]" />
            <span class="umap-overview-swatch" :style="{ background: colorLibrary[code] || '#A0BF7C' }"></span>
            <span class="umap-overview-name">{{ code }}</span>
          </label>
        </div>
        <button class="btn btn-icon-text umap-draw-btn" @click="drawMultiUmap" title="Draw UMAP for selected codes">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
            <circle cx="6" cy="6" r="2" fill="currentColor"/>
            <circle cx="18" cy="8" r="2" fill="currentColor"/>
            <circle cx="10" cy="16" r="2" fill="currentColor"/>
            <circle cx="16" cy="18" r="2" fill="currentColor"/>
            <circle cx="12" cy="10" r="2" fill="currentColor"/>
          </svg>
          <span class="btn-label">Draw UMAP</span>
        </button>
      </div>

      <div 
  v-for="(passage, passageName) in passageDatabase" 
  :key="passageName" 
  class="passage-row"
  :class="{ 'compact-view': !arePocketsVisible }"
>
        <div class="passage-header">
          <h3 class="passage-title" 
              :ref="el => setTitleRef(passageName, el)" 
              :style="titleStyle"
          >{{ passageName }}
            <span class="underline"></span>
          </h3>
          <div 
      :ref="el => setChartRef(passageName, el)" 
      class="passage-chart-container"
    ></div>
          <button @click="enterEditMode(passageName)" class="edit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 0 0 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83l3.75 3.75l1.83-1.83z"/>
            </svg>
          </button>
        </div>

        
        <div v-if="arePocketsVisible" class="classified-container">
          <div class="pockets-wrapper">
            <div class="pocket-list">
              
              <div 
  v-for="(secondCode, index) in uniqueSecondCodes(passage)" 
  :key="index" 
  class="pocket-card"
  @dragover.prevent="handleDragOver($event, passageName, secondCode)"
  @drop="handleDrop($event, passageName, secondCode)"
>
  <div class="pocket-header" :style="{ background: colorLibrary[secondCode] || '#A0BF7C' }">
    <button class="edit-pocket-btn" @click.stop="showEditModal(secondCode, passageName)" title="Edit pocket">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
</button>
<span class="pocket-title-text" @contextmenu.prevent="showContextMenu($event, 'Second-Order Code Notes', secondCode)">{{ secondCode }}</span>
<button class="delete-pocket-btn" @click.stop="showDeleteConfirm(secondCode, passageName)" title="Delete this pocket">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
    <path d="M3 6h18"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
</button>
  </div>
  <div class="pocket-content">
    <span 
      v-for="(code, idx) in getFirstOrderCodesForSecondCode(passage, secondCode).split(', ')" 
      :key="idx"
      class="code-tag"
      draggable="true"
      @dragstart="handleDragStart($event, passageName, secondCode, code)"
      @click.stop="selectAndJump(passageName, code)"
      @contextmenu.prevent="showContextMenu($event, 'First-Order Code Notes', code)"
    >
      {{ code }}
    </span>
  </div>
</div>


<div 
  class="pocket-card unclassified-pocket"
  @dragover.prevent="handleDragOver($event, passageName, 'unclassified')"
  @drop="handleDrop($event, passageName, 'unclassified')"
>
  <div class="pocket-header">Unclassified Codes</div>
  <div class="pocket-content">
    <span 
      v-for="(code, idx) in passage.firstOrderCodes.filter((code, idx) => !passage.secondOrderCodes[idx])" 
      :key="idx"
      class="code-tag"
      draggable="true"
      @dragstart="handleDragStart($event, passageName, 'unclassified', code)"
      @click.stop="selectAndJump(passageName, code)"
      @contextmenu.prevent="showContextMenu($event, 'First-Order Code Notes', code)"
    >
      {{ code }}
    </span>
  </div>
</div>
            </div>
          </div>
        </div>

        
      </div>
    </div>

    
    <div v-if="showFinalView" class="final-view-container">
      <div class="overview-header">
        <div class="header-title font-semibold text-[#407434]">
          Final Linkage View
        </div>
        <div class="button-group">
          <div class="final-spacing-control" style="display:flex;align-items:center;gap:6px;">
            <label style="font-size:0.75rem;white-space:nowrap;">Spacing: {{ finalSpacingFactor.toFixed(1) }}</label>
            <input
              type="range"
              v-model.number="finalSpacingFactor"
              :min="0.3" :max="3.0" step="0.1"
              @mouseup="drawFinalView"
              style="width:80px;"
            />
          </div>
          <button class="btn btn-icon-text" @click="downloadFinalSvg" title="Export as SVG">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
            </svg>
            <span class="btn-label">SVG</span>
          </button>
          <button class="btn btn-icon-text" @click="clearAllFinalLinks" title="Clear all links in Final View">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" style="color:#e53935;">
              <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
            <span class="btn-label" style="color:#e53935;">Clear</span>
          </button>
          <button class="btn btn-icon-text" @click="toggleFinalView" title="Close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
            <span class="btn-label">Close</span>
          </button>
        </div>
      </div>
      <div class="final-charts-wrapper" style="overflow-y:auto; overflow-x:hidden; height: calc(100% - 40px);">
        <div class="final-chart-section">
          <h4 class="chart-title" style="margin:8px 0 4px 12px;color:#407434;">View 1 — Bundled Linkage View</h4>
          <div id="final-bundled-chart" class="sankey-chart-container" style="min-height:400px;"></div>
        </div>
        <div class="final-chart-section">
          <h4 class="chart-title" style="margin:8px 0 4px 12px;color:#407434;">View 2 — Combined Linkage View</h4>
          <div id="final-combined-chart" class="sankey-chart-container" style="min-height:300px;"></div>
        </div>
      </div>
    </div>

    
    <div v-if="finalContextMenuVisible"
         class="context-menu-bubble"
         :style="{ left: `${finalContextMenuPos.x}px`, top: `${finalContextMenuPos.y}px` }"
         @click.stop>
      <button v-if="finalContextMenuTarget.type === 'link'" class="context-menu-btn" @click="finalContextMemo">+memo</button>
      <button class="context-menu-btn" style="color:#e53935;" @click="finalContextDelete">Delete</button>
    </div>

    
    <div v-else-if="isEditing">
      <div class="overview-header">
        <div class="header-title font-semibold text-[#407434]">
          Hierarchy View of {{ currentPassage }}
        </div>
        <div class="button-group">
  
  <button 
    class="btn btn-icon-text"
    @click="addNewPocket"
    v-b-tooltip.hover 
    title="Add a new pocket to organize codes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
    </svg>
    <span class="btn-label">Add Card</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="MergePockets"
    v-b-tooltip.hover 
    title="Merge selected pockets into one"
  >
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
  <path fill="currentColor" d="M4 6h6v12H4V6zm10 0h6v12h-6V6zm-5 5h2v2H9v-2z"/>
  <path stroke="currentColor" stroke-width="2" d="M10 12h4"/>
</svg>
    <span class="btn-label">Merge</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="showDeletedKeywords"
    v-b-tooltip.hover 
    title="View and restore deleted keywords"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
    </svg>
    <span class="btn-label">Trash</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="multiAbsorb"
    v-b-tooltip.hover 
    title="Absorb multiple codes into a pocket"
  >
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
    <path fill="currentColor" d="M12 3l8 8h-5v8h-6v-8H4l8-8zm-2 12h4v2h-4v-2z"/>
  </svg>
    <span class="btn-label">Absorb</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="exitEditMode"
    v-b-tooltip.hover 
    title="Exit edit mode"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>
    <span class="btn-label">Exit</span>
  </button>
</div>
      </div>
      <div id="chart-container" class="scrollable-container">
        <div id="chart"></div>
      </div>
    </div>

    
    <div v-if="umapActive" class="umap-overlay-container">
      <div class="overview-header">
        <div class="header-title font-semibold text-[#407434]">
          Hierarchy View of {{ umapTitle }}
        </div>
        <div class="button-group">
          
          <button 
            class="btn btn-icon-text"
            @click="toggleUmapBrush"
            v-b-tooltip.hover 
            :title="umapBrushActive ? 'Exit Selection Mode' : 'Enter Selection Mode'"
            :class="{ active: umapBrushActive }"
            :style="umapBrushActive ? 'background-color: #e8f5e9; color: #2e7d32;' : ''"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M3 3h4v2H5v2H3V3m14 0h4v4h-2V5h-2V3M3 17v4h4v-2H5v-2H3m14 4h4v-4h-2v2h-2v2M9 3h6v2H9V3m9 6h2v6h-2V9M9 19h6v2H9v-2M3 9h2v6H3V9z"/>
            </svg>
            <span class="btn-label">{{ umapBrushActive ? 'Dragging' : 'Select' }}</span>
          </button>
          
          <button 
            class="btn btn-icon-text"
            @click="exitUmapOverlay"
            v-b-tooltip.hover 
            title="Exit UMAP view"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
            <span class="btn-label">Exit</span>
          </button>
        </div>
      </div>
      
      <div v-if="umapLoading" class="umap-loading">
        <div class="loading-spinner"></div>
        <div class="loading-text">Computing UMAP projection...</div>
      </div>
      
      <div v-else class="umap-chart-area">
        <div id="umap-chart-container" class="umap-chart-wrapper"></div>
        
        
        <div v-if="showUmapSelectionPanel" class="umap-selection-panel">
          <div class="panel-header">
            <h4>Selection ({{ selectedUmapPoints.length }})</h4>
            <button class="close-btn" @click="showUmapSelectionPanel = false; toggleUmapBrush()">×</button>
          </div>
          <div class="panel-body">
            <button class="action-btn cluster-btn" @click="handleAnalyzeCluster">
              Cluster Features (Memo)
            </button>
            
            <div class="reclassify-section">
              <label>Second-Order Code</label>
              <div
                v-if="!umapSecondCodeTextEdit"
                class="umap-soc-selector"
                @click.stop="umapSecondCodeDropdownOpen = !umapSecondCodeDropdownOpen"
                @dblclick.prevent.stop="enterUmapSecondCodeTextEdit"
              >
                <span class="umap-soc-value">{{ newSecondOrderCodeInput || 'Select code...' }}</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" class="umap-soc-chevron" :class="{ 'rotate': umapSecondCodeDropdownOpen }">
                  <path fill="#6b7280" d="M7 10l5 5l5-5z"/>
                </svg>
              </div>
              <div v-if="umapSecondCodeDropdownOpen && !umapSecondCodeTextEdit" class="umap-soc-dropdown" @click.stop>
                <div
                  v-for="sc in allSecondCodes"
                  :key="sc"
                  class="umap-soc-option"
                  :class="{ 'active': sc === newSecondOrderCodeInput }"
                  @click="selectUmapSecondCode(sc)"
                >
                  {{ sc }}
                </div>
                <div v-if="allSecondCodes.length === 0" class="umap-soc-option disabled">No codes available</div>
              </div>
              <input
                v-if="umapSecondCodeTextEdit"
                v-model="newSecondOrderCodeInput"
                class="umap-soc-input"
                ref="umapSecondCodeInputRef"
                placeholder="Create new code..."
                @blur="umapSecondCodeTextEdit = false"
                @keyup.enter="umapSecondCodeTextEdit = false"
              />
              <button class="action-btn save-btn" @click="handleReclassify">
                Re-classify & Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

<div v-if="isCompressed" class="compressed-view-container">
  <div class="compressed-header">
    <h3>Hierarchy View</h3>
    
    <div class="sort-controls">
  <label>Sort Method:</label>
  <select v-model="currentSortMode" @change="handleSortModeChange">
    <option value="total">Total Code Count</option>
    <option value="classified">Classified Count</option>
    <option value="ratio">Classification Rate</option>
    <option value="byTopic">Sort by Topic</option>
  </select>
  <select 
    v-if="currentSortMode === 'byTopic'" 
    v-model="selectedTopic" 
    @change="drawBarChart" 
    class="topic-select"
  >
    <option value="">Select Topic</option>
    <option v-for="topic in availableTopics" :key="topic" :value="topic">{{ topic }}</option>
  </select>
 </div>

 <button 
            class="btn btn-icon-text"
            @click="exportasSvg" 
            title="Export as SVG"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
            </svg>
            <span class="btn-label">SVG</span>
          </button>

    <button @click="exitCompressedView" class="exit-button">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path fill="currentColor" d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41z"/>
      </svg>
    </button>
  </div>
  <div id="compressed-view"></div>
  <div id="compressed-tooltip" class="chart-tooltip"></div>
</div>

    
    <div v-if="showLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">Calculating the similarity....</div>
    </div>

    
    <DeletedKeywordsAlert 
      v-if="showDeletedKeywordsAlert" 
      :deletedKeywords="deletedKeywords" 
      @restore-keyword="restoreKeyword"
      @close="closeDeletedKeywordsAlert"
    />

    
    <div v-if="showDeleteModal" class="delete-modal-overlay">
      <div class="delete-modal-container">
        <h3>Confirm Deletion</h3>
        <p>Delete "{{ deleteTarget.pocketName }}" pocket?</p>
        <div class="delete-options">
          <label>
            <input type="radio" v-model="deleteScope" value="single" />
            Delete only this card
          </label>
          <label>
            <input type="radio" v-model="deleteScope" value="all" />
            Delete all cards with this name
          </label>
        </div>
        <div class="modal-buttons">
          <button @click="confirmDelete" class="confirm-btn">Confirm</button>
          <button @click="cancelDelete" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>

    
  <div v-if="showApplyAllModal" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <div class="mode-toggle-container">
            <span class="toggle-label">Preserve existing results</span>

            

            <button
              class="switch"
              :class="{ active: processingMode === 'sweep' }"
              @click="processingMode = (processingMode === 'sweep' ? 'extract' : 'sweep')"
              aria-pressed="false"
            >
              <span class="thumb"></span>
            </button>
          </div>

        <div style="display: flex; justify-content: flex-end; gap: 8px;">
          
          <button class="start-button" @click="handleStartProcessing">Start</button>
          <button class="start-button" @click="showApplyAllModal = false">×</button>
        </div>
      </div>

      
      <div class="merged-content">
        
        <div class="existing-codes-section">
          <div class="section-header">
            <h4 class="custom-bordered-header">Existing Second Order Codes</h4>
            <button @click="toggleSelectAllExisting" class="select-all-btn">
  <svg v-if="isAllExistingSelected" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="icon">
    <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
  </svg>

  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="icon">
    <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 0 1 .208 1.04l-9 13.5a.75.75 0 0 1-1.154.114l-6-6a.75.75 0 0 1 1.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 0 1 1.04-.208Z" clip-rule="evenodd" />
  </svg>
</button>
          </div>
          <div class="code-grid">
            <div
              v-for="code in existingSecondCodes"
              :key="code.name"
              class="code-item " 
              :style="{ background: code.backgroundStyle, color: 'black' }"
              :title="code.name"
            >
              <label>
                <input type="checkbox" v-model="selectedExistingCodes[code.name]" />
                <span class="code-name-label">{{ code.name }}</span>
                <span class="ratio-label">({{ code.count }}/{{ code.total }})</span>
              </label>
              
              <span class="info-icon" 
       @mouseover="showCodeTooltip($event, code.name)" 
       @mouseleave="hideCodeTooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z" />
                </svg>
              </span>
            </div>
          </div>
        </div>

        
        <div class="custom-input-section">
          <div class="section-header">
            <h4>Custom Second Order Codes</h4>
            <button @click="addCustomInput" class="add-btn">+</button>
          </div>

          

          <div class="input-container">
            <div v-for="(input, index) in customInputs" :key="index" class="input-row">
              <div class="input-group">
                
                <input
                  type="text"
                  v-model="input.code"
                  placeholder="Enter code"
                  class="custom-input code-input"
                  @change="updateExplanation(input.code, input.explanation)"
                />
                
                <input
                  type="text"
                  v-model="input.explanation"
                  placeholder="Enter explanation"
                  class="custom-input explanation-input"
                  @change="updateExplanation(input.code, input.explanation)"
                />
              </div>
              <button @click="removeCustomInput(index)" class="remove-btn" v-if="customInputs.length > 1">
                ×
              </button>
            </div>
          </div>

          
          <div class="semantic-option">
          <label>
            <input type="checkbox" v-model="includeExplanation" />
            Include explanation in semantic processing
          </label>

            <label >
              <input type="checkbox" v-model="isStrictMode" />
              Strict Mode
            </label>
      <label>
        <input type="checkbox" v-model="useLLMProcessing" />
        Use LLM
      </label>

        </div>
        </div>
      </div>
    </div>
  </div>

  
    

    
    <div v-if="processing" class="processing-overlay">
      <div class="processing-content">
        <div class="animate-spin mr-2">⏳</div>
        <div>
          Processing... Completed {{ processedCount }}/{{ totalFiles }} files,
          <span v-if="currentFile">
            Processing chunk {{ currentChunk }}/{{ totalChunks }} of {{ currentFile }}
          </span>
        </div>
      </div>
    </div>

  
  <transition name="panel-slide">
    <div v-if="showSankeyDiagram" 
         class="sankey-floating-panel" 
         :style="{ height: panelHeight + 'px' }"
         :class="{ 'dragging': isDraggingPanel }">
      
      
      <div class="panel-resize-handle" @mousedown="startResize">
        <div class="handle-bar"></div>
      </div>

      
      <div class="combined-view-controls">
            <div class="control-header">View Controls</div>
            <div class="control-row button-row" style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; justify-content: center;">
              <button class="btn btn-icon-text" style="padding: 8px 4px; font-size: 0.8rem;" @click="exportCSV" title="Export as CSV">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-1 9h-4v3l-3-4 3-4v3h4v2z"/>
                </svg>
                <span class="btn-label" style="font-size: 0.8rem;">CSV</span>
              </button>
              <button class="btn btn-icon-text" style="padding: 8px 4px; font-size: 0.8rem;" @click="exportSvg" title="Export as SVG">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                <span class="btn-label" style="font-size: 0.8rem;">SVG</span>
              </button>
            </div>
            <div class="control-row button-row" style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; justify-content: center;">
              <button class="btn btn-icon-text" style="padding: 8px 4px; font-size: 0.8rem;" @click="isCombined ? undoCombine() : combineStages()" :title="isCombined ? 'Undo' : 'Combine'">
                 <svg v-if="!isCombined" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M16.01 11H4v2h12.01v3L20 12l-3.99-4v3zM8 7h8v2H8V7zm0 8h8v2H8v-2z"/></svg>
                 <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/></svg>
                 <span class="btn-label" style="font-size: 0.8rem;">{{ isCombined ? 'Undo' : 'Combine' }}</span>
              </button>
              <button class="btn btn-icon-text" style="padding: 8px 4px; font-size: 0.8rem;" @click="exportToFinalView" title="Export current links to Final View">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>
                  <span class="btn-label" style="font-size: 0.8rem;">Export</span>
              </button>
              <button class="btn btn-icon-text" style="padding: 8px 4px; font-size: 0.8rem;" @click="showSankeyDiagram = false" title="Close">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                  <span class="btn-label" style="font-size: 0.8rem;">Close</span>
              </button>
            </div>
            
            <div class="control-item">
              <label class="control-label">Combined Min Count: {{ combinedThreshold }}</label>
              <input
                type="range"
                v-model.number="combinedThreshold"
                :min="combinedMinThreshold"
                :max="combinedMaxThreshold"
                step="1"
                @mouseup="updateSankey"
                class="mini-slider"
              />
            </div>

            <div class="control-item">
              <label class="control-label">Standard Min Count: {{ threshold }}</label>
              <input
                type="range"
                v-model.number="threshold"
                :min="minThreshold"
                :max="maxThreshold"
                step="1"
                class="mini-slider"
              />
            </div>

            <div class="control-item checkbox-item">
              <label class="control-label">
                <input 
                  type="checkbox" 
                  v-model="includeUnclassified" 
                  @change="updateSankey" 
                />
                Unclassified Nodes
              </label>
            </div>
            
             <div class="control-item">
              <label class="control-label">Spacing: {{ stageSpacingFactor }}</label>
              <input
                type="range"
                v-model.number="stageSpacingFactor"
                :min="0.3"
                :max="3.0"
                step="0.1"
                @mouseup="updateSankey"
                class="mini-slider"
              />
            </div>
          </div>

      <div class="sankey-panel-container">
        <div class="sankey-header" v-if="false">
          <div class="sankey-header-top">
            <h3 class="large-text">Linkage View<span class="small-gray-text"></span></h3>
            <div class="sankey-controls button-group">
              

              
              <button 
                class="btn btn-icon-text"
                @click="exportCSV" 
                title="Export as CSV"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-1 9h-4v3l-3-4 3-4v3h4v2z"/>
                </svg>
                <span class="btn-label">CSV</span>
              </button>

              
              <button 
                class="btn btn-icon-text"
                @click="exportSvg" 
                title="Export as SVG"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                <span class="btn-label">SVG</span>
              </button>

              
              <button 
              class="btn btn-icon-text"
              @click="combineStages" 
              title="Combine stages by second order codes" 
              :disabled="isCombined"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                <path fill="currentColor" d="M16.01 11H4v2h12.01v3L20 12l-3.99-4v3zM8 7h8v2H8V7zm0 8h8v2H8v-2z"/>
              </svg>
              <span class="btn-label">Combine</span>
              </button>

              
              <button 
                class="btn btn-icon-text"
                @click="undoCombine" 
                title="Undo the last combine operation" 
                :disabled="!isCombined"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/>
                </svg>
                <span class="btn-label">Undo</span>
              </button>

              
              <button 
                class="btn btn-icon-text"
                @click="showSankeyDiagram = false" 
                title="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
                <span class="btn-label">Close</span>
              </button>


            </div>
          </div>
          <template v-if="!isCombined">
            
            <div class="slider-container">
              <label for="threshold-slider">Minimum Count Threshold: {{ threshold }}</label>
              <input
                type="range"
                id="threshold-slider"
                v-model.number="threshold"
                :min="minThreshold"
                :max="maxThreshold"
                step="1"
              />
              <span>(Range: {{ minThreshold }} - {{ maxThreshold }})</span>
            </div>

            <div class="slider-container">
              <label for="stage-spacing-slider">Stage Horizontal Spacing: {{ stageSpacingFactor }}</label>
              <input
                type="range"
                id="stage-spacing-slider"
                v-model.number="stageSpacingFactor"
                :min="0.3"
                :max="3.0"
                step="0.1"
                @mouseup="updateSankey"
              />
              <span>(Range: 1.0 - 3.0)</span>
            </div>

            <div class="controls-row">
              <div class="checkbox-container">
                <label class="green-text">
                  <input type="checkbox" v-model="includeUnclassified" @change="updateStage" />
                  Include Unclassified Nodes
                </label>
              </div>
              
            </div>
          </template>
        </div>

        
        <div class="sankey-chart-group" :class="{ 'no-border': isCombined }" style="position: relative;" v-show="isCombined">
          <h4 class="chart-title">
            <span>Combined Linkage View</span>
            <span class="chart-description"></span>
          </h4>


          <div id="sankey-chart" class="sankey-chart-container"></div>
        </div>

        <div class="sankey-chart-group no-border" style="position: relative;" v-if="!isCombined">
          <h4 class="chart-title">Bundled Linkage View
            <span class="chart-description"></span>
          </h4>
          <div id="bundled-sankey-chart" class="sankey-chart-container"></div>
        </div>


     </div>
    </div>
  </transition>
</div>


<div v-if="tooltipVisible" 
     class="explanation-tooltip"
     :style="{ left: `${tooltipPosition.x}px`, top: `${tooltipPosition.y}px` }">
  {{ tooltipContent }}
</div>


<div v-if="contextMenuVisible" 
     class="context-menu-bubble"
     :style="{ left: `${contextMenuPosition.x}px`, top: `${contextMenuPosition.y}px` }"
     @click.stop>
  <button class="context-menu-btn" @click="confirmCreateMemo">
    +memo
  </button>
</div>

<div v-if="selectedNodeInfo" 
     class="fw-dbl-code-bubble"
     :style="{ left: `${selectedNodeInfo.x}px`, top: `${selectedNodeInfo.y}px` }"
     v-click-outside="closeCodeBubble">
  <div class="fw-dbl-bubble-header" @mousedown="startDrag">
    <div class="fw-dbl-title-wrapper">
      <svg class="fw-edit-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
        <path fill="#407434" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 0 0 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83l3.75 3.75l1.83-1.83z"/>
      </svg>
      <span class="fw-dbl-title">Edit Node</span>
    </div>
  </div>

  
  <div class="fw-edit-container">
    
    <div class="fw-edit-section fw-left-section">
      <h4 class="section-title">Second Order Code</h4>
      <div class="fw-dbl-code-options">
        <button 
          v-for="code in allSecondCodes" 
          :key="code"
          class="fw-dbl-code-btn"
          @click="updateNodeClassification(code)">
          {{ code }}
        </button>
        <button 
          class="fw-dbl-remove-btn"
          @click="updateNodeClassification(null)">
          Remove
        </button>
      </div>
    </div>

    
    <div class="fw-edit-section fw-right-section">
      <h4 class="section-title">Stages</h4>
      <div class="fw-stage-select">
        <select v-model="selectedNewStage">
          <option 
            v-for="stage in stageOrder" 
            :key="stage" 
            :value="stage">
            {{ stage }}
          </option>
        </select>
      </div>
      <div class="fw-scope-options">
        <label>
          <input type="radio" v-model="editScope" value="single"/>
          Single Node
        </label>
        <label>
          <input type="radio" v-model="editScope" value="hull"/>
          Entire Hull
        </label>
      </div>
      <button 
        class="fw-dbl-confirm-btn" 
        @click="confirmStageChange">
        Confirm Stage
      </button>
    </div>
  </div>
</div>


  <div v-if="showEditPocketModal" class="edit-modal-overlay">
    <div class="edit-modal-container">
      <h3>Edit Card</h3>
      <div class="edit-form">
        <label>
          Card Name:
          <input 
            type="text" 
            v-model="editPocketData.name" 
            @input="validateName"
          />
        </label>
        <label>
          Explanation:
          <textarea 
            v-model="editPocketData.explanation"
            rows="3"
          ></textarea>
        </label>
        <div class="edit-options">
          <label>
            <input type="radio" v-model="editScope" value="single" />
            Edit only this card
          </label>
          <label>
            <input type="radio" v-model="editScope" value="all" />
            Edit all cards with this name
          </label>
        </div>
      </div>
      <div class="modal-buttons">
        <button @click="savePocketEdit" class="confirm2-btn">Save</button>
        <button @click="cancelEdit" class="cancel2-btn">Cancel</button>
      </div>
    </div>
  </div>



</template>

<script setup>
import { onMounted, ref, watch, reactive, nextTick } from 'vue';
import * as d3 from 'd3';
import { usePoint } from '~/composables/state';
import { defineProps, useAttrs } from 'vue';
import DeletedKeywordsAlert from '@/components/DeletedKeywordsAlert.vue';
import MemoPanel from '@/components/MemoPanel.vue';
import cloud from 'd3-cloud'; 
import {computed, onUpdated, onBeforeUpdate} from 'vue';


const showStageModal = ref(false);
const stageOrder = ref([]);  
const showSankeyDiagram = ref(false);
const includeUnclassified = ref(true); 


const panelHeight = ref(400); 
const isDraggingPanel = ref(false);
const lastMouseY = ref(0);


const passageDatabase = reactive({});
const isEditing = ref(false);
const currentPassage = ref('');


const umapActive = ref(false);
const umapTitle = ref('');
const umapPoints = ref([]);
const umapLoading = ref(false);
const umapColorMap = ref({});
const umapCodeSelection = reactive({});


const umapBrushActive = ref(false);
const selectedUmapPoints = ref([]);
const showUmapSelectionPanel = ref(false);
const newSecondOrderCodeInput = ref('');
const umapSecondCodeDropdownOpen = ref(false);
const umapSecondCodeTextEdit = ref(false);
const umapSecondCodeInputRef = ref(null);
let currentUmapSvg = null;
let currentUmapZoom = null;
let currentUmapDrag = null;

const toggleUmapBrush = () => {
  umapBrushActive.value = !umapBrushActive.value;
  if (!currentUmapSvg) return;
  if (umapBrushActive.value) {
    currentUmapSvg.on('.zoom', null);
    currentUmapSvg.call(currentUmapDrag);
  } else {
    currentUmapSvg.on('.drag', null);
    currentUmapSvg.call(currentUmapZoom).on('dblclick.zoom', null);
    d3.select('.lasso-group path').style('display', 'none');
    d3.selectAll('.umap-chart-wrapper circle')
      .attr('stroke', function() { return d3.select(this).attr('data-default-stroke'); })
      .attr('stroke-width', 1.5);
    selectedUmapPoints.value = [];
    showUmapSelectionPanel.value = false;
    umapSecondCodeDropdownOpen.value = false;
    umapSecondCodeTextEdit.value = false;
  }
};

const selectUmapSecondCode = (code) => {
  newSecondOrderCodeInput.value = code;
  umapSecondCodeDropdownOpen.value = false;
};



const showFinalView = ref(false);
const finalLinks = ref([]);
const finalSpacingFactor = ref(1.0);

const finalContextMenuVisible = ref(false);
const finalContextMenuPos = reactive({ x: 0, y: 0 });

const finalContextMenuTarget = ref(null); 

const toggleFinalView = () => {
  showFinalView.value = !showFinalView.value;
  if (showFinalView.value) {
    if (showSankeyDiagram.value) showSankeyDiagram.value = false;
    fetchFinalLinks().then(() => {
      drawFinalView();
    });
  }
};

const clearAllFinalLinks = async () => {
  if (confirm('Are you sure you want to clear ALL links in the Final View?')) {
    try {
      const res = await fetch('http://localhost:5002/api/final-linkage/all', { method: 'DELETE' });
      if (res.ok) {
        await fetchFinalLinks();
        drawFinalView();
      }
    } catch (err) {
      console.error('Failed to clear all final links', err);
    }
  }
};

const downloadFinalSvg = () => {
  const chartConfigs = [
    { selector: '#final-bundled-chart svg', filename: 'final_bundled_linkage' },
    { selector: '#final-combined-chart svg', filename: 'final_combined_linkage' }
  ];
  let exportedCount = 0;
  const timestamp = new Date().toISOString();
  chartConfigs.forEach(config => {
    const svgElement = document.querySelector(config.selector);
    if (svgElement) {
      const svgClone = svgElement.cloneNode(true);
      const serializer = new XMLSerializer();
      let svgString = serializer.serializeToString(svgClone);
      svgString = '<?xml version="1.0" standalone="no"?>\n' +
                 '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n' +
                 svgString;
      const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${config.filename}_${timestamp}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      exportedCount++;
    }
  });
  if (exportedCount === 0) alert('No Final View SVGs found');
};

const fetchFinalLinks = async () => {
  try {
    const response = await fetch('http://localhost:5002/api/final-linkage');
    if (response.ok) {
      finalLinks.value = await response.json();
    }
  } catch (err) {
    console.error("Failed to fetch final links", err);
  }
};

const drawFinalView = () => {
  if (!showFinalView.value) return;
  drawFinalBundledSankey();
  drawFinalCombinedSankey();
};

const validateLinkAdjacency = (sourceStage, targetStage) => {
  const sourceIndex = stageOrder.value.indexOf(sourceStage);
  const targetIndex = stageOrder.value.indexOf(targetStage);
  
  return sourceIndex !== -1 && targetIndex !== -1 && targetIndex === sourceIndex + 1;
};


const addMemoLinkToFinal = async ({ code1, code2 }) => {
  
  let validLink = null;
  for (const passageName in passageDatabase) {
    const p = passageDatabase[passageName];
    const idx1 = p.firstOrderCodes.indexOf(code1);
    const idx2 = p.firstOrderCodes.indexOf(code2);
    if (idx1 !== -1 && idx2 !== -1) {
      const stage1 = p.stages[idx1];
      const stage2 = p.stages[idx2];
      if (validateLinkAdjacency(stage1, stage2)) {
        
        const sc1 = p.secondOrderCodes[idx1] || 'unclassified';
        const sc2 = p.secondOrderCodes[idx2] || 'unclassified';
        
        validLink = {
          id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
          sourceCode: code1,
          sourceSecondCode: sc1,
          sourceStage: stage1,
          targetCode: code2,
          targetSecondCode: sc2,
          targetStage: stage2,
          passages: [passageName],
          value: 1, 
          createdAt: new Date().toISOString()
        };
        break; 
      } else if (validateLinkAdjacency(stage2, stage1)) {
        
        const sc1 = p.secondOrderCodes[idx2] || 'unclassified';
        const sc2 = p.secondOrderCodes[idx1] || 'unclassified';
        validLink = {
          id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
          sourceCode: code2,
          sourceSecondCode: sc2,
          sourceStage: stage2,
          targetCode: code1,
          targetSecondCode: sc1,
          targetStage: stage1,
          passages: [passageName],
          value: 1,
          createdAt: new Date().toISOString()
        };
        break;
      }
    }
  }

  if (!validLink) {
    alert("This link is invalid. The codes must belong to adjacent stages.");
    return;
  }

  
  try {
    const res = await fetch('http://localhost:5002/api/final-linkage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(validLink)
    });
    if (res.ok) {
      if (showFinalView.value) {
        await fetchFinalLinks();
        drawFinalView();
      }
      alert('Link successfully added to Final View!');
    }
  } catch (err) {
    console.error("Failed to add memo link to final", err);
  }
};

const exportToFinalView = async () => {
  
  const linksToExport = [];
  Object.entries(pathLibrary).forEach(([pathKey, linkState]) => {
    
    if (linkState < threshold.value) return;

    const parts = pathKey.split('|');
    if (parts.length === 2) {
      const srcParts = parts[0].split('#');
      const tgtParts = parts[1].split('#');
      if (srcParts.length === 2 && tgtParts.length === 2) {
        const sourceCode = srcParts[0];
        const sourceStage = srcParts[1];
        const targetCode = tgtParts[0];
        const targetStage = tgtParts[1];
        
        
        if (!validateLinkAdjacency(sourceStage, targetStage)) return;

        
        let sc1 = 'unclassified'; let sc2 = 'unclassified';
        let matchedPassages = new Set();
        Object.entries(passageDatabase).forEach(([pname, p]) => {
          const idx1 = p.firstOrderCodes.indexOf(sourceCode);
          const idx2 = p.firstOrderCodes.indexOf(targetCode);
          if (idx1 !== -1 && idx2 !== -1 && p.stages[idx1] === sourceStage && p.stages[idx2] === targetStage) {
             sc1 = p.secondOrderCodes[idx1] || 'unclassified';
             sc2 = p.secondOrderCodes[idx2] || 'unclassified';
             matchedPassages.add(pname);
          }
        });
        
        if (matchedPassages.size > 0) {
          linksToExport.push({
            id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
            sourceCode,
            sourceSecondCode: sc1,
            sourceStage,
            targetCode,
            targetSecondCode: sc2,
            targetStage,
            passages: Array.from(matchedPassages),
            value: linkState.value || matchedPassages.size,
            createdAt: new Date().toISOString()
          });
        }
      }
    }
  });

  if (linksToExport.length === 0) {
    alert('No valid adjacent links found in the current view to export.');
    return;
  }

  try {
    const res = await fetch('http://localhost:5002/api/final-linkage/bulk', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(linksToExport)
    });
    if (res.ok) {
        alert('Successfully exported to Final View!');
        if (showFinalView.value) {
            await fetchFinalLinks();
            drawFinalView();
        }
    }
  } catch (err) {
    console.error('Export fail:', err);
  }
};

const showFinalContextMenu = (event, type, target) => {
  event.preventDefault();
  finalContextMenuPos.x = event.clientX;
  finalContextMenuPos.y = event.clientY;
  finalContextMenuTarget.value = { type, data: target };
  finalContextMenuVisible.value = true;
};

const closeFinalContextMenu = () => {
  finalContextMenuVisible.value = false;
};

const finalContextMemo = () => {
  if (finalContextMenuTarget.value && finalContextMenuTarget.value.type === 'link') {
    const l = finalContextMenuTarget.value.data;
    const title = `${l.source.label}—${l.target.label}`; 
    createMemoWithTitle('Theoretical Memos', title);
  }
  closeFinalContextMenu();
};

const finalContextDelete = async () => {
  if (!finalContextMenuTarget.value) return;
  const target = finalContextMenuTarget.value;
  try {
    if (target.type === 'link') {
      const linkId = target.data.originalData ? target.data.originalData.id : null;
      if (linkId) {
        await fetch(`http://localhost:5002/api/final-linkage/${linkId}`, { method: 'DELETE' });
      } else if (target.data.links) {
        
        for (const childLink of target.data.links) {
           if(childLink.originalData && childLink.originalData.id) {
               await fetch(`http://localhost:5002/api/final-linkage/${childLink.originalData.id}`, { method: 'DELETE' });
           }
        }
      }
    } else if (target.type === 'node') {
      
      const code = target.data.label; 
      const stage = target.data.stage;
      await fetch(`http://localhost:5002/api/final-linkage/node?code=${encodeURIComponent(code)}&stage=${encodeURIComponent(stage)}`, { method: 'DELETE' });
    }
    
    await fetchFinalLinks();
    drawFinalView();
  } catch (err) {
    console.error("Failed to delete", err);
  }
  closeFinalContextMenu();
};

onMounted(() => {
  document.addEventListener('click', closeFinalContextMenu);
});
onUnmounted(() => {
  document.removeEventListener('click', closeFinalContextMenu);
});



const buildFinalViewData = (isCombinedView) => {
  const nodesMap = new Map();
  const linksMap = new Map();

  const getNodeKey = (code, scode, stage) => {
    return isCombinedView ? `${scode}#${stage}` : `${code}#${stage}`;
  };

  const getNodeLabel = (code, scode) => {
    return isCombinedView ? scode : code;
  };

  finalLinks.value.forEach(fl => {
    const sKey = getNodeKey(fl.sourceCode, fl.sourceSecondCode, fl.sourceStage);
    const tKey = getNodeKey(fl.targetCode, fl.targetSecondCode, fl.targetStage);

    if (!nodesMap.has(sKey)) {
      nodesMap.set(sKey, { key: sKey, label: getNodeLabel(fl.sourceCode, fl.sourceSecondCode), stage: fl.sourceStage, secondCode: fl.sourceSecondCode, value: 0 });
    }
    if (!nodesMap.has(tKey)) {
      nodesMap.set(tKey, { key: tKey, label: getNodeLabel(fl.targetCode, fl.targetSecondCode), stage: fl.targetStage, secondCode: fl.targetSecondCode, value: 0 });
    }

    const sNode = nodesMap.get(sKey);
    const tNode = nodesMap.get(tKey);
    
    if (!isCombinedView) {
      sNode.value += fl.value;
      tNode.value += fl.value;
    } else {
      
      sNode.outVal = (sNode.outVal || 0) + fl.value;
      tNode.inVal = (tNode.inVal || 0) + fl.value;
      sNode.value = Math.max(sNode.inVal || 0, sNode.outVal || 0);
      tNode.value = Math.max(tNode.inVal || 0, tNode.outVal || 0);
    }

    const linkKey = `${sKey}->${tKey}`;
    if (!linksMap.has(linkKey)) {
      linksMap.set(linkKey, {
        source: sNode,
        target: tNode,
        value: 0,
        originalData: isCombinedView ? null : fl,
        links: isCombinedView ? [] : [fl] 
      });
    }
    const L = linksMap.get(linkKey);
    L.value += fl.value;
    if (isCombinedView) L.links.push(fl);
  });

  const nodes = Array.from(nodesMap.values()).map((n, i) => ({ ...n, id: i }));
  
  const nodesByKey = new Map(nodes.map(n => [n.key, n]));
  const links = Array.from(linksMap.values()).map(l => ({
    ...l,
    source: nodesByKey.get(l.source.key),
    target: nodesByKey.get(l.target.key),
  }));

  return { nodes, links };
};

const drawFinalBundledSankey = () => {
  const containerId = '#final-bundled-chart';
  const chartContainer = d3.select(containerId);
  chartContainer.selectAll('*').remove();

  if (finalLinks.value.length === 0) {
    chartContainer.append('div').style('padding', '20px').text('No final links available.');
    return;
  }

  const { nodes, links } = buildFinalViewData(false);
  renderFinalChart(chartContainer, nodes, links, false);
};

const drawFinalCombinedSankey = () => {
  const containerId = '#final-combined-chart';
  const chartContainer = d3.select(containerId);
  chartContainer.selectAll('*').remove();

  if (finalLinks.value.length === 0) {
    chartContainer.append('div').style('padding', '20px').text('No final links available.');
    return;
  }

  const { nodes, links } = buildFinalViewData(true);
  renderFinalChart(chartContainer, nodes, links, true);
};

const renderFinalChart = (chartContainer, nodes, links, isCombinedView) => {
  const numStages = stageOrder.value.length;
  let width = (2000 + nodes.length * 100) * finalSpacingFactor.value;
  let height = 600;

  const svg = chartContainer.append('svg').attr('width', width).attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
  const g = svg.append('g');

  const stageX = {};
  stageOrder.value.forEach((stage, i) => {
    stageX[stage] = (width / (numStages + 0.5)) * (i + 0.5);
  });

  const getColor = (sc) => colorLibrary[sc] || '#CCCCCC';
  nodes.forEach(n => {
     n.color = getColor(n.secondCode);
     n.inDegree = links.reduce((c, l) => c + (l.target.id === n.id ? 1 : 0), 0);
     n.outDegree = links.reduce((c, l) => c + (l.source.id === n.id ? 1 : 0), 0);
  });

  if (isCombinedView) {
    
    
    
    const stageTotals = stageOrder.value.map(st => d3.sum(nodes.filter(n => n.stage === st), d => d.value));
    const maxStageTotal = d3.max(stageTotals) || 1;
    const hScale = (height - 200) / maxStageTotal;
    
    
    links.forEach(l => { l.width = Math.max(2, l.value * hScale); });
    nodes.forEach(n => { n.height = Math.max(15, n.value * hScale); });

    
    stageOrder.value.forEach((st, i) => {
      const stageNodes = nodes.filter(n => n.stage === st);

      stageNodes.forEach(n => {
        const incomingLinks = links.filter(l => l.target.id === n.id);
        const outgoingLinks = links.filter(l => l.source.id === n.id);

        
        if (i > 0 && incomingLinks.length > 0) {
          n.height = d3.sum(incomingLinks, l => l.width);
          
          if (n.height < 5) n.height = Math.max(15, n.value * hScale);
        }

        
        const totalOutValue = d3.sum(outgoingLinks, l => l.value);
        if (totalOutValue > 0 && n.height > 0) {
          outgoingLinks.forEach(l => {
            
            l.width = (l.value / totalOutValue) * n.height;
          });
        }
      });
    });

    
    const intraSpacing = 30;
    stageOrder.value.forEach(st => {
      const stNodes = nodes.filter(n => n.stage === st);
      stNodes.sort((a,b) => b.value - a.value);
      
      const totalH = d3.sum(stNodes, n => n.height) + (stNodes.length - 1) * intraSpacing;
      let ny = (height - totalH) / 2;
      
      stNodes.forEach(n => {
         n.x = stageX[st];
         n.y = ny + n.height / 2; 
         ny += n.height + intraSpacing;
      });
    });

    const maxY = d3.max(nodes, n => n.y + n.height/2);
    if (maxY > height) {
      height = maxY + 100;
      svg.attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
    }

    
    const nodeW = 20;
    nodes.forEach(n => {
       const sources = links.filter(l => l.source.id === n.id).sort((a,b)=>a.target.y - b.target.y);
       const targets = links.filter(l => l.target.id === n.id).sort((a,b)=>a.source.y - b.source.y);
       
       
       let currentSy = n.y - n.height / 2;
       sources.forEach(l => { 
           l.sy = currentSy + l.width / 2; 
           currentSy += l.width; 
       });
       
       
       let currentTy = n.y - n.height / 2;
       targets.forEach(l => { 
           l.ty = currentTy + l.width / 2; 
           currentTy += l.width; 
       });
    });

    
    const linkP = l => {
      const startX = l.source.x + nodeW / 2;
      const endX = l.target.x - nodeW / 2;
      const xi = d3.interpolateNumber(startX, endX);
      const x2 = xi(0.5);
      return `M${startX},${l.sy} C${x2},${l.sy} ${x2},${l.ty} ${endX},${l.ty}`;
    };
    
    g.append('g').selectAll('.link').data(links).join('path').attr('class', 'link')
       .attr('d', linkP)
       .attr('stroke', d => d.source.color)
       .attr('stroke-width', d => d.width)
       .attr('stroke-opacity', 0.5)
       .attr('fill', 'none')
       .style('cursor', 'pointer')
       .on('contextmenu', (e, d) => showFinalContextMenu(e, 'link', d))
       .append('title').text(d => `${d.source.label} -> ${d.target.label}\nValue: ${d.value}`);

    const nodeG = g.append('g').selectAll('.node').data(nodes).join('g')
       .attr('class', 'node')
       .attr('transform', d=>`translate(${d.x},${d.y})`)
       .style('cursor', 'pointer')
       .on('contextmenu', (e, d) => showFinalContextMenu(e, 'node', d));
       
    nodeG.append('rect')
       .attr('x', -nodeW/2).attr('y', d => -d.height/2)
       .attr('width', nodeW).attr('height', d=>d.height)
       .attr('fill', d=>d.color);

    nodeG.append('text')
       .attr('dy', '-0.5em').attr('y', d => -d.height/2)
       .attr('text-anchor', 'middle')
       .style('font-size', '16px').style('fill', d=>d.color)
       .style('font-weight', 'bold')
       .text(d=>d.label);

    nodeG.append('title').text(d => `${d.label}\nStage: ${d.stage}\nValue: ${d.value}`);

    
    nodeG.on('click', function(e, d) {
        e.stopPropagation();
        g.selectAll('.link').transition().duration(200).attr('stroke-opacity', 0.05);
        g.selectAll('.node rect').transition().duration(200).style('opacity', 0.2);
        d3.select(this).select('rect').transition().duration(200).style('opacity', 1);
        g.selectAll('.link').filter(l => l.source.id === d.id || l.target.id === d.id)
          .transition().duration(200).attr('stroke-opacity', 0.8);
        const nbs = new Set();
        links.forEach(l => {
            if(l.source.id===d.id) nbs.add(l.target.id);
            if(l.target.id===d.id) nbs.add(l.source.id);
        });
        g.selectAll('.node').filter(n => nbs.has(n.id)).select('rect').transition().duration(200).style('opacity', 1);
    });
    
    svg.on('click', () => {
        g.selectAll('.link').transition().duration(200).attr('stroke-opacity', 0.5);
        g.selectAll('.node rect').transition().duration(200).style('opacity', 1);
    });

  } else {
    
    
    
    const fontSizeFactorVar = Math.min(12, 1 + nodes.length / 50);
    const minFs = 10, maxFs = 24;
    const fsScale = d3.scaleLinear().domain([1, d3.max(nodes, d=>d.value)||1]).range([minFs, maxFs]);

    nodes.forEach(n => {
      n.fontSize = fsScale(n.value) * fontSizeFactorVar;
      n.bboxHeight = n.fontSize * 1.2;
    });

    
    const maxLinkVal = d3.max(links, d => d.value) || 1;
    const linkWidthScale = d3.scaleLinear().domain([1, maxLinkVal]).range([3, 10]); 
    links.forEach(l => { 
      l.width = linkWidthScale(l.value); 
    });

    const stageGroups = {};
    stageOrder.value.forEach(st => {
      const sNodes = nodes.filter(n => n.stage === st);
      const groups = d3.group(sNodes, n => n.secondCode);
      const renderGroups = [];
      groups.forEach((gNodes, sc) => {
        gNodes.sort((a,b) => b.value - a.value);
        renderGroups.push({ id: `${st}-${sc}`, stage: st, secondCode: sc, color: getColor(sc), nodes: gNodes });
      });
      stageGroups[st] = renderGroups;
    });

    const intraSpacing = 10;
    const interSpacing = 60 * fontSizeFactorVar;
    
    stageOrder.value.forEach(st => {
      const groups = stageGroups[st];
      if(!groups) return;
      const totalH = d3.sum(groups, g => 30 + d3.sum(g.nodes, n=>n.bboxHeight) + g.nodes.length*intraSpacing) + groups.length*interSpacing;
      let currentY = (height - totalH) / 2;
      groups.forEach(g => {
         g.y = currentY; g.x = stageX[st];
         let ny = currentY + 30; 
         g.nodes.forEach(n => {
           n.x = g.x; n.y = ny + n.bboxHeight/2;
           ny += n.bboxHeight + intraSpacing;
         });
         g.height = ny - currentY;
         currentY = ny + interSpacing;
      });
    });

    const maxY = d3.max(nodes, n => n.y);
    if (maxY > height) {
      height = maxY + 100;
      svg.attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
    }

    const allHulls = [];
    Object.values(stageGroups).forEach(groups => {
      groups.forEach(g => {
        const pts = [];
        g.nodes.forEach(n => {
           const w = n.fontSize * n.label.length * 0.6;
           const pad = 15;
           pts.push([n.x - w/2 - pad, n.y - n.bboxHeight/2 - pad]);
           pts.push([n.x + w/2 + pad, n.y - n.bboxHeight/2 - pad]);
           pts.push([n.x - w/2 - pad, n.y + n.bboxHeight/2 + pad]);
           pts.push([n.x + w/2 + pad, n.y + n.bboxHeight/2 + pad]);
        });
        if(pts.length > 0) allHulls.push({ color: g.color, points: d3.polygonHull(pts) || pts, group: g });
      });
    });

    const hullPath = d3.line().x(d=>d[0]).y(d=>d[1]).curve(d3.curveCatmullRomClosed.alpha(0.5));
    
    g.append('g').attr('class', 'hulls').selectAll('.hull').data(allHulls).join('path')
     .attr('d', d => hullPath(d.points.concat([d.points[0]])))
     .style('fill', d => d.color).style('fill-opacity', 0.2).style('stroke', d => d.color).style('stroke-width', 2);
    
    g.append('g').selectAll('.hull-lb').data(allHulls).join('text')
     .attr('x', d => d.group.x).attr('y', d => d.group.y)
     .attr('text-anchor', 'middle').text(d => d.group.secondCode).style('fill', d => d.color)
     .style('font-size', `${20 * fontSizeFactorVar}px`).style('font-weight', 'bold');

    
    const linkP = l => {
      
      const srcHalfW = (l.source.fontSize * l.source.label.length * 0.6) / 2;
      const tgtHalfW = (l.target.fontSize * l.target.label.length * 0.6) / 2;
      
      
      const startX = l.source.x + srcHalfW + 2;
      const endX = l.target.x - tgtHalfW - 2;

      const xi = d3.interpolateNumber(startX, endX);
      const x2 = xi(0.5);
      return `M${startX},${l.source.y} C${x2},${l.source.y} ${x2},${l.target.y} ${endX},${l.target.y}`;
    };
    
    g.append('g').selectAll('.link').data(links).join('path').attr('class', 'link')
     .attr('d', linkP).attr('stroke', d => d.source.color).attr('stroke-width', d => d.width)
     .attr('stroke-opacity', 0.5).attr('fill', 'none')
     .style('cursor', 'pointer')
     .on('contextmenu', (e, d) => showFinalContextMenu(e, 'link', d))
     .append('title').text(d => `${d.source.label} -> ${d.target.label}\nValue: ${d.value}`);

    const nodeG = g.append('g').selectAll('.node').data(nodes).join('g')
     .attr('class', 'node')
     .attr('transform', d=>`translate(${d.x},${d.y})`)
     .style('cursor', 'pointer')
     .on('contextmenu', (e, d) => showFinalContextMenu(e, 'node', d));

    nodeG.append('text').attr('dy', '0.35em').attr('text-anchor', 'middle')
     .style('font-size', d=>`${d.fontSize}px`).text(d=>d.label)
     .append('title').text(d => `${d.label}\nStage: ${d.stage}\nValue: ${d.value}`);

    nodeG.on('click', function(e, d) {
        e.stopPropagation();
        g.selectAll('.link').transition().duration(200).attr('stroke-opacity', 0.05);
        g.selectAll('text').transition().duration(200).style('opacity', 0.2);
        d3.select(this).select('text').transition().duration(200).style('opacity', 1).style('font-weight', 'bold');
        g.selectAll('.link').filter(l => l.source.id === d.id || l.target.id === d.id)
         .transition().duration(200).attr('stroke-opacity', 0.8);
        const nbs = new Set();
        links.forEach(l => {
            if(l.source.id===d.id) nbs.add(l.target.id);
            if(l.target.id===d.id) nbs.add(l.source.id);
        });
        g.selectAll('.node').filter(n => nbs.has(n.id)).select('text').transition().duration(200).style('opacity', 1).style('font-weight', 'bold');
        g.selectAll('.hull-lb').transition().duration(200).style('opacity', 1);
    });
    
    svg.on('click', () => {
        g.selectAll('.link').transition().duration(200).attr('stroke-opacity', 0.5);
        g.selectAll('text').transition().duration(200).style('opacity', 1).style('font-weight', 'normal');
    });
  }

  
  const zoom = d3.zoom().scaleExtent([0.1, 5]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom).on('dblclick.zoom', null);
  
  const cw = chartContainer.node().clientWidth, ch = chartContainer.node().clientHeight;
  const sc = Math.min(cw/width, ch/height) * 0.95;
  svg.call(zoom.transform, d3.zoomIdentity.translate((cw-width*sc)/2, (ch-height*sc)/2).scale(sc));
};
const enterUmapSecondCodeTextEdit = () => {
  umapSecondCodeDropdownOpen.value = false;
  umapSecondCodeTextEdit.value = true;
  nextTick(() => {
    if (umapSecondCodeInputRef.value) umapSecondCodeInputRef.value.focus();
  });
};

const handleAnalyzeCluster = () => {
  if (selectedUmapPoints.value.length === 0) return;
  
  const timestamp = Date.now().toString();
  const clusterDataArray = [];
  
  selectedUmapPoints.value.forEach(pt => {
    const code = pt.name;
    const items = [];
    Object.entries(passageDatabase).forEach(([passage, p]) => {
      p.firstOrderCodes.forEach((foc, idx) => {
        if (foc === code) {
          items.push({
            passage,
            sentence: p.sentences ? p.sentences[idx] : '',
            explanation: p.explanations ? p.explanations[idx] : '',
            originalSecondOrderCode: p.secondOrderCodes[idx] || ''
          });
        }
      });
    });
    if (items.length > 0) {
      clusterDataArray.push({ code, items });
    }
  });

  
  clusterDataArray.sort((a, b) => b.items.length - a.items.length);
  
  const newMemo = {
    id: timestamp,
    title: 'New Cluster Analysis',
    type: 'Cluster Analysis Notes', 
    content: '',
    timestamp: Date.now(),
    clusterData: clusterDataArray
  };
  
  memoList.value.unshift(newMemo);
  
  
  
  fetch('http://localhost:5002/api/memos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(memoList.value)
  }).catch(e => console.error(e));
  
  showCollectCode.value = false; 
};

const handleReclassify = () => {
  const newSoc = newSecondOrderCodeInput.value.trim();
  if (!newSoc || selectedUmapPoints.value.length === 0) return;
  
  const selectedCodes = selectedUmapPoints.value.map(pt => pt.name);
  
  Object.values(passageDatabase).forEach(p => {
    p.firstOrderCodes.forEach((foc, idx) => {
      if (selectedCodes.includes(foc)) {
        p.secondOrderCodes[idx] = newSoc;
      }
    });
  });
  
  const newColor = colorLibrary[newSoc] || '#fbc02d';
  const currentMap = { ...umapColorMap.value };
  selectedCodes.forEach(c => { currentMap[c] = newColor; });
  umapColorMap.value = currentMap;
  
  newSecondOrderCodeInput.value = '';
  umapSecondCodeDropdownOpen.value = false;
  umapSecondCodeTextEdit.value = false;
  toggleUmapBrush();
  
  renderUmapChart();
  nextTick(drawAllPassageCharts); 
};
const attrs = useAttrs();
const processedDataRef = ref([]);
const pockets = ref([]);
const thumbnails = ref([]);
let pocketKeywords = reactive({});
let currentTransform = d3.zoomIdentity.scale(6);
let attractcondition = false;
let globalPocketName = null;
let globalSimilarities = null;
const deletedKeywords = ref([]);
const point = usePoint();
const showDeletedKeywordsAlert = ref(false);
const isSending = ref(false);
const showLoading = ref(false);
let mincnt = 1;
let maxcnt = 1;
let currentSimulation = null; 
let bubbleClickHandler = null; 
let styleInjected = false; 
let topcodescount = ref(6)


const showApplyAllModal = ref(false);
const processingMode = ref('extract');
const selectedPassages = ref({});
const processing = ref(false);
const processedCount = ref(0);
const totalFiles = ref(0);
const currentFile = ref('');
const currentChunk = ref(0);
const totalChunks = ref(0);
const csvFileInput = ref(null);
const arePocketsVisible = ref(true); 
const sortstate = ref(true); 
const showMemoPanel = ref(false); 
const isMemoFullScreen = ref(false); 
const memoList = ref([]); 


import { provide } from 'vue';
provide('passageDatabase', passageDatabase);


import { inject } from 'vue';
const showCollectCode = inject('showCollectCode', ref(false));

const toggleCollectMemo = () => {
  showCollectCode.value = !showCollectCode.value;
};


const fetchMemos = async () => {
  try {
    const res = await fetch('http://localhost:5002/api/memos');
    if (res.ok) {
      memoList.value = await res.json();
    }
  } catch (e) {
    console.error('Failed to fetch memos:', e);
  }
};

const handleSaveMemos = async () => {
  try {
    await fetch('http://localhost:5002/api/memos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(memoList.value)
    });
  } catch (e) {
    console.error('Failed to save memos:', e);
  }
};

const handleAddMemo = (type) => {
  const newMemo = {
    id: Date.now().toString(),
    title: 'New Memo',
    type,
    content: '',
    timestamp: Date.now()
  };
  memoList.value.unshift(newMemo);
  handleSaveMemos();
};


const createMemoWithTitle = (type, title) => {
  const newMemo = {
    id: Date.now().toString(),
    title: title,
    type,
    content: '',
    timestamp: Date.now()
  };
  memoList.value.unshift(newMemo);
  handleSaveMemos();
  
  showCollectCode.value = false;
};

const handleDeleteMemo = (id) => {
  memoList.value = memoList.value.filter(m => m.id !== id);
  handleSaveMemos();
};

const handleSortMemos = () => {
  const typeOrder = {
    'First-Order Code Notes': 1,
    'Second-Order Code Notes': 2,
    'Theoretical Memos': 3,
    'Analytical Memos': 4
  };
  memoList.value.sort((a, b) => {
    if (typeOrder[a.type] !== typeOrder[b.type]) {
      return typeOrder[a.type] - typeOrder[b.type];
    }
    return b.timestamp - a.timestamp;
  });
  handleSaveMemos();
};


onMounted(() => {
  fetchMemos();
  
  document.addEventListener('click', closeContextMenu);
});


const contextMenuVisible = ref(false);
const contextMenuPosition = reactive({ x: 0, y: 0 });
const pendingMemoType = ref('');
const pendingMemoTitle = ref('');


const showContextMenu = (event, type, title) => {
  event.preventDefault();
  contextMenuPosition.x = event.clientX;
  contextMenuPosition.y = event.clientY;
  pendingMemoType.value = type;
  pendingMemoTitle.value = title;
  contextMenuVisible.value = true;
};


const closeContextMenu = () => {
  contextMenuVisible.value = false;
};


const confirmCreateMemo = () => {
  if (pendingMemoType.value && pendingMemoTitle.value) {
    createMemoWithTitle(pendingMemoType.value, pendingMemoTitle.value);
  }
  closeContextMenu();
};



const threshold = ref(1); 
const minThreshold = ref(1); 
const maxThreshold = ref(1); 
let pathLibrary = reactive({});
let combinedSubLinksMap = new Map(); 
const expandedLinkKey = ref(null); 

const combinedThreshold = ref(1);
const combinedMinThreshold = ref(1);
const combinedMaxThreshold = ref(1);
const combinedIncludeUnclassified = ref(true)
let topn = ref(6);


const tooltipVisible = ref(false)
const tooltipContent = ref('')
const tooltipPosition = reactive({ x: 0, y: 0 })


const showCodeTooltip = (event, codeName) => {
  tooltipContent.value = codeExplanations[codeName] || 'No explanation available'
  tooltipPosition.x = event.clientX + 15
  tooltipPosition.y = event.clientY + 15
  tooltipVisible.value = true
}

const hideCodeTooltip = () => {
  tooltipVisible.value = false
}

let dragStartX = 0;
let dragStartY = 0;
let originalX = 0;
let originalY = 0;

const startDrag = (e) => {
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  originalX = selectedNodeInfo.value.x;
  originalY = selectedNodeInfo.value.y;
  
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
};

const handleDrag = (e) => {
  const dx = e.clientX - dragStartX;
  const dy = e.clientY - dragStartY;
  selectedNodeInfo.value.x = originalX + dx;
  selectedNodeInfo.value.y = originalY + dy;
};

const stopDrag = () => {
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
};


const useCustomInput = ref(false)
const customSecondOrderCodes = ref(['']) 


const originalState = ref(null); 
const isCombined = ref(false); 


const isUndoing = ref(false);


const showDeleteModal = ref(false);
const deleteTarget = ref({ pocketName: '', passageName: '' });
const deleteScope = ref('single'); 


const secondViewRef = inject('secondViewRef');

const combinedNodeMap = ref({}); 
const combinedPathMap = ref({}); 


import { defineEmits } from 'vue';
import { _100 } from '#tailwind-config/theme/backdropBrightness';

const emit = defineEmits(['select-passage']); 


const selectAndJump = (passageName, code) => {
  console.log('MainView: Selecting passage and code:', passageName, code); 
  emit('select-passage', { passageName, code });
};


const toggleCustomInput = () => {
  if (!useCustomInput.value) {
    customSecondOrderCodes.value = [''] 
  }
}


const addCodeInput = () => {
  customSecondOrderCodes.value.push('')
}

const removeCodeInput = (index) => {
  if (customSecondOrderCodes.value.length > 1) {
    customSecondOrderCodes.value.splice(index, 1)
  }
}

const useLLMProcessing = ref(false); 

const handleStartProcessing = () => {
  if (useLLMProcessing.value) {
    startProcessing_llm();
  } else {
    startProcessing();
  }
};


const toggleMemoPanel = () => {
  showCollectCode.value = false;  
};



const showUmapOverlay = async (payload) => {
  const { secondCodeName, firstOrderCodes } = payload;
  umapTitle.value = secondCodeName;
  umapActive.value = true;
  umapLoading.value = true;

  
  const socColor = colorLibrary[secondCodeName] || '#4caf50';
  const newColorMap = {};
  firstOrderCodes.forEach(foc => { newColorMap[foc] = socColor; });
  umapColorMap.value = newColorMap;

  try {
    const res = await fetch('http://localhost:5003/api/umap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codes: firstOrderCodes })
    });
    const data = await res.json();
    if (data.error) {
      alert('UMAP error: ' + data.error);
      umapActive.value = false;
      return;
    }
    umapPoints.value = data.points;
    umapLoading.value = false;

    
    await nextTick();
    renderUmapChart();
  } catch (e) {
    console.error('UMAP request failed:', e);
    alert('UMAP request failed');
    umapActive.value = false;
    umapLoading.value = false;
  }
};

const renderUmapChart = () => {
  const container = document.getElementById('umap-chart-container');
  if (!container) return;

  
  d3.select(container).selectAll('*').remove();

  const margin = { top: 40, right: 40, bottom: 50, left: 50 };
  const w = container.clientWidth || 600;
  const h = container.clientHeight || 500;
  const innerW = w - margin.left - margin.right;
  const innerH = h - margin.top - margin.bottom;

  const svg = d3.select(container)
    .append('svg')
    .attr('width', w)
    .attr('height', h);

  
  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);
    
  
  const zoomG = g.append('g');

  const pts = umapPoints.value;

  
  const xExtent = d3.extent(pts, d => d.x);
  const yExtent = d3.extent(pts, d => d.y);
  const xPad = (xExtent[1] - xExtent[0]) * 0.08 || 0.1;
  const yPad = (yExtent[1] - yExtent[0]) * 0.08 || 0.1;

  const xScale = d3.scaleLinear()
    .domain([xExtent[0] - xPad, xExtent[1] + xPad])
    .range([0, innerW]);

  const yScale = d3.scaleLinear()
    .domain([yExtent[0] - yPad, yExtent[1] + yPad])
    .range([innerH, 0]);

  
  const codeFrequencies = {};
  Object.values(passageDatabase).forEach(p => {
    p.firstOrderCodes.forEach(code => {
      codeFrequencies[code] = (codeFrequencies[code] || 0) + 1;
    });
  });

  const allFrequencies = Object.values(codeFrequencies);
  const minFreq = d3.min(allFrequencies) || 1;
  const maxFreq = d3.max(allFrequencies) || 1;

  
  const radiusScale = d3.scaleSqrt()
    .domain([minFreq, maxFreq])
    .range([4, 15]);

  
  const zoom = d3.zoom()
    .scaleExtent([0.1, 10])
    .on('zoom', (event) => {
      zoomG.attr('transform', event.transform);
    });

  
  let lassoPath = [];
  const lassoLine = d3.line().x(d => d[0]).y(d => d[1]).curve(d3.curveLinearClosed);
  const lassoG = svg.append('g').attr('class', 'lasso-group');
  const lassoPathNode = lassoG.append('path')
    .attr('fill', 'rgba(255, 235, 59, 0.2)')
    .attr('stroke', '#fbc02d')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '3,3')
    .style('pointer-events', 'none')
    .style('display', 'none');

  const drag = d3.drag()
    .on('start', (event) => {
      if (!umapBrushActive.value) return;
      lassoPath = [[event.x, event.y]];
      lassoPathNode.attr('d', lassoLine(lassoPath)).style('display', 'block');
    })
    .on('drag', (event) => {
      if (!umapBrushActive.value) return;
      lassoPath.push([event.x, event.y]);
      lassoPathNode.attr('d', lassoLine(lassoPath));
    })
    .on('end', (event) => {
      if (!umapBrushActive.value) return;
      if (lassoPath.length < 3) {
        lassoPathNode.style('display', 'none');
        return;
      }
      
      const start = lassoPath[0];
      const end = lassoPath[lassoPath.length - 1];
      const dist = Math.sqrt(Math.pow(end[0] - start[0], 2) + Math.pow(end[1] - start[1], 2));
      
      if (dist > 50) { 
        lassoPathNode.style('display', 'none');
        lassoPath = [];
        return;
      }

      const selected = [];
      const currentTransform = d3.zoomTransform(svg.node());
      
      zoomG.selectAll('circle').each(function(d) {
        const px = currentTransform.applyX(xScale(d.x)) + margin.left;
        const py = currentTransform.applyY(yScale(d.y)) + margin.top;
        if (d3.polygonContains(lassoPath, [px, py])) {
          selected.push(d);
          d3.select(this)
            .attr('stroke', '#ffe100')
            .attr('stroke-width', 4);
        } else {
          d3.select(this)
            .attr('stroke', d3.select(this).attr('data-default-stroke'))
            .attr('stroke-width', 1.5);
        }
      });

      if (selected.length > 0) {
        selectedUmapPoints.value = selected;
        showUmapSelectionPanel.value = true;
        umapSecondCodeDropdownOpen.value = false;
        umapSecondCodeTextEdit.value = false;
      } else {
        selectedUmapPoints.value = [];
        showUmapSelectionPanel.value = false;
        umapSecondCodeDropdownOpen.value = false;
        umapSecondCodeTextEdit.value = false;
        lassoPathNode.style('display', 'none');
      }
    });

  currentUmapSvg = svg;
  currentUmapZoom = zoom;
  currentUmapDrag = drag;

  if (umapBrushActive.value) {
    svg.call(drag);
  } else {
    svg.call(zoom).on('dblclick.zoom', null); 
  }

  
  zoomG.append('g')
    .attr('class', 'umap-grid')
    .selectAll('line.h')
    .data(yScale.ticks(6))
    .enter().append('line')
    .attr('x1', 0).attr('x2', innerW)
    .attr('y1', d => yScale(d)).attr('y2', d => yScale(d))
    .attr('stroke', '#e8e8e8').attr('stroke-dasharray', '3,3');

  zoomG.append('g')
    .attr('class', 'umap-grid')
    .selectAll('line.v')
    .data(xScale.ticks(6))
    .enter().append('line')
    .attr('y1', 0).attr('y2', innerH)
    .attr('x1', d => xScale(d)).attr('x2', d => xScale(d))
    .attr('stroke', '#e8e8e8').attr('stroke-dasharray', '3,3');

  
  const tooltip = d3.select(container)
    .append('div')
    .attr('class', 'umap-tooltip')
    .style('opacity', 0);

  
  const cMap = umapColorMap.value;
  const defaultColor = colorLibrary[umapTitle.value] || '#4caf50';
  const getPointColor = (d) => cMap[d.name] || defaultColor;

  
  zoomG.selectAll('circle')
    .data(pts)
    .enter()
    .append('circle')
    .attr('cx', d => xScale(d.x))
    .attr('cy', d => yScale(d.y))
    .attr('r', d => radiusScale(codeFrequencies[d.name] || 1))
    .attr('fill', d => getPointColor(d))
    .attr('stroke', d => d3.color(getPointColor(d)).darker(0.6))
    .attr('data-default-stroke', d => d3.color(getPointColor(d)).darker(0.6))
    .attr('stroke-width', 1.5)
    .attr('opacity', 0.85)
    .style('cursor', 'pointer')
    .style('transition', 'opacity 0.2s')
    .on('mouseover', function (event, d) {
      d3.select(this)
        .attr('opacity', 1)
        .attr('fill', d3.color(getPointColor(d)).brighter(0.4));

      const [px, py] = d3.pointer(event, container);
      const isRightSide = px > w / 2;

      tooltip
        .html(`<strong>${d.name}</strong><br/>Frequency: ${codeFrequencies[d.name] || 0}`)
        .style('left', isRightSide ? (px - 14) + 'px' : (px + 14) + 'px')
        .style('top', (py - 10) + 'px')
        .style('transform', isRightSide ? 'translateX(-100%)' : 'none')
        .transition().duration(150)
        .style('opacity', 1);
    })
    .on('mouseout', function (event, d) {
      d3.select(this)
        .attr('opacity', 0.85)
        .attr('fill', getPointColor(d));

      tooltip.transition().duration(150).style('opacity', 0);
    })
    .on('click', function (event, d) {
      const code = d.name;
      let targetPassage = null;
      for (const [passageName, p] of Object.entries(passageDatabase)) {
        const idx = p.firstOrderCodes.findIndex(foc => foc === code);
        if (idx !== -1) {
          targetPassage = passageName;
          break;
        }
      }
      if (targetPassage) {
        emit('select-passage', { passageName: targetPassage, code });
      }
    })
    .on('contextmenu', function (event, d) {
      event.preventDefault();
      showContextMenu(event, 'First-Order Code Notes', d.name);
    });
};

const exitUmapOverlay = () => {
  umapActive.value = false;
  umapTitle.value = '';
  umapPoints.value = [];
  umapColorMap.value = {};
  
  nextTick(drawAllPassageCharts);
};


const drawMultiUmap = async () => {
  const selectedSocs = Object.entries(umapCodeSelection)
    .filter(([, checked]) => checked)
    .map(([code]) => code);

  if (selectedSocs.length === 0) {
    alert('Please select at least one Second-Order Code');
    return;
  }

  
  const allCodes = [];
  const codeToSoc = {};
  for (const soc of selectedSocs) {
    const socLower = soc.toLowerCase();
    Object.values(passageDatabase).forEach(p => {
      p.firstOrderCodes.forEach((foc, idx) => {
        let currentSoc = (p.secondOrderCodes[idx] || '').toLowerCase().trim();
        if (!currentSoc) currentSoc = 'unclassified';
        if (currentSoc === socLower && !codeToSoc[foc]) {
          allCodes.push(foc);
          codeToSoc[foc] = soc;
        }
      });
    });
  }

  if (allCodes.length === 0) {
    alert('No first-order codes found for selected codes');
    return;
  }

  
  const newColorMap = {};
  allCodes.forEach(foc => {
    const soc = codeToSoc[foc];
    newColorMap[foc] = colorLibrary[soc] || '#4caf50';
  });
  umapColorMap.value = newColorMap;

  umapTitle.value = selectedSocs.join(' + ');
  umapActive.value = true;
  umapLoading.value = true;

  try {
    const res = await fetch('http://localhost:5003/api/umap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codes: allCodes })
    });
    const data = await res.json();
    if (data.error) {
      alert('UMAP error: ' + data.error);
      umapActive.value = false;
      return;
    }
    umapPoints.value = data.points;
    umapLoading.value = false;
    await nextTick();
    renderUmapChart();
  } catch (e) {
    console.error('UMAP request failed:', e);
    alert('UMAP request failed');
    umapActive.value = false;
    umapLoading.value = false;
  }
};

defineExpose({
  passageDatabase,
  memoList,
  handleAddMemo,
  handleDeleteMemo,
  handleSortMemos,
  handleSaveMemos,
  createMemoWithTitle,
  showUmapOverlay,
  fetchMemos,
  stageOrder,
  addMemoLinkToFinal,
});




const uploadCsv = () => {
  if (!csvFileInput.value) {
    csvFileInput.value = document.createElement('input');
    csvFileInput.value.type = 'file';
    csvFileInput.value.accept = '.csv';
    csvFileInput.value.style.display = 'none';
    document.body.appendChild(csvFileInput.value);
    csvFileInput.value.addEventListener('change', handleCsvUpload);
  }
  csvFileInput.value.click();
};

const handleCsvUpload = async (event) => {
  const file = event.target.files[0];
  if (!file || !file.name.endsWith('.csv')) {
    alert('Please select a valid CSV file');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('csv_file', file);
    const uploadResponse = await fetch('http://localhost:8000/upload-csv', {
      method: 'POST',
      body: formData
    });
    const uploadData = await uploadResponse.json();
    if (!uploadResponse.ok) throw new Error(uploadData.error || 'Upload failed');

    const text = await file.text();
    const parsedData = d3.csvParse(text);
    
    if (!validateCsvFormat(parsedData)) {
      alert('Invalid CSV format. Supported formats:\n' +
            '1. Original: code, count, passage, explanation, sentence, stage\n' +
            '2. New: FirstOrderCode, SecondOrderCode, Passage, Stage');
      return;
    }

    Object.keys(passageDatabase).forEach(key => delete passageDatabase[key]);
    initDatabase(parsedData);
    updateStageOrder();
    
    isEditing.value = false;
    currentPassage.value = '';
    alert('CSV uploaded successfully!');
  } catch (error) {
    console.error('Error uploading CSV:', error);
    alert('Failed to upload CSV: ' + error.message);
  } finally {
    event.target.value = '';
  }
};


const validateCsvFormat = (data) => {
  if (data.length === 0) return false;
  
  
  const originalColumns = ['code', 'count', 'passage', 'explanation', 'sentence', 'stage'];
  
  const newColumns = ['FirstOrderCode', 'SecondOrderCode', 'Passage', 'Stage'];
  
  
  const isOriginal = originalColumns.every(col => data.columns.includes(col));
  const isNew = newColumns.every(col => data.columns.includes(col));
  
  return isOriginal || isNew;
};


const initDatabase = (csvData) => {
  
  const isOriginalFormat = csvData.columns.includes('code');
  
  
  const stageCounts = {};
  const totalRows = csvData.length;
  
  
  csvData.forEach(row => {
    const stage = (isOriginalFormat ? row.stage : row.Stage || 'Unknown').trim();
    stageCounts[stage] = (stageCounts[stage] || 0) + 1;
  });
  
  
  const validStages = new Set();
  Object.entries(stageCounts).forEach(([stage, count]) => {
    const percentage = (count / totalRows) * 100;
    if (percentage >= 5) {  
      validStages.add(stage);
    } else {
      console.warn(`Removing low-percentage stage: ${stage} (${percentage.toFixed(2)}%)`);
    }
  });
  
  
  csvData.forEach(row => {
    const passageName = isOriginalFormat ? row.passage : row.Passage;
    const code = isOriginalFormat ? row.code : row.FirstOrderCode;
    const secondCode = (isOriginalFormat ? null : row.SecondOrderCode) || null;
    let explanation = isOriginalFormat ? row.explanation : row.Explanation || '';
    let sentence = isOriginalFormat ? row.sentence : row.Sentence || '';
    const stage = (isOriginalFormat ? row.stage : row.Stage || 'Unknown').trim();
    
    
    if (explanation) explanation = explanation.replace(/\?\?/g, "'");
    if (sentence) sentence = sentence.replace(/\?\?/g, "'");
    
    
    if (!validStages.has(stage)) {
      return;
    }
    
    if (!passageDatabase[passageName]) {
      passageDatabase[passageName] = reactive({
        firstOrderCodes: [],
        secondOrderCodes: [],
        explanations: [],
        sentences: [],
        stages: []
      });
    }
    
    const passage = passageDatabase[passageName];
    if (!passage.firstOrderCodes.includes(code)) {
      passage.firstOrderCodes.push(code);
      passage.secondOrderCodes.push(secondCode);
      passage.explanations.push(explanation);
      passage.sentences.push(sentence);
      passage.stages.push(stage);
    }
  });
  
  
  console.log('Valid stages after filtering:', Array.from(validStages));
};





let currentCsvFilename = null;

onMounted(async () => {
  const intervalId = setInterval(checkForNewCsv, 3000);  
  checkForNewCsv();  
  updateStageOrder();
  updateConfView();
});

const checkForNewCsv = async () => {
  try {
    const res = await fetch('http://localhost:8000/latest-csv', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch latest CSV: ${res.statusText}`);
    }
    const data = await res.json();
    const newFilename = data.filename;

    
    if (!newFilename || newFilename === currentCsvFilename) {
      return;
    }

    
    console.log(`New CSV detected: ${newFilename}, updating passageDatabase...`);
    const csvResponse = await fetch(`http://localhost:8000/public/${newFilename}`);
    if (!csvResponse.ok) {
      throw new Error(`Failed to fetch CSV: ${csvResponse.statusText}`);
    }
    const csvText = await csvResponse.text();
    const parsedData = d3.csvParse(csvText);

    
    initDatabase(parsedData);
    updateStageOrder();
    
    
    currentCsvFilename = newFilename;
  } catch (error) {
    
  }
};


const updateStageOrder = () => {
  const currentStages = new Set();
  Object.values(passageDatabase).forEach(passage => {
    passage.stages.forEach(stage => currentStages.add(stage));
  });

  
  const newStageOrder = [
    ...stageOrder.value.filter(stage => currentStages.has(stage)),
    ...Array.from(currentStages).filter(stage => !stageOrder.value.includes(stage))
  ];

  
  if (
    newStageOrder.length !== stageOrder.value.length ||
    newStageOrder.some((stage, index) => stage !== stageOrder.value[index])
  ) {
    stageOrder.value = newStageOrder;
  }
};



watch(
  () => passageDatabase,
  () => updateStageOrder(),
  { deep: true }
);


const toggleStageModal = () => {
  showStageModal.value = !showStageModal.value;
};


const dragStart = (event, index) => {
  event.dataTransfer.setData('text/plain', index);
};

const drop = (event, index) => {
  event.preventDefault();
  const fromIndex = parseInt(event.dataTransfer.getData('text/plain'));
  const toIndex = index;
  
  if (fromIndex !== toIndex) {
    const newOrder = [...stageOrder.value];
    const [movedItem] = newOrder.splice(fromIndex, 1);
    newOrder.splice(toIndex, 0, movedItem);
    stageOrder.value = newOrder;
  }
};


const width = 8000;
const height = 8000;
const color = d3.scaleOrdinal(d3.schemeCategory10);
let fontSizeScale = null;


const props = defineProps({
  releaseIndex: { type: Number, default: null },
  releaseCount: { type: Number, default: 0 }
});



const selectedCode = ref('');
const selectedExplanation = ref('');
const showExplanationModal = ref(false);

const codeExplanations = reactive({}); 
const includeExplanation = ref(false); 
const isStrictMode = ref(false); 

const updateExplanation = (code, explanation) => {
  if (code) codeExplanations[code] = explanation;
};









const existingSecondCodes = computed(() => {
  const codeMap = new Map();
  const totalPassages = Object.keys(passageDatabase).length;
  
  
  Object.values(passageDatabase).forEach(passage => {
    const uniqueCodes = new Set(passage.secondOrderCodes.filter(Boolean));
    uniqueCodes.forEach(code => {
      codeMap.set(code, (codeMap.get(code) || 0) + 1);
    });
  });

  return Array.from(codeMap.entries()).map(([code, count]) => {
    const ratio = count / totalPassages;
    const percentage = Math.round(ratio * 100);
    
    let backgroundStyle;
    if (ratio === 1) {
      backgroundStyle = '#A0BF7C'; 
    } else {
      backgroundStyle = `linear-gradient(
        to right,
        #A0BF7C 0%,
        #A0BF7C ${percentage}%,
        #ffffff ${percentage}%,
        #ffffff 100%
      )`;
    }

    return {
      name: code,
      count,
      total: totalPassages,
      ratio,
      backgroundStyle
    };
  });
});

const selectedExistingCodes = ref({});
const isAllExistingSelected = ref(false);

const customInputs = ref([{ code: '', explanation: '' }]);



const addCustomInput = () => {
  customInputs.value.push({ code: '', explanation: '' });
};


const toggleSelectAllExisting = () => {
  isAllExistingSelected.value = !isAllExistingSelected.value;
  existingSecondCodes.value.forEach(code => {
    selectedExistingCodes.value[code.name] = isAllExistingSelected.value;
  });
};


const removeCustomInput = (index) => {
  if (customInputs.value.length > 1) {
    customInputs.value.splice(index, 1);
  }
};

const startProcessing_llm = async () => {
  
  if (
    Object.values(selectedExistingCodes.value).every(selected => !selected) &&
    customInputs.value.every(input => !input.code.trim())
  ) {
    alert('Please select at least one code or enter a valid code');
    return;
  }

  
  const existingCodeDetails = existingSecondCodes.value
    .filter(code => selectedExistingCodes.value[code.name])
    .map(code => ({
      code: code.name,
      explanation: codeExplanations[code.name] || '',
      examples: getFirstOrderExamples(code.name) 
    }));

  
  const customCodes = customInputs.value
    .filter(input => input.code.trim())
    .map(input => ({
      code: input.code.trim(),
      explanation: input.explanation.trim(),
      isCustom: true 
    }));

  
  const allTargets = [...existingCodeDetails, ...customCodes];

  console.log(allTargets);

  
  processing.value = true;
  totalFiles.value = Object.keys(passageDatabase).length;
  processedCount.value = 0;

  
  for (const [passageName, passage] of Object.entries(passageDatabase)) {
    currentFile.value = passageName;

    
    const processCodes = processingMode.value === 'extract' 
      ? passage.firstOrderCodes 
      : passage.firstOrderCodes.filter((_, idx) => !passage.secondOrderCodes[idx]);

    const processStages = processingMode.value === 'extract'
      ? passage.stages
      : passage.stages.filter((_, idx) => !passage.secondOrderCodes[idx]);

    
    const chunkSize = 10;
    totalChunks.value = Math.ceil(processCodes.length / chunkSize);

    for (let i = 0; i < processCodes.length; i += chunkSize) {
      currentChunk.value = i / chunkSize + 1;
      const codeChunk = processCodes.slice(i, i + chunkSize);
      const stageChunk = processStages.slice(i, i + chunkSize);

      
      const textsWithContext = codeChunk.map((code, idx) => ({
        text: code,
        stage: stageChunk[idx] || 'unknown',
        fullText: passage.sentences[idx] || '' 
      }));

      try {
        
        const response = await fetch('http://localhost:5001/api/llm-process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            targets: allTargets,
            texts: textsWithContext,
            options: {
              includeExplanation: includeExplanation.value,
              strictMode: isStrictMode.value
            }
          })
        });

        
        const data = await response.json();
        codeChunk.forEach((originalCode, idx) => {
          const codeIndex = passage.firstOrderCodes.indexOf(originalCode);
          if (codeIndex === -1) return;

          
          const newSecondCode = data.results[idx];
          
          
          passage.secondOrderCodes[codeIndex] = newSecondCode !== 'null' 
            ? newSecondCode 
            : null;
        });
      } catch (error) {
        console.error('Processing failed:', error);
      }
    }
    processedCount.value++;
  }

  
  processing.value = false;
  showApplyAllModal.value = false;
  updateConfView();

  
  customInputs.value = [{ code: '', explanation: '' }];
};

const startProcessing = async () => {
  
  if (
    Object.values(selectedExistingCodes.value).every(selected => !selected) &&
    customInputs.value.every(input => !input.code.trim())
  ) {
    alert('Please select at least one code or enter a valid code');
    return;
  }

  
  Object.entries(selectedExistingCodes.value)
    .filter(([_, selected]) => selected)
    .forEach(([code]) => {
      updateExplanation(code, codeExplanations[code] || '');
    });

  
  customInputs.value
    .filter(input => input.code.trim())
    .forEach(input => {
      updateExplanation(input.code.trim(), input.explanation.trim());
    });

  
  processing.value = true;
  totalFiles.value = Object.keys(passageDatabase).length;
  processedCount.value = 0;

  
  const customCodes = customInputs.value
    .filter(input => input.code.trim())
    .map(input => ({
      code: input.code.trim(),
      explanation: input.explanation.trim()
    }));

  
  const existingCodes = Object.entries(selectedExistingCodes.value)
    .filter(([_, selected]) => selected)
    .map(([code]) => ({
      code,
      explanation: codeExplanations[code] || ''
    }));

  
  const selectedCodes = [
    ...existingCodes,
    ...customCodes
  ].filter(item => item.code); 

  
  const processingTexts = selectedCodes.map(item =>
    includeExplanation.value
      ? `${item.code},${item.explanation}`
      : item.code
  );

  
  selectedCodes.forEach(item => {
    codeExplanations[item.code] = item.explanation;
  });

  
  for (const [passageName, passage] of Object.entries(passageDatabase)) {
    currentFile.value = passageName;

    
    const processCodes = processingMode.value === 'extract'
      ? passage.firstOrderCodes 
      : passage.firstOrderCodes.filter((_, idx) => !passage.secondOrderCodes[idx]); 

    const processStages = processingMode.value === 'extract'
    ? passage.stages
    : passage.stages.filter((_, idx) => !passage.secondOrderCodes[idx])

    
    const chunkSize = 10;
    totalChunks.value = Math.ceil(processCodes.length / chunkSize);

    for (let i = 0; i < processCodes.length; i += chunkSize) {
      currentChunk.value = i / chunkSize + 1;
      const codeChunk = processCodes.slice(i, i + chunkSize);
      const stageChunk = processStages.slice(i, i + chunkSize) 

      const textsWithStage = codeChunk.map((code, idx) => {
        const stage = stageChunk[idx] || 'unknown' 
        return `${code},${stage}`
      })

      try {
        
        const response = await fetch('http://localhost:5004/api/batch-process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            targets: processingTexts, 
            texts: textsWithStage
          })
        });

        
        const data = await response.json();
        codeChunk.forEach((text, idx) => {
          const originalCode = text.split(',')[0]  
          const codeIndex = passage.firstOrderCodes.indexOf(originalCode)
          if (codeIndex === -1) return;

          
          const similarities = data.results[idx];

          
          const maxEntry = Object.entries(similarities)
            .filter(([_, sim]) => sim > 0.30) 
            .sort((a, b) => b[1] - a[1])[0]; 

          
          if (maxEntry) {
            
            const [key] = maxEntry[0].split(','); 
            passage.secondOrderCodes[codeIndex] = key;
          } 
        });
      } catch (error) {
        console.error('Processing failed:', error);
      }
    }

    
    processedCount.value++;
  }

  
  processing.value = false;
  showApplyAllModal.value = false;
  updateConfView(); 

  
  customInputs.value = [{ code: '', explanation: '' }]; 
};



const getFirstOrderExamples = (secondCode) => {
  const examples = [];
  
  
  Object.values(passageDatabase).forEach(passage => {
    passage.secondOrderCodes.forEach((code, idx) => {
      if (code === secondCode && examples.length < 3) {
        examples.push(passage.firstOrderCodes[idx]);
      }
    });
  });

  return examples;
};


const getFirstOrderCodesForSecondCode = (objectpassage, secondCode) => {
  const firstOrderCodes = [];
  Object.values(passageDatabase).forEach(passage => {
    passage.firstOrderCodes.forEach((code, index) => {
      if (objectpassage === passage && passage.secondOrderCodes[index] === secondCode) {
        firstOrderCodes.push(code);
      }
    });
  });
  return firstOrderCodes.join(', ');
};

watch(showApplyAllModal, (val) => {
  if (val) {
    selectedPassages.value = Object.fromEntries(
      Object.keys(passageDatabase).map(passageName => [
        passageName,
        {
          allSelected: false,
          codes: Object.fromEntries(
            uniqueSecondCodes(passageDatabase[passageName]).map(code => [code, false])
          )
        }
      ])
    );
  }
});





const getSecondOrderCode = (code, stage) => {
  let secondCode = null;
  Object.values(passageDatabase).some(passage => {
    const idx = passage.firstOrderCodes.indexOf(code);
    if (idx !== -1 && passage.stages[idx] === stage) {
      secondCode = passage.secondOrderCodes[idx] || 'unclassified';
      return true;
    }
    return false;
  });
  return (!includeUnclassified.value && secondCode === 'unclassified') ? null : secondCode;
};

const generateRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};



const predefinedColors = [
  '#a6cee3',
  '#1f78b4',
  '#b2df8a',
  '#33a02c',
  '#fb9a99',
  '#e31a1c',
  '#fdbf6f',
  '#ff7f00',
  '#cab2d6'
];






















const fixedCategoryColors = {
  'Personal experiences': '#33a02c',
  'Resource Accumulation': '#1f78b4',
  'Cognitive Process': '#a6cee3',
  'Early Contextual Triggers': '#fb9a99',
  'Entrepreneurial Insight & Action': '#b2df8a',
  'content influence': '#1f78b4',
  'trust erosion': '#b2df8a',
  'develop of discerning strategies': '#a6cee3',
  'over commercialization': '#33a02c',
  'growing scepticism': '#e31a1c',
  'decreased engagement': '#fb9a99',
  'Unclassified': '#CCCCCC',
  'trust crisis': '#fdbf6f'
   
};


const colorLibrary = reactive({});

const allUniqueCodeNames = computed(() => {
  const codes = existingSecondCodes.value.map(item => item.name);
  if (!codes.includes('Unclassified')) {
    codes.push('Unclassified');
  }
  return codes;
});

watch(allUniqueCodeNames, (newCodeNames) => {
  let usedPredefinedColors = 0;
  
  Object.values(colorLibrary).forEach(color => {
    if (predefinedColors.includes(color)) {
      usedPredefinedColors++;
    }
  });

  newCodeNames.forEach(code => {
    if (!colorLibrary[code]) {
      if (usedPredefinedColors < predefinedColors.length) {
        colorLibrary[code] = predefinedColors[usedPredefinedColors];
        usedPredefinedColors++;
      } else {
        colorLibrary[code] = generateRandomColor();
      }
    }
  });
}, {
  immediate: true 
});











const buildCombinedData = () => {
  combinedNodeMap.value = {};
  combinedPathMap.value = {};

  if (!isCombined.value) return;

  
  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    passage.firstOrderCodes.forEach((code, idx) => {
      const stage = passage.stages[idx];
      const secondCode = passage.secondOrderCodes[idx] || 'unclassified';
      if (!combinedIncludeUnclassified.value && !passage.secondOrderCodes[idx]) return;

      const key = `${secondCode}#${stage}`;
      if (!combinedNodeMap.value[key]) {
        combinedNodeMap.value[key] = {
          topCodes: [], 
          others: [],   
          counts: new Map() 
        };
      }

      const nodeData = combinedNodeMap.value[key];
      const count = passage.count?.[idx] || 1; 
      nodeData.counts.set(code, (nodeData.counts.get(code) || 0) + count);
    });
  });

  
  Object.keys(combinedNodeMap.value).forEach(key => {
    const nodeData = combinedNodeMap.value[key];
    const codeCounts = Array.from(nodeData.counts.entries())
      .sort((a, b) => b[1] - a[1]); 
    nodeData.topCodes = codeCounts.slice(0, topn.value).map(([code]) => code); 
    nodeData.others = codeCounts.slice(topn.value).map(([code]) => code); 
  });

  
  Object.entries(pathLibrary).forEach(([pathKey, value]) => {
    const [sourceId, targetId] = pathKey.split('|');
    const [sourceCode, sourceStage] = sourceId.split('#');
    const [targetCode, targetStage] = targetId.split('#');

    const sourceSecondCode = getSecondOrderCode(sourceCode, sourceStage);
    const targetSecondCode = getSecondOrderCode(targetCode, targetStage);

    if (!sourceSecondCode || !targetSecondCode) return;

    const sourceKey = `${sourceSecondCode}#${sourceStage}`;
    const targetKey = `${targetSecondCode}#${targetStage}`;

    const sourceNodeData = combinedNodeMap.value[sourceKey];
    const targetNodeData = combinedNodeMap.value[targetKey];

    if (!sourceNodeData || !targetNodeData) return;

    const sourceNode = sourceNodeData.topCodes.includes(sourceCode) ? sourceCode : 'others';
    const targetNode = targetNodeData.topCodes.includes(targetCode) ? targetCode : 'others';

    const newPathKey = `${sourceSecondCode}#${sourceNode}#${sourceStage}|${targetSecondCode}#${targetNode}#${targetStage}`;
    combinedPathMap.value[newPathKey] = (combinedPathMap.value[newPathKey] || 0) + value;
  });
};







let fontSizeFactor = ref(1.2)

let stageSpacingFactor = ref(1);


const intraGroupSpacing = 10; 
const interGroupSpacing = 100; 

const buildPathLibrary = () => {
  pathLibrary = {};
  const passagePathTracker = new Map();

  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    const stageMap = {};
    stageOrder.value.forEach(stage => {
      stageMap[stage] = [];
    });

    passage.firstOrderCodes.forEach((code, idx) => {
      const stage = passage.stages[idx];
      
      const codeWithStage = `${code}#${stage}`;
      if (stageMap[stage]) {
        stageMap[stage].push(codeWithStage);
      }
    });

    const paths = stageOrder.value.reduce((acc, stage, index) => {
      if (index === 0) {
        return stageMap[stage].map(code => [code]);
      }
      const newPaths = [];
      acc.forEach(prevPath => {
        stageMap[stage].forEach(code => {
          newPaths.push([...prevPath, code]);
        });
      });
      return newPaths;
    }, []);

    paths.forEach(path => {
      for (let i = 0; i < path.length - 1; i++) {
        
        const binaryPathKey = `${path[i]}|${path[i + 1]}`;
        if (!passagePathTracker.has(binaryPathKey)) {
          passagePathTracker.set(binaryPathKey, new Set());
        }
        passagePathTracker.get(binaryPathKey).add(passageName);
      }
    });
  });

  if (isCombined.value) {
    const combinedPathTracker = new Map();
    const codeToSecondCode = new Map();
    Object.values(passageDatabase).forEach(passage => {
      passage.firstOrderCodes.forEach((code, idx) => {
        const stage = passage.stages[idx];
        const secondCode = passage.secondOrderCodes[idx] || 'unclassified';
        
        codeToSecondCode.set(`${code}#${stage}`, `${secondCode}#${stage}`);
      });
    });

    
    combinedSubLinksMap = new Map();

    passagePathTracker.forEach((passageSet, binaryPathKey) => {
      const [sourceId, targetId] = binaryPathKey.split('|');
      const combinedSource = codeToSecondCode.get(sourceId) || (includeUnclassified.value ? `unclassified#${sourceId.split('#')[1]}` : null);
      const combinedTarget = codeToSecondCode.get(targetId) || (includeUnclassified.value ? `unclassified#${targetId.split('#')[1]}` : null);

      if (combinedSource && combinedTarget && combinedSource !== combinedTarget) {
        const combinedKey = `${combinedSource}|${combinedTarget}`;
        combinedPathTracker.set(combinedKey, (combinedPathTracker.get(combinedKey) || 0) + passageSet.size);

        
        if (!combinedSubLinksMap.has(combinedKey)) {
          combinedSubLinksMap.set(combinedKey, []);
        }
        combinedSubLinksMap.get(combinedKey).push({
          source: sourceId,   
          target: targetId,   
          value: passageSet.size
        });
      }
    });

    combinedPathTracker.forEach((count, binaryPathKey) => {
      pathLibrary[binaryPathKey] = count;
    });

    
    const combinedValues = Object.values(pathLibrary);
    if (combinedValues.length > 0) {
      combinedMinThreshold.value = Math.min(...combinedValues);
      combinedMaxThreshold.value = Math.max(...combinedValues);
    } else {
      combinedMinThreshold.value = 1;
      combinedMaxThreshold.value = 1;
    }
  } else {
    passagePathTracker.forEach((passageSet, binaryPathKey) => {
      if (includeUnclassified.value || !binaryPathKey.includes('unclassified')) {
        pathLibrary[binaryPathKey] = passageSet.size;
      }
    });

    
    
  };

  
  const standardValues = [];
  passagePathTracker.forEach((passageSet, binaryPathKey) => {
    if (includeUnclassified.value || !binaryPathKey.includes('unclassified')) {
      standardValues.push(passageSet.size);
    }
  });

  const baseMin = isCombined.value ? 1 : 2;
  if (standardValues.length > 0) {
    minThreshold.value = Math.max(baseMin, Math.min(...standardValues));
    maxThreshold.value = Math.max(...standardValues);
  } else {
    minThreshold.value = baseMin;
    maxThreshold.value = baseMin;
  }
  
  if (threshold.value < minThreshold.value) {
    threshold.value = minThreshold.value;
  }
  
};

const createSankeyData = () => {
  const nodes = [];
  const links = [];
  const nodeIndex = new Map();
  const colorMap = new Map();
  let colorIdx = 0;

  
  const getColor = (secondCode) => {
  
  if (!secondCode || secondCode === 'unclassified') {
    return "#CCCCCC"; 
  }
  
  return colorLibrary[secondCode] || "#808080"; 
 };


  
  const stageGroups = {};
  stageOrder.value.forEach(stage => {
    stageGroups[stage] = [];
  });

  
  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    passage.firstOrderCodes.forEach((code, i) => {
      const stage = passage.stages[i];
      const secondCode = passage.secondOrderCodes[i] || 'unclassified';

      if (!includeUnclassified.value && !passage.secondOrderCodes[i]) {
        return;
      }

      const nodeKey = isCombined.value ? `${secondCode}#${stage}` : `${code}#${stage}`;
      const nodeLabel = isCombined.value ? secondCode : code;

      if (!stageGroups[stage].some(n => n.key === nodeKey)) {
        const colors = [getColor(secondCode)];
        stageGroups[stage].push({
          key: nodeKey,
          label: nodeLabel,
          stage,
          colors,
          passages: new Set([passageName]),
          secondCodes: new Set([secondCode])
        });
      } else {
        const node = stageGroups[stage].find(n => n.key === nodeKey);
        node.passages.add(passageName);
        node.secondCodes.add(secondCode);
        node.colors = Array.from(node.secondCodes).map(sc => getColor(sc)).sort();
      }
    });
  });

  
  const validLinks = new Map();
  Object.entries(pathLibrary).forEach(([pathKey, value]) => {
    const currentThreshold = isCombined.value ? combinedThreshold.value : threshold.value;
    if (value >= currentThreshold) {
      const [sourceId, targetId] = pathKey.split('|');
      if (sourceId !== targetId) {
        validLinks.set(`${sourceId}|${targetId}`, {
          sourceId,
          targetId,
          value: (validLinks.get(`${sourceId}|${targetId}`)?.value || 0) + value
        });
      }
    }
  });

  
  const validNodes = new Set();
  validLinks.forEach(link => {
    validNodes.add(link.sourceId);
    validNodes.add(link.targetId);
  });

  
  const preliminaryNodes = [];
  stageOrder.value.forEach(stage => {
    const stageNodes = stageGroups[stage].filter(node => validNodes.has(node.key));
    stageNodes.sort((a, b) => {
      const aColor = a.colors[0] || '#CCCCCC';
      const bColor = b.colors[0] || '#CCCCCC';
      return aColor === '#CCCCCC' && bColor !== '#CCCCCC' ? 1 :
             bColor === '#CCCCCC' && aColor !== '#CCCCCC' ? -1 :
             aColor.localeCompare(bColor);
    });
    stageNodes.forEach(node => {
      const nodeIdx = preliminaryNodes.length;
      nodeIndex.set(node.key, nodeIdx);
      preliminaryNodes.push({
        label: node.label,
        stage: node.stage,
        colors: node.colors,
        passages: Array.from(node.passages),
      });
    });
  });

  
  const preliminaryLinks = [];
  validLinks.forEach((link) => {
    const sourceIdx = nodeIndex.get(link.sourceId);
    const targetIdx = nodeIndex.get(link.targetId);
    if (sourceIdx !== undefined && targetIdx !== undefined) {
      preliminaryLinks.push({
        source: sourceIdx,
        target: targetIdx,
        value: link.value
      });
    }
  });

  
  const connectedNodeIndices = new Set();
  preliminaryLinks.forEach(link => {
    connectedNodeIndices.add(link.source);
    connectedNodeIndices.add(link.target);
  });

  
  const finalNodeIndex = new Map();
  preliminaryNodes.forEach((node, idx) => {
    if (connectedNodeIndices.has(idx)) {
      const newIdx = nodes.length;
      finalNodeIndex.set(`${node.label}#${node.stage}`, newIdx);
      nodes.push(node);
    }
  });

  
  preliminaryLinks.forEach(link => {
    const newSourceIdx = finalNodeIndex.get(`${preliminaryNodes[link.source].label}#${preliminaryNodes[link.source].stage}`);
    const newTargetIdx = finalNodeIndex.get(`${preliminaryNodes[link.target].label}#${preliminaryNodes[link.target].stage}`);
    if (newSourceIdx !== undefined && newTargetIdx !== undefined) {
      links.push({
        source: newSourceIdx,
        target: newTargetIdx,
        value: link.value
      });
    }
  });

  
  nodes.forEach(node => {
    node.value = Math.max(
      d3.sum(links.filter(l => l.source === finalNodeIndex.get(`${node.label}#${node.stage}`)), l => l.value),
      d3.sum(links.filter(l => l.target === finalNodeIndex.get(`${node.label}#${node.stage}`)), l => l.value)
    ) || 1; 
  });

  return { nodes, links };
};

const drawBundledSankey = async () => {
  if (isCombined.value) return;

  const { nodes: initialNodes, links: initialLinks } = createSankeyData();

  fontSizeFactor = Math.min(12, 1 + initialNodes.length / 50);

  const nodeCount = initialNodes.length;
  let width = (2000 + nodeCount * 140)*stageSpacingFactor.value 
  let height = 800; 

  
  const chartContainer = d3.select('#bundled-sankey-chart');
  chartContainer.selectAll('*').remove();

  
  const svg = chartContainer
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`);

  
  const numStages = stageOrder.value.length;
  const stageX = {};
  stageOrder.value.forEach((stage, i) => {
    stageX[stage] = (width / (numStages + 1)) * (i + 1);
  });

  
  const totalValue = d3.sum(initialNodes, d => d.value);
  const heightScale = (height - 100 - (initialNodes.length - numStages) * 10) / totalValue * 3;

  
  const nodes = [];
  const nodesByStage = d3.group(initialNodes, d => d.stage);
  stageOrder.value.forEach(stage => {
    const stageNodes = nodesByStage.get(stage) || [];
    const stageValues = stageNodes.map(node => node.value);
    const stageTotalValue = d3.sum(stageValues);
    const stageHeight = stageTotalValue * heightScale;
    const stageYStart = (height - stageHeight) / 2;
    let y = stageYStart;
    stageNodes.forEach((node, index) => {
      const fixedX = stageX[stage];
      const nodeHeight = node.value * heightScale;
      nodes.push({
        ...node,
        id: nodes.length,
        x: fixedX,
        y: y + nodeHeight / 2, 
        height: nodeHeight
      });
      y += nodeHeight + 10;
    });
  });

  
  const links = initialLinks.map(link => ({
    ...link,
    source: nodes[link.source],
    target: nodes[link.target],
    width: link.value * heightScale
  }));

  const g = svg.append('g');

  
  const stageColorGroups = {};
  stageOrder.value.forEach(stage => {
    stageColorGroups[stage] = [];
    const stageNodes = nodes.filter(node => node.stage === stage);
    const colorGroups = d3.group(stageNodes, n => n.colors[0] || '#CCCCCC');
    colorGroups.forEach((groupNodes, color) => {
      stageColorGroups[stage].push({ color, nodes: groupNodes });
    });
  });

  
  stageOrder.value.forEach(stage => {
    stageColorGroups[stage].forEach(group => {
      const secondCodeCounts = {};
      group.nodes.forEach(node => {
        const code = node.label;
        const secondCode = getSecondOrderCode(code, stage);
        if (secondCode) {
          secondCodeCounts[secondCode] = (secondCodeCounts[secondCode] || 0) + 1;
        }
      });
      const mostFrequentSecondCode = Object.entries(secondCodeCounts).reduce(
        (a, b) => (a[1] > b[1] ? a : b),
        ['unclassified', 0]
      )[0];
      group.secondCode = mostFrequentSecondCode;
    });
  });

  
  const padding = 10;
  const allHulls = [];
  stageOrder.value.forEach(stage => {
    const stageHulls = stageColorGroups[stage].map(group => {
      const points = [];
      group.nodes.forEach(node => {
        const left = node.x - (node.bbox?.width / 2 || 20) - padding;
        const right = node.x + (node.bbox?.width / 2 || 20) + padding;
        const top = node.y - (node.bbox?.height / 2 || 10) - padding;
        const bottom = node.y + (node.bbox?.height / 2 || 10) + padding;
        points.push([left, top], [right, top], [left, bottom], [right, bottom]);
      });
      const hullPoints = convexHull(points);
      return { color: group.color, points: hullPoints, group };
    });
    allHulls.push(...stageHulls);
  });

  const hullPath = d3.line()
    .x(d => d[0])
    .y(d => d[1])
    .curve(d3.curveCatmullRomClosed.alpha(0.5));

  const hulls = g.append('g')
    .attr('class', 'hulls')
    .selectAll('.hull')
    .data(allHulls)
    .join('path')
    .attr('class', 'hull')
    .attr('d', d => hullPath(d.points.concat([d.points[0]])))
    .style('fill', d => d.color)
    .style('fill-opacity', 0.5)
    .style('stroke', d => d.color)
    .style('stroke-width', 2)
    .style('stroke-opacity', 0.7);

  const baseFontSize = 30;
  
  const hullLabels = g.append('g')
    .attr('class', 'hull-labels')
    .selectAll('.hull-label')
    .data(allHulls)
    .join('text')
    .attr('class', 'hull-label')
    .attr('x', d => {
      const minX = d3.min(d.points, p => p[0]);
      const maxX = d3.max(d.points, p => p[0]);
      return (minX + maxX) / 2;
    })
    .attr('y', d => {
      const minY = d3.min(d.points, p => p[1]);
      return minY;
    })
    .attr('text-anchor', 'middle')
    .attr('dy', '-0.35em')
    .text(d => d.group.secondCode)
    .style('fill', d => d.color)
    .style('font-size', d => `${baseFontSize * fontSizeFactor}px`)
    .style('font-weight', 'bold');

  
  const node = g.append('g')
    .selectAll('.node')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.x},${d.y})`)
    .on('click', function(event, d) {
      highlightNode.call(this, d, g);
    })
    .on("dblclick", function(event, d) {
      event.stopPropagation();
      handleNodeDoubleClick(d);
    });
    

  const minFontSize = 10;
  const maxFontSize = 30;
  const fontSizeScale = d3.scaleLinear()
    .domain([d3.min(nodes, d => d.value), d3.max(nodes, d => d.value)])
    .range([minFontSize, maxFontSize]);

  nodes.forEach(node => {
    node.inDegree = links.reduce((count, link) => count + (link.target.id === node.id ? 1 : 0), 0);
    node.outDegree = links.reduce((count, link) => count + (link.source.id === node.id ? 1 : 0), 0);
  });

  node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .text(d => d.label)
    .style('font-size', d => `${fontSizeScale(d.value) * fontSizeFactor}px`)
    .each(function(d) {
      d.bbox = this.getBBox();
    })
    .append('title')
    .text(d => `${d.label}\nStage: ${d.stage}\nIn: ${d.inDegree}\nOut: ${d.outDegree}\nPassages: ${d.passages.join(', ')}`);

  
  stageOrder.value.forEach(stage => {
    const groups = stageColorGroups[stage];
    groups.forEach(group => {
      
      group.nodes.sort((a, b) => b.value - a.value);
    });

    const totalHeight = d3.sum(groups, g => 
      d3.sum(g.nodes, n => n.bbox.height) + (g.nodes.length - 1) * intraGroupSpacing
    ) + (groups.length - 1) * interGroupSpacing * fontSizeFactor;
    let y = (height - totalHeight) / 2;

    groups.forEach((group, groupIndex) => {
      group.nodes.forEach((node, nodeIndex) => {
        node.y = y + node.bbox.height / 2;
        if (nodeIndex < group.nodes.length - 1) {
          y += node.bbox.height + intraGroupSpacing;
        }
      });
      if (groupIndex < groups.length - 1) {
        y += interGroupSpacing * fontSizeFactor;
      }
    });
  });

  
  node.attr('transform', d => `translate(${d.x},${d.y})`);

  
  const updatedHulls = [];
  stageOrder.value.forEach(stage => {
    const stageHulls = stageColorGroups[stage].map(group => {
      const points = [];
      group.nodes.forEach(node => {
        const left = node.x - node.bbox.width / 2 - padding;
        const right = node.x + node.bbox.width / 2 + padding;
        const top = node.y - node.bbox.height / 2 - padding;
        const bottom = node.y + node.bbox.height / 2 + padding;
        points.push([left, top], [right, top], [left, bottom], [right, bottom]);
      });
      const hullPoints = convexHull(points);
      return { color: group.color, points: hullPoints, group };
    });
    updatedHulls.push(...stageHulls);
  });

  hulls.data(updatedHulls)
    .attr('d', d => hullPath(d.points.concat([d.points[0]])));

  
  hullLabels.data(updatedHulls)
    .attr('x', d => {
      const minX = d3.min(d.points, p => p[0]);
      const maxX = d3.max(d.points, p => p[0]);
      return (minX + maxX) / 2;
    })
    .attr('y', d => {
      const minY = d3.min(d.points, p => p[1]);
      return minY;
    });

  
  const maxY = d3.max(nodes, d => d.y + d.bbox.height / 2);
  const minY = d3.min(nodes, d => d.y - d.bbox.height / 2);
  if (maxY + 50 > height || minY - 50 < 0) {
    height = maxY - minY + 100;
    svg.attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
  }

  
  const colorGroups = {};
  stageOrder.value.forEach(stage => {
    colorGroups[stage] = stageColorGroups[stage].map(group => ({
      color: group.color,
      nodes: group.nodes,
      avgY: d3.mean(group.nodes, n => n.y)
    }));
  });

  const nodeToGroup = new Map();
  Object.values(colorGroups).forEach(groups => {
    groups.forEach(group => {
      group.nodes.forEach(node => {
        nodeToGroup.set(node, group);
      });
    });
  });

  links.forEach(link => {
    link.sourceGroup = nodeToGroup.get(link.source);
    link.targetGroup = nodeToGroup.get(link.target);
  });

  
  const customLinkPath = (d) => {
    const sourceX = d.sourceX;
    const targetX = d.targetX;
    const sourceY = d.sourceY;
    const targetY = d.targetY;
    const sourceGroupY = d.sourceGroup.avgY;
    const targetGroupY = d.targetGroup.avgY;
    const dx = (targetX - sourceX) / 2;
    const controlX1 = sourceX + dx;
    const controlY1 = sourceGroupY;
    const controlX2 = targetX - dx;
    const controlY2 = targetGroupY;
    return `M ${sourceX}, ${sourceY} C ${controlX1}, ${controlY1}, ${controlX2}, ${controlY2}, ${targetX}, ${targetY}`;
  };

  
  links.forEach(link => {
    const sourceText = node.filter(d => d.id === link.source.id).select('text');
    const targetText = node.filter(d => d.id === link.target.id).select('text');
    const sourceBBox = sourceText.node().getBBox();
    const targetBBox = targetText.node().getBBox();
    link.sourceX = link.source.x + sourceBBox.width / 2;
    link.sourceY = link.source.y;
    link.targetX = link.target.x - targetBBox.width / 2;
    link.targetY = link.target.y;
  });

  
  const link = g.append('g')
    .attr('fill', 'none')
    .selectAll('.link')
    .data(links)
    .join('path')
    .attr('class', 'link')
    .attr('d', customLinkPath)
    .style('stroke', d => d.source.colors[0])
    .attr('stroke-opacity', 0.7)
    .attr('stroke-width', d => Math.max(1, Math.min(d.width, 10)))
    .on('click', function(event, d) {
      highlightLink.call(this, d, g);
    })
    .append('title')
    .text(d => `${d.source.label} → ${d.target.label}\nValue: ${d.value}`);

  
  const zoom = d3.zoom()
    .scaleExtent([0.01, 5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom)
    .on('click', function(event) {
      if (event.target === this) {
        g.selectAll('.link')
          .transition()
          .duration(200)
          .style('stroke-opacity', 0.7)
          .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));
        g.selectAll('.node text')
          .transition()
          .duration(200)
          .style('font-weight', 'normal');
      }
    });

  
  const chartWidth = chartContainer.node().clientWidth;
  const chartHeight = chartContainer.node().clientHeight;
  const scaleX = chartWidth / width;
  const scaleY = chartHeight / height;
  const initialScale = Math.min(scaleX, scaleY, 1);
  const initialTranslate = [
    (chartWidth - width * initialScale) / 2,
    (chartHeight - height * initialScale) / 2
  ];

  svg.call(zoom.transform, d3.zoomIdentity
    .translate(initialTranslate[0], initialTranslate[1])
    .scale(initialScale));

  
  function highlightLink(selectedLink, g) {
    g.selectAll('.link')
      .transition()
      .duration(200)
      .style('stroke-opacity', 0.1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));

    g.selectAll('.node text')
      .transition()
      .duration(200)
      .style('font-weight', 'normal');

    d3.select(this)
      .transition()
      .duration(200)
      .style('stroke-opacity', 1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)) * 1.5);

    const sourceNode = g.selectAll('.node').filter(d => d.id === selectedLink.source.id);
    const targetNode = g.selectAll('.node').filter(d => d.id === selectedLink.target.id);
    sourceNode.select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');
    targetNode.select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');
  }

  
  function highlightNode(selectedNode, g) {
    g.selectAll('.link')
      .transition()
      .duration(200)
      .style('stroke-opacity', 0.1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));

    g.selectAll('.node text')
      .transition()
      .duration(200)
      .style('font-weight', 'normal');

    d3.select(this).select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');

    const connectedLinks = g.selectAll('.link').filter(d => d.source.id === selectedNode.id || d.target.id === selectedNode.id);
    connectedLinks
      .transition()
      .duration(200)
      .style('stroke-opacity', 1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)) * 1.5);
  }
};



const drawSankey = async () => {

  const { nodes: initialNodes, links: initialLinks } = createSankeyData();

  fontSizeFactor = Math.min(12, 1 + initialNodes.length / 50);

  const nodeCount = initialNodes.length;
  let width = (2000 + nodeCount * 140)*stageSpacingFactor.value;
  let height = 800; 

  const chartContainer = d3.select('#sankey-chart');
  chartContainer.selectAll('*').remove();

  const svg = chartContainer
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`);

  const numStages = stageOrder.value.length;
  const stageX = {};
  stageOrder.value.forEach((stage, i) => {
    stageX[stage] = (width / (numStages + 1)) * (i + 1);
  });

  const totalValue = d3.sum(initialNodes, d => d.value);
  const heightScale = (height - 100 - (initialNodes.length - numStages) * 10) / totalValue * 3;

  const nodes = [];
  const nodesByStage = d3.group(initialNodes, d => d.stage);
  stageOrder.value.forEach(stage => {
    const stageNodes = nodesByStage.get(stage) || [];
    const stageValues = stageNodes.map(node => node.value);
    const stageTotalValue = d3.sum(stageValues);
    const stageHeight = stageTotalValue * heightScale;
    const stageYStart = (height - stageHeight) / 2;
    let y = stageYStart;
    stageNodes.forEach((node, index) => {
      const fixedX = stageX[stage];
      const nodeHeight = node.value * heightScale;
      nodes.push({
        ...node,
        id: nodes.length,
        x: fixedX,
        y: y + nodeHeight / 2,
        height: nodeHeight
      });
      y += nodeHeight + 10;
    });
  });

  const links = initialLinks.map(link => ({
    ...link,
    source: nodes[link.source],
    target: nodes[link.target],
    width: link.value * heightScale
  }));

  const g = svg.append('g');

  
  const node = g.append('g')
    .selectAll('.node')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.x},${d.y})`)
    .on('click', function(event, d) {
      highlightNode.call(this, d, g);
    })
    .on("dblclick", function(event, d) {
      event.stopPropagation();
      handleNodeDoubleClick(d);
    });

  const minFontSize = 10;
  const maxFontSize = 30;
  const fontSizeScale = d3.scaleLinear()
    .domain([d3.min(nodes, d => d.value), d3.max(nodes, d => d.value)])
    .range([minFontSize, maxFontSize]);

  nodes.forEach(node => {
    node.inDegree = links.reduce((count, link) => count + (link.target.id === node.id ? 1 : 0), 0);
    node.outDegree = links.reduce((count, link) => count + (link.source.id === node.id ? 1 : 0), 0);
  });

  node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .text(d => d.label)
    .style('font-size', d => `${fontSizeScale(d.value) * fontSizeFactor}px`)
    .style('fill', '#333333') 
    .each(function(d) {
      d.bbox = this.getBBox();
    })
    .append('title')
    .text(d => `${d.label}\nStage: ${d.stage}\nIn: ${d.inDegree}\nOut: ${d.outDegree}\nPassages: ${d.passages.join(', ')}`);

  
  const stageColorGroups = {};
  stageOrder.value.forEach(stage => {
    stageColorGroups[stage] = [{ nodes: nodes.filter(n => n.stage === stage) }];
  });

  stageOrder.value.forEach(stage => {
    const groups = stageColorGroups[stage];
    groups.forEach(group => {
      group.nodes.sort((a, b) => b.value - a.value);
    });

    const totalHeight = d3.sum(groups, g => 
      d3.sum(g.nodes, n => n.bbox.height) + (g.nodes.length - 1) * intraGroupSpacing
    ) + (groups.length - 1) * interGroupSpacing * fontSizeFactor;
    let y = (height - totalHeight) / 2;

    groups.forEach((group, groupIndex) => {
      group.nodes.forEach((node, nodeIndex) => {
        node.y = y + node.bbox.height / 2;
        if (nodeIndex < group.nodes.length - 1) {
          y += node.bbox.height + intraGroupSpacing;
        }
      });
      if (groupIndex < groups.length - 1) {
        y += interGroupSpacing * fontSizeFactor;
      }
    });
  });

  node.attr('transform', d => `translate(${d.x},${d.y})`);

  
  const maxY = d3.max(nodes, d => d.y + d.bbox.height / 2);
  const minY = d3.min(nodes, d => d.y - d.bbox.height / 2);
  if (maxY + 50 > height || minY - 50 < 0) {
    height = maxY - minY + 100;
    svg.attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
  }

  
  links.forEach(link => {
    const sourceText = node.filter(d => d.id === link.source.id).select('text');
    const targetText = node.filter(d => d.id === link.target.id).select('text');
    const sourceBBox = sourceText.node().getBBox();
    const targetBBox = targetText.node().getBBox();
    link.sourceX = link.source.x + sourceBBox.width / 2;
    link.sourceY = link.source.y;
    link.targetX = link.target.x - targetBBox.width / 2;
    link.targetY = link.target.y;
  });

  
  const link = g.append('g')
    .attr('fill', 'none')
    .selectAll('.link')
    .data(links)
    .join('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal()
      .source(d => [d.sourceX, d.sourceY])
      .target(d => [d.targetX, d.targetY])
    )
    .style('stroke', '#333333') 
    .attr('stroke-opacity', 0.7)
    .attr('stroke-width', d => Math.max(1, Math.min(d.width, 10)))
    .on('click', function(event, d) {
      highlightLink.call(this, d, g);
    })
    .append('title')
    .text(d => `${d.source.label} → ${d.target.label}\nValue: ${d.value}`);

  
  const zoom = d3.zoom()
    .scaleExtent([0.01, 5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom)
    .on('click', function(event) {
      if (event.target === this) {
        g.selectAll('.link')
          .transition()
          .duration(200)
          .style('stroke-opacity', 0.7)
          .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));
        g.selectAll('.node text')
          .transition()
          .duration(200)
          .style('font-weight', 'normal');
      }
    });

  const chartWidth = chartContainer.node().clientWidth;
  const chartHeight = chartContainer.node().clientHeight;
  const scaleX = chartWidth / width;
  const scaleY = chartHeight / height;
  const initialScale = Math.min(scaleX, scaleY, 1);
  const initialTranslate = [
    (chartWidth - width * initialScale) / 2,
    (chartHeight - height * initialScale) / 2
  ];

  svg.call(zoom.transform, d3.zoomIdentity
    .translate(initialTranslate[0], initialTranslate[1])
    .scale(initialScale));

  function highlightLink(selectedLink, g) {
    g.selectAll('.link')
      .transition()
      .duration(200)
      .style('stroke-opacity', 0.1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));

    g.selectAll('.node text')
      .transition()
      .duration(200)
      .style('font-weight', 'normal');

    d3.select(this)
      .transition()
      .duration(200)
      .style('stroke-opacity', 1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)) * 1.5);

    const sourceNode = g.selectAll('.node').filter(d => d.id === selectedLink.source.id);
    const targetNode = g.selectAll('.node').filter(d => d.id === selectedLink.target.id);
    sourceNode.select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');
    targetNode.select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');
  }

  function highlightNode(selectedNode, g) {
    g.selectAll('.link')
      .transition()
      .duration(200)
      .style('stroke-opacity', 0.1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)));

    g.selectAll('.node text')
      .transition()
      .duration(200)
      .style('font-weight', 'normal');

    d3.select(this).select('text')
      .transition()
      .duration(200)
      .style('font-weight', 'bold');

    const connectedLinks = g.selectAll('.link').filter(d => d.source.id === selectedNode.id || d.target.id === selectedNode.id);
    connectedLinks
      .transition()
      .duration(200)
      .style('stroke-opacity', 1)
      .style('stroke-width', d => Math.max(1, Math.min(d.width, 10)) * 1.5);
  }
};

function convexHull(points) {
  
  if (points.length < 3) return points;

  
  const uniquePoints = Array.from(new Set(points.map(p => `${p[0]},${p[1]}`)))
    .map(str => str.split(',').map(Number));

  
  if (uniquePoints.length < 3) return uniquePoints;

  
  let start = uniquePoints[0];
  for (let p of uniquePoints) {
    if (p[1] < start[1] || (p[1] === start[1] && p[0] < start[0])) {
      start = p;
    }
  }

  
  
  uniquePoints.sort((a, b) => {
    const angleA = Math.atan2(a[1] - start[1], a[0] - start[0]);
    const angleB = Math.atan2(b[1] - start[1], b[0] - start[0]);
    const angleDiff = angleA - angleB;
    if (angleDiff === 0) {
      const distA = (a[0] - start[0]) ** 2 + (a[1] - start[1]) ** 2;
      const distB = (b[0] - start[0]) ** 2 + (b[1] - start[1]) ** 2;
      return distA - distB;
    }
    return angleDiff;
  });

  
  const stack = [uniquePoints[0], uniquePoints[1]];

  
  for (let i = 2; i < uniquePoints.length; i++) {
    let top = stack[stack.length - 1];
    let nextToTop = stack[stack.length - 2];
    
    let crossProduct =
      (top[0] - nextToTop[0]) * (uniquePoints[i][1] - nextToTop[1]) -
      (top[1] - nextToTop[1]) * (uniquePoints[i][0] - nextToTop[0]);
    
    
    while (crossProduct <= 0 && stack.length > 1) {
      stack.pop();
      top = stack[stack.length - 1];
      nextToTop = stack[stack.length - 2];
      crossProduct =
        (top[0] - nextToTop[0]) * (uniquePoints[i][1] - nextToTop[1]) -
        (top[1] - nextToTop[1]) * (uniquePoints[i][0] - nextToTop[0]);
    }
    stack.push(uniquePoints[i]);
  }

  return stack;
}

const drawSecondSankey = async () => {
  const { nodes: initialNodes, links: initialLinks } = createSankeyData();

  const nodeCount = initialNodes.length;
  let width = (2000 + nodeCount * 50)* stageSpacingFactor.value
  let height = Math.max(600, initialNodes.length * 20); 

  
  expandedLinkKey.value = null;
  const chartContainer = d3.select('#sankey-chart');
  chartContainer.selectAll('*').remove();

  
  const svg = chartContainer
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`);

  
  const sankey = Sankey()
    .nodeId((d, i) => i)
    .nodeWidth(20)
    .nodePadding(60)
    .extent([[50, 50], [width - 50, height - 50]])
    .iterations(0)
    .nodeSort((a, b) => {
      if (a.stage !== b.stage) return stageOrder.value.indexOf(a.stage) - stageOrder.value.indexOf(b.stage);
      const aColor = a.colors[0] || '#CCCCCC';
      const bColor = b.colors[0] || '#CCCCCC';
      return aColor === '#CCCCCC' && bColor !== '#CCCCCC' ? 1 :
             bColor === '#CCCCCC' && aColor !== '#CCCCCC' ? -1 :
             aColor.localeCompare(bColor);
    });

  
  const nodesByStage = d3.group(initialNodes, d => d.stage);
  const sortedNodes = [];
  const nodeMap = new Map();
  stageOrder.value.forEach(stage => {
    const stageNodes = nodesByStage.get(stage) || [];
    stageNodes.sort((a, b) => {
      const aColor = a.colors[0] || '#CCCCCC';
      const bColor = b.colors[0] || '#CCCCCC';
      return aColor === '#CCCCCC' && bColor !== '#CCCCCC' ? 1 :
             bColor === '#CCCCCC' && aColor !== '#CCCCCC' ? -1 :
             aColor.localeCompare(bColor);
    });
    stageNodes.forEach(node => {
      const newIndex = sortedNodes.length;
      nodeMap.set(`${node.label}#${node.stage}`, newIndex);
      sortedNodes.push({ ...node, id: newIndex });
    });
  });

  
  const validLinks = initialLinks
    .map(link => {
      const sourceNode = initialNodes[link.source];
      const targetNode = initialNodes[link.target];
      if (!sourceNode || !targetNode) return null;
      const sourceKey = `${sourceNode.label}#${sourceNode.stage}`;
      const targetKey = `${targetNode.label}#${targetNode.stage}`;
      const sourceIdx = nodeMap.get(sourceKey);
      const targetIdx = nodeMap.get(targetKey);
      return sourceIdx !== undefined && targetIdx !== undefined ? { ...link, source: sourceIdx, target: targetIdx } : null;
    })
    .filter(link => link !== null);

  const graph = { nodes: sortedNodes, links: validLinks };

  
  try {
    sankey(graph);
  } catch (error) {
    console.error('Sankey layout error:', error);
    return;
  }


  
  const numStages = stageOrder.value.length;
  const stageX = {};
  stageOrder.value.forEach((stage, i) => {
    stageX[stage] = (width / (numStages + 1)) * (i + 1);
  });

  
  const nodePadding = sankey.nodePadding();
  const nodesByStageMap = d3.group(graph.nodes, d => d.stage);
  stageOrder.value.forEach(stage => {
    const stageNodes = nodesByStageMap.get(stage) || [];
    if (stageNodes.length === 0) return;

    stageNodes.sort((a, b) => a.y0 - b.y0);
    let lastY1 = stageNodes[0].y0 - nodePadding;
    stageNodes.forEach(node => {
      const fixedX = stageX[node.stage];
      node.x0 = fixedX - (sankey.nodeWidth() / 2);
      node.x1 = fixedX + (sankey.nodeWidth() / 2);

      const nodeHeight = node.y1 - node.y0;
      if (node.y0 - lastY1 < nodePadding) {
        node.y0 = lastY1 + nodePadding;
        node.y1 = node.y0 + nodeHeight;
      }
      lastY1 = node.y1;
    });

    
    const maxY = d3.max(stageNodes, d => d.y1);
    if (maxY + 50 > height) {
      height = maxY + 50;
      svg.attr('height', height).attr('viewBox', `0 0 ${width} ${height}`);
    }
  });

  
  const maxX = d3.max(graph.nodes, d => d.x1);
  if (maxX + 50 > width) {
    width = maxX + 50;
    svg.attr('width', width).attr('viewBox', `0 0 ${width} ${height}`);
  }

  
  graph.links.forEach(link => {
    link.y0 = link.source.y0 + (link.source.y1 - link.source.y0) / 2;
    link.y1 = link.target.y0 + (link.target.y1 - link.target.y0) / 2;
  });

  
  const adjustStageSourceLinks = (stageIndex) => {
  
  const stages = Array.from(new Set(graph.nodes.map(n => n.stage)))
    .sort((a, b) => {
      
      const aX = graph.nodes.find(n => n.stage === a)?.x0 || 0;
      const bX = graph.nodes.find(n => n.stage === b)?.x0 || 0;
      return aX - bX;
    });

  if (stageIndex >= stages.length) return;

  const targetStage = stages[stageIndex];
  const stageNodes = graph.nodes.filter(n => n.stage === targetStage);

  stageNodes.forEach(node => {
    const outgoingLinks = graph.links
      .filter(link => link.source === node)
      .sort((a, b) => a.y0 - b.y0); 

    let currentY = node.y0;
    outgoingLinks.forEach(link => {
      link.y0 = currentY + link.width / 2;
      currentY += link.width;
    });
    
    
    node.y1 = Math.max(node.y1, currentY);
  });
 };

  const adjustIncomingLinksToStage = (stageIndex) => {
  
  const stages = Array.from(new Set(graph.nodes.map(n => n.stage)))
    .sort((a, b) => {
      const aX = graph.nodes.find(n => n.stage === a)?.x0 || 0;
      const bX = graph.nodes.find(n => n.stage === b)?.x0 || 0;
      return aX - bX;
    });

  if (stageIndex >= stages.length) return;
  const targetStage = stages[stageIndex];

  
  const targetNodes = graph.nodes.filter(n => n.stage === targetStage);

  targetNodes.forEach(node => {
    
    const incomingLinks = graph.links
      .filter(link => link.target === node)
      .sort((a, b) => a.y1 - b.y1); 

    let currentY = node.y0;
    incomingLinks.forEach(link => {
      link.y1 = currentY + link.width / 2; 
      currentY += link.width;
    });

    
    node.y1 = Math.max(node.y1, currentY);
  });
};




const adjustNodeHeightByIncomingLinks = (stageIndex) => {
  
  const stages = Array.from(new Set(graph.nodes.map(n => n.stage)))
    .sort((a, b) => {
      const aX = graph.nodes.find(n => n.stage === a)?.x0 || 0;
      const bX = graph.nodes.find(n => n.stage === b)?.x0 || 0;
      return aX - bX;
    });

  if (stageIndex >= stages.length) return;
  const targetStage = stages[stageIndex];

  graph.nodes
    .filter(node => node.stage === targetStage)
    .forEach(node => {
      
      const incomingLinks = graph.links.filter(link => link.target === node);
      
      if (incomingLinks.length > 0) {
        
        const lowestLinkPoint = d3.max(incomingLinks, link => 
          link.y1 + link.width / 2
        );
        
        
        node.y1 = lowestLinkPoint;
      }
    });
};



const adjustOutgoingLinkWidths = (stageIndex) => {
  
  const stages = Array.from(new Set(graph.nodes.map(n => n.stage)))
    .sort((a, b) => {
      const aX = graph.nodes.find(n => n.stage === a)?.x0 || 0;
      const bX = graph.nodes.find(n => n.stage === b)?.x0 || 0;
      return aX - bX;
    });

  if (stageIndex >= stages.length) return;
  const targetStage = stages[stageIndex];

  graph.nodes
    .filter(node => node.stage === targetStage)
    .forEach(node => {
      const outgoingLinks = graph.links.filter(link => link.source === node);
      const totalValue = d3.sum(outgoingLinks, link => link.value);
      const nodeHeight = node.y1 - node.y0;

      if (totalValue > 0 && nodeHeight > 0) {
        outgoingLinks.forEach(link => {
          
          link.width = (link.value / totalValue) * nodeHeight;
        });
      }
    });
};


const adjustAllStages = () => {
  let i = 0;
  
  adjustStageSourceLinks(i);
  
  
  while (i <= numStages - 1) {
    
    adjustIncomingLinksToStage(i);
    
    
    adjustNodeHeightByIncomingLinks(i);
    
    
    adjustOutgoingLinkWidths(i);
    
    
    adjustStageSourceLinks(i);
    
    i++;  
  }
};


adjustAllStages();

  
  graph.links.forEach(link => {
    const sourceKey = `${link.source.label}#${link.source.stage}`;
    const targetKey = `${link.target.label}#${link.target.stage}`;
    const combinedKey = `${sourceKey}|${targetKey}`;
    const allSubs = combinedSubLinksMap.get(combinedKey) || [];
    
    link.subLinks = allSubs.filter(s => s.value >= threshold.value);
  });



  const g = svg.append('g');

  
  graph.nodes.forEach(n => {
    n._origX0 = n.x0;
    n._origX1 = n.x1;
  });

  
  const EXPAND_WIDTH = 120; 

  
  function expandBand(linkData, container) {
    
    container.selectAll('.expansion-layer').remove();

    const src = linkData.source;
    const tgt = linkData.target;
    const srcOrigWidth = src._origX1 - src._origX0;
    const tgtOrigWidth = tgt._origX1 - tgt._origX0;

    
    const srcNodeSel = container.selectAll('.node').filter(d => d.id === src.id);
    const tgtNodeSel = container.selectAll('.node').filter(d => d.id === tgt.id);

    
    srcNodeSel.select('rect')
      .transition('expand').duration(300)
      .attr('width', srcOrigWidth + EXPAND_WIDTH)
      .style('stroke-width', 0);

    
    tgtNodeSel
      .transition('expand').duration(300)
      .attr('transform', d => `translate(${d._origX0 - EXPAND_WIDTH},${d.y0})`);
    tgtNodeSel.select('rect')
      .transition('expand').duration(300)
      .attr('width', tgtOrigWidth + EXPAND_WIDTH)
      .style('stroke-width', 0);
    
    tgtNodeSel.select('text')
      .transition('expand').duration(300)
      .attr('x', d => (d._origX1 - d._origX0) / 2 + EXPAND_WIDTH);

    
    container.selectAll('.link')
      .transition('expand').duration(300)
      .style('stroke-opacity', l => l === linkData ? 0 : 0.1);

    
    container.selectAll('.node').filter(d => d.id !== src.id && d.id !== tgt.id)
      .select('rect')
      .transition('expand').duration(300)
      .style('stroke-width', 0);

    
    const subs = linkData.subLinks || [];
    if (subs.length === 0) return;

    
    const srcYTop = linkData.y0 - linkData.width / 2;
    const srcYBot = linkData.y0 + linkData.width / 2;
    const tgtYTop = linkData.y1 - linkData.width / 2;
    const tgtYBot = linkData.y1 + linkData.width / 2;

    
    subs.sort((a, b) => b.value - a.value);

    
    const labelH = 14;
    const labelFontSize = 11;

    
    const _canvas = document.createElement('canvas');
    const _ctx = _canvas.getContext('2d');
    _ctx.font = `normal ${labelFontSize}px sans-serif`;
    function getLabelLines(label, availW) {
      const textW = _ctx.measureText(label).width;
      return Math.max(1, Math.ceil(textW / Math.max(availW - 8, 1))); 
    }

    
    const srcValueSum = {};
    const tgtValueSum = {};
    subs.forEach(sub => {
      const sc = sub.source.split('#')[0];
      const tc = sub.target.split('#')[0];
      srcValueSum[sc] = (srcValueSum[sc] || 0) + sub.value;
      tgtValueSum[tc] = (tgtValueSum[tc] || 0) + sub.value;
    });

    
    let srcLabels = Object.keys(srcValueSum)
      .sort((a, b) => srcValueSum[b] - srcValueSum[a]);
    let tgtLabels = Object.keys(tgtValueSum)
      .sort((a, b) => tgtValueSum[b] - tgtValueSum[a]);

    
    const srcAvailH = srcYBot - srcYTop;
    const tgtAvailH = tgtYBot - tgtYTop;
    const srcAvailW = srcOrigWidth + EXPAND_WIDTH;
    const tgtAvailW = tgtOrigWidth + EXPAND_WIDTH;

    
    const srcLabelInfo = {};
    srcLabels.forEach(l => {
      const lines = getLabelLines(l, srcAvailW);
      srcLabelInfo[l] = { lines, h: lines * labelH };
    });
    const tgtLabelInfo = {};
    tgtLabels.forEach(l => {
      const lines = getLabelLines(l, tgtAvailW);
      tgtLabelInfo[l] = { lines, h: lines * labelH };
    });

    
    {
      let accH = 0;
      const kept = [];
      for (const l of srcLabels) {
        if (accH + srcLabelInfo[l].h > srcAvailH && kept.length > 0) break;
        accH += srcLabelInfo[l].h;
        kept.push(l);
      }
      srcLabels = kept;
    }
    {
      let accH = 0;
      const kept = [];
      for (const l of tgtLabels) {
        if (accH + tgtLabelInfo[l].h > tgtAvailH && kept.length > 0) break;
        accH += tgtLabelInfo[l].h;
        kept.push(l);
      }
      tgtLabels = kept;
    }

    
    const srcLabelY = {};  
    const srcLabelCenterY = {};  
    {
      const totalH = srcLabels.reduce((s, l) => s + srcLabelInfo[l].h, 0);
      const gap = (srcAvailH - totalH) / (srcLabels.length + 1);
      let curY = srcYTop;
      srcLabels.forEach(l => {
        curY += gap;
        srcLabelY[l] = curY;
        srcLabelCenterY[l] = curY + srcLabelInfo[l].h / 2;
        curY += srcLabelInfo[l].h;
      });
    }
    const tgtLabelY = {};  
    const tgtLabelCenterY = {};  
    {
      const totalH = tgtLabels.reduce((s, l) => s + tgtLabelInfo[l].h, 0);
      const gap = (tgtAvailH - totalH) / (tgtLabels.length + 1);
      let curY = tgtYTop;
      tgtLabels.forEach(l => {
        curY += gap;
        tgtLabelY[l] = curY;
        tgtLabelCenterY[l] = curY + tgtLabelInfo[l].h / 2;
        curY += tgtLabelInfo[l].h;
      });
    }

    
    const firstOrderCodeFreq = {};
    for (const pName in passageDatabase) {
      if (passageDatabase[pName] && passageDatabase[pName].firstOrderCodes) {
        passageDatabase[pName].firstOrderCodes.forEach(c => {
          firstOrderCodeFreq[c] = (firstOrderCodeFreq[c] || 0) + 1;
        });
      }
    }
    const maxFreq = Math.max(...Object.values(firstOrderCodeFreq), 1);
    const minFreq = Math.min(...Object.values(firstOrderCodeFreq), 0);
    const lightnessScale = d3.scaleLinear()
      .domain([minFreq, maxFreq])
      .range([70, 0]);

    
    const expLayer = container.append('g').attr('class', 'expansion-layer');

    

    
    const srcLinkX = src._origX1 + EXPAND_WIDTH;   
    const tgtLinkX = tgt._origX0 - EXPAND_WIDTH;   
    const midX = (srcLinkX + tgtLinkX) / 2;        

    
    
    const srcTooltip = {};
    srcLabels.forEach(label => {
      const outCount = subs.filter(s => s.source.split('#')[0] === label).length;
      const inCount = subs.filter(s => s.target.split('#')[0] === label).length;
      
      const passages = [];
      for (const pName in passageDatabase) {
        if (passageDatabase[pName] && passageDatabase[pName].firstOrderCodes &&
            passageDatabase[pName].firstOrderCodes.includes(label)) {
          passages.push(pName);
        }
      }
      srcTooltip[label] = `${label}\nStage: ${src.stage}\nIn: ${inCount}\nOut: ${outCount}\nPassages: ${passages.join(', ')}`;
    });
    const tgtTooltip = {};
    tgtLabels.forEach(label => {
      const outCount = subs.filter(s => s.source.split('#')[0] === label).length;
      const inCount = subs.filter(s => s.target.split('#')[0] === label).length;
      const passages = [];
      for (const pName in passageDatabase) {
        if (passageDatabase[pName] && passageDatabase[pName].firstOrderCodes &&
            passageDatabase[pName].firstOrderCodes.includes(label)) {
          passages.push(pName);
        }
      }
      tgtTooltip[label] = `${label}\nStage: ${tgt.stage}\nIn: ${inCount}\nOut: ${outCount}\nPassages: ${passages.join(', ')}`;
    });

    
    expLayer.selectAll('.exp-src-fo')
      .data(srcLabels)
      .join('foreignObject')
      .attr('class', 'exp-src-fo')
      .attr('x', src._origX0)
      .attr('y', label => srcLabelY[label])
      .attr('width', srcAvailW)
      .attr('height', label => srcLabelInfo[label].h)
      .append('xhtml:div')
      .style('width', '100%')
      .style('height', '100%')
      .style('display', 'flex')
      .style('align-items', 'center')
      .style('padding', '0 4px')
      .style('box-sizing', 'border-box')
      .style('font-size', `${labelFontSize}px`)
      .style('font-weight', 'normal')
      .style('line-height', `${labelH}px`)
      .style('color', label => `hsl(0, 0%, ${lightnessScale(firstOrderCodeFreq[label] || 0)}%)`)
      .style('overflow', 'hidden')
      .style('white-space', 'normal')
      .style('word-wrap', 'break-word')
      .style('overflow-wrap', 'break-word')
      .style('text-align', 'left')
      .style('opacity', 0)
      .attr('title', label => srcTooltip[label])
      .text(label => label)
      .transition().delay(200).duration(300)
      .style('opacity', 1);

    
    expLayer.selectAll('.exp-tgt-fo')
      .data(tgtLabels)
      .join('foreignObject')
      .attr('class', 'exp-tgt-fo')
      .attr('x', tgt._origX0 - EXPAND_WIDTH)
      .attr('y', label => tgtLabelY[label])
      .attr('width', tgtAvailW)
      .attr('height', label => tgtLabelInfo[label].h)
      .append('xhtml:div')
      .style('width', '100%')
      .style('height', '100%')
      .style('display', 'flex')
      .style('align-items', 'center')
      .style('padding', '0 4px')
      .style('box-sizing', 'border-box')
      .style('font-size', `${labelFontSize}px`)
      .style('font-weight', 'normal')
      .style('line-height', `${labelH}px`)
      .style('color', label => `hsl(0, 0%, ${lightnessScale(firstOrderCodeFreq[label] || 0)}%)`)
      .style('overflow', 'hidden')
      .style('white-space', 'normal')
      .style('word-wrap', 'break-word')
      .style('overflow-wrap', 'break-word')
      .style('text-align', 'left')
      .style('opacity', 0)
      .attr('title', label => tgtTooltip[label])
      .text(label => label)
      .transition().delay(200).duration(300)
      .style('opacity', 1);

    
    const filteredSubs = subs.filter(sub => {
      const sc = sub.source.split('#')[0];
      const tc = sub.target.split('#')[0];
      return srcLabels.includes(sc) && tgtLabels.includes(tc);
    });

    
    const maxSubVal = d3.max(filteredSubs, s => s.value) || 1;
    const subWidthScale = d3.scaleLinear()
      .domain([1, maxSubVal])
      .range([1.5, Math.min(6, linkData.width / Math.max(filteredSubs.length, 1))])

    const subLinksData = filteredSubs.map(sub => {
      const srcCode = sub.source.split('#')[0];
      const tgtCode = sub.target.split('#')[0];
      return {
        sourceX: srcLinkX,
        sourceY: srcLabelCenterY[srcCode],
        targetX: tgtLinkX,
        targetY: tgtLabelCenterY[tgtCode],
        value: sub.value,
        width: subWidthScale(sub.value),
        srcCode,
        tgtCode
      };
    });

    
    const subLinkPath = (d) => {
      const xi = d3.interpolateNumber(d.sourceX, d.targetX);
      const x2 = xi(0.5);
      return `M${d.sourceX},${d.sourceY} C${x2},${d.sourceY} ${x2},${d.targetY} ${d.targetX},${d.targetY}`;
    };

    
    const allSrcY = subLinksData.map(d => d.sourceY);
    const allTgtY = subLinksData.map(d => d.targetY);
    const srcMinY = Math.min(...allSrcY);
    const srcMaxY = Math.max(...allSrcY);
    const tgtMinY = Math.min(...allTgtY);
    const tgtMaxY = Math.max(...allTgtY);
    const bandPad = 3;
    const bandColor = src.colors[0] || '#666';

    
    const bandPath = `
      M${srcLinkX},${srcMinY - bandPad}
      C${midX},${srcMinY - bandPad} ${midX},${tgtMinY - bandPad} ${tgtLinkX},${tgtMinY - bandPad}
      L${tgtLinkX},${tgtMaxY + bandPad}
      C${midX},${tgtMaxY + bandPad} ${midX},${srcMaxY + bandPad} ${srcLinkX},${srcMaxY + bandPad}
      Z
    `;

    expLayer.append('path')
      .attr('class', 'exp-band-fill')
      .attr('d', bandPath)
      .attr('fill', bandColor)
      .attr('fill-opacity', 0)
      .attr('stroke', 'none')
      .transition().delay(200).duration(350)
      .attr('fill-opacity', 0.45);

    
    expLayer.selectAll('.exp-link-outline')
      .data(subLinksData)
      .join('path')
      .attr('class', 'exp-link-outline')
      .attr('d', subLinkPath)
      .attr('fill', 'none')
      .attr('stroke', 'white')
      .attr('stroke-width', d => d.width + 1)
      .attr('stroke-opacity', 0)
      .transition().delay(250).duration(350)
      .attr('stroke-opacity', 0.9);

    
    expLayer.selectAll('.exp-link')
      .data(subLinksData)
      .join('path')
      .attr('class', 'exp-link')
      .attr('d', subLinkPath)
      .attr('fill', 'none')
      .attr('stroke', bandColor)
      .attr('stroke-width', d => d.width)
      .attr('stroke-opacity', 0)
      .style('cursor', 'pointer')
      .on('click', function(event, d) {
        event.stopPropagation();
        
        expLayer.selectAll('.exp-link')
          .transition().duration(200)
          .attr('stroke-opacity', 0.1);
        expLayer.selectAll('.exp-link-outline')
          .transition().duration(200)
          .attr('stroke-opacity', 0.1);
        d3.select(this)
          .transition().duration(200)
          .attr('stroke-opacity', 1)
          .attr('stroke-width', d.width);
        expLayer.selectAll('.exp-link-outline').filter(od => od === d)
          .transition().duration(200)
          .attr('stroke-opacity', 0.9)
          .attr('stroke-width', d.width + 2);
      })
      .on('contextmenu', function(event, d) {
        event.preventDefault();
        event.stopPropagation();
        showContextMenu(event, 'Theoretical Memos', `${d.srcCode}—${d.tgtCode}`);
      })
      .transition().delay(250).duration(350)
      .attr('stroke-opacity', 0.7);

    
    expLayer.selectAll('.exp-link')
      .append('title')
      .text(d => `${d.srcCode} → ${d.tgtCode}\nValue: ${d.value}`);

    


    
    expLayer.selectAll('.exp-src-fo')
      .style('cursor', 'pointer')
      .on('click', function(event, label) {
        event.stopPropagation();
        
        expLayer.selectAll('.exp-link')
          .transition().duration(200)
          .attr('stroke-opacity', d => d.srcCode === label ? 1 : 0.1)
          .attr('stroke-width', d => d.width);
        expLayer.selectAll('.exp-link-outline')
          .transition().duration(200)
          .attr('stroke-opacity', d => d.srcCode === label ? 0.9 : 0.1)
          .attr('stroke-width', d => d.width + 2);
      });

    
    expLayer.selectAll('.exp-tgt-fo')
      .style('cursor', 'pointer')
      .on('click', function(event, label) {
        event.stopPropagation();
        
        expLayer.selectAll('.exp-link')
          .transition().duration(200)
          .attr('stroke-opacity', d => d.tgtCode === label ? 1 : 0.1)
          .attr('stroke-width', d => d.width);
        expLayer.selectAll('.exp-link-outline')
          .transition().duration(200)
          .attr('stroke-opacity', d => d.tgtCode === label ? 0.9 : 0.1)
          .attr('stroke-width', d => d.width + 2);
      });

    
    expLayer.select('.exp-band-fill')
      .style('cursor', 'default')
      .on('click', function(event) {
        event.stopPropagation();
        
        expLayer.selectAll('.exp-link')
          .transition().duration(200)
          .attr('stroke-opacity', 0.7)
          .attr('stroke-width', d => d.width);
        expLayer.selectAll('.exp-link-outline')
          .transition().duration(200)
          .attr('stroke-opacity', 0.9)
          .attr('stroke-width', d => d.width + 2);
      });
  }

  
  function collapseExpandedBand(container) {
    
    container.selectAll('.expansion-layer').remove();

    
    container.selectAll('.node')
      .transition().duration(300)
      .attr('transform', d => `translate(${d._origX0},${d.y0})`);

    container.selectAll('.node rect')
      .transition().duration(300)
      .attr('width', d => d._origX1 - d._origX0)
      .style('stroke-width', 0);

    
    container.selectAll('.node text')
      .transition().duration(300)
      .attr('x', d => (d._origX1 - d._origX0) / 2);
    container.selectAll('.link')
      .transition().duration(300)
      .style('stroke-opacity', 0.7)
      .style('stroke-width', d => Math.max(1, d.width));

    expandedLinkKey.value = null;
  }

  
  function renderExpansionDetail(linkData, container) {
    
    const sourceKey = `${linkData.source.label}#${linkData.source.stage}`;
    const targetKey = `${linkData.target.label}#${linkData.target.stage}`;
    const combinedKey = `${sourceKey}|${targetKey}`;
    const allSubs = combinedSubLinksMap.get(combinedKey) || [];
    linkData.subLinks = allSubs.filter(s => s.value >= threshold.value);

    
    container.selectAll('.expansion-layer').remove();
    if (linkData.subLinks.length > 0) {
      expandBand(linkData, container);
    }
  }

  
  const links = g.append('g')
    .attr('fill', 'none')
    .selectAll('.link')
    .data(graph.links)
    .join('path')
    .attr('class', 'link')
    .attr('d', sankeyLinkHorizontal())
    .style('stroke', d => d.source.colors[0])
    .attr('stroke-opacity', 0.7)
    .attr('stroke-width', d => Math.max(1, d.width))
    .style('cursor', 'pointer')
    .on('click', function(event, d) {
      event.stopPropagation();
      const key = `${d.source.label}#${d.source.stage}|${d.target.label}#${d.target.stage}`;
      if (expandedLinkKey.value === key) {
        
        collapseExpandedBand(g);
      } else {
        
        if (expandedLinkKey.value) {
          collapseExpandedBand(g);
        }
        
        setTimeout(() => {
          expandedLinkKey.value = key;
          expandBand(d, g);
        }, expandedLinkKey.value ? 350 : 0);
      }
    })
    .append('title')
    .text(d => `${d.source.label} → ${d.target.label}\nValue: ${d.value}\nClick to expand First-Order detail`);

  
  const node = g.append('g')
    .selectAll('.node')
    .data(graph.nodes)
    .join('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.x0},${d.y0})`)
    .on('click', function(event, d) {
      if (expandedLinkKey.value) {
        collapseExpandedBand(g);
        return;
      }
      highlightNode.call(this, d, g);
    });

  node.append('rect')
    .attr('height', d => d.y1 - d.y0)
    .attr('width', d => d.x1 - d.x0)
    .attr('fill', d => d.colors[0] || '#CCCCCC')
    .attr('stroke-width', 0)
    .append('title')
    .text(d => `${d.label}\nStage: ${d.stage}\nPassages: ${d.passages.join(', ')}`);

  
node.append('text')
    .attr('x', d => (d.x1 - d.x0) / 2)  
    .attr('y', -15)  
    .attr('dy', '0.15em')
    .attr('text-anchor', 'middle')  
    .style('fill', d => d.colors[0] || '#CCCCCC')  
    .text(d => d.label)
    .style('font-size', '30px');

  
  const zoom = d3.zoom()
    .scaleExtent([0.01,5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom)
    .on('click', function(event) {
      if (event.target === this) {
        
        if (expandedLinkKey.value) {
          collapseExpandedBand(g);
        } else {
          g.selectAll('.link')
            .transition()
            .duration(200)
            .style('stroke-opacity', 0.7)
            .style('stroke-width', d => Math.max(1, d.width));
          g.selectAll('.node rect')
            .transition()
            .duration(200)
            .style('stroke-width', 0);
        }
      }
    });

  
  const chartWidth = chartContainer.node().clientWidth;
  const chartHeight = chartContainer.node().clientHeight;
  const scaleX = chartWidth / width;
  const scaleY = chartHeight / height;
  const initialScale = Math.min(scaleX, scaleY, 1);
  const initialTranslate = [
    (chartWidth - width * initialScale) / 2,
    (chartHeight - height * initialScale) / 2
  ];

  svg.call(zoom.transform, d3.zoomIdentity
    .translate(initialTranslate[0], initialTranslate[1])
    .scale(initialScale));

  
  function highlightNode(selectedNode, g) {
    g.selectAll('.link')
      .transition()
      .duration(200)
      .style('stroke-opacity', 0.1)
      .style('stroke-width', d => Math.max(1, d.width));

    g.selectAll('.node rect')
      .transition()
      .duration(200)
      .style('stroke-width', 0);

    d3.select(this).select('rect')
      .transition()
      .duration(200)
      .style('stroke-width', 3);

    const connectedLinks = g.selectAll('.link').filter(d => d.source.id === selectedNode.id || d.target.id === selectedNode.id);
    connectedLinks
      .transition()
      .duration(200)
      .style('stroke-opacity', 1)
      .style('stroke-width', d => Math.max(1, d.width) * 1.5);
  }

  
  const stopThresholdWatch = watch(threshold, () => {
    if (!expandedLinkKey.value) return;
    
    const expandedLink = graph.links.find(l => {
      const key = `${l.source.label}#${l.source.stage}|${l.target.label}#${l.target.stage}`;
      return key === expandedLinkKey.value;
    });
    if (expandedLink) {
      renderExpansionDetail(expandedLink, g);
    }
  });

  
  const containerNode = chartContainer.node();
  if (containerNode._hybridCleanup) containerNode._hybridCleanup();
  containerNode._hybridCleanup = stopThresholdWatch;
};


function Sankey() {
  let x0 = 0, y0 = 0, x1 = 1, y1 = 1; 
  let dx = 24; 
  let dy = 8, py; 
  let id = d => d.index;
  let align = justify;
  let sort = null;
  let linkSort = null;
  let nodes = graph => graph.nodes;
  let links = graph => graph.links;
  let iterations = 6;

  function sankey() {
    const graph = { nodes: nodes.apply(null, arguments), links: links.apply(null, arguments) };
    computeNodeLinks(graph);
    computeNodeValues(graph);
    computeNodeDepths(graph);
    computeNodeHeights(graph);
    computeNodeBreadths(graph);
    computeLinkBreadths(graph);
    return graph;
  }

  
  function computeNodeLinks({ nodes, links }) {
    for (const [i, node] of nodes.entries()) {
      node.index = i;
      node.sourceLinks = [];
      node.targetLinks = [];
    }
    const nodeById = new Map(nodes.map((d, i) => [id(d, i, nodes), d]));
    for (const [i, link] of links.entries()) {
      link.index = i;
      let { source, target } = link;
      if (typeof source !== "object") source = link.source = find(nodeById, source);
      if (typeof target !== "object") target = link.target = find(nodeById, target);
      source.sourceLinks.push(link);
      target.targetLinks.push(link);
    }
    if (linkSort != null) {
      for (const { sourceLinks, targetLinks } of nodes) {
        sourceLinks.sort(linkSort);
        targetLinks.sort(linkSort);
      }
    }
  }

  function computeNodeValues({ nodes }) {
    for (const node of nodes) {
      node.value = node.fixedValue === undefined
        ? Math.max(d3.sum(node.sourceLinks, d => d.value), d3.sum(node.targetLinks, d => d.value))
        : node.fixedValue;
    }
  }

  function computeNodeDepths({ nodes }) {
    const n = nodes.length;
    let current = new Set(nodes);
    let next = new Set();
    let x = 0;
    while (current.size) {
      for (const node of current) {
        node.depth = x;
        for (const { target } of node.sourceLinks) {
          next.add(target);
        }
      }
      if (++x > n) throw new Error("circular link");
      current = next;
      next = new Set();
    }
  }

  function computeNodeHeights({ nodes }) {
    const n = nodes.length;
    let current = new Set(nodes);
    let next = new Set();
    let x = 0;
    while (current.size) {
      for (const node of current) {
        node.height = x;
        for (const { source } of node.targetLinks) {
          next.add(source);
        }
      }
      if (++x > n) throw new Error("circular link");
      current = next;
      next = new Set();
    }
  }

  function computeNodeBreadths(graph) {
    const columns = computeNodeLayers(graph);
    py = Math.min(dy, (y1 - y0) / (d3.max(columns, c => c.length) - 1));
    initializeNodeBreadths(columns);
    for (let i = 0; i < iterations; ++i) {
      const alpha = Math.pow(0.99, i);
      const beta = Math.max(1 - alpha, (i + 1) / iterations);
      relaxRightToLeft(columns, alpha, beta);
      relaxLeftToRight(columns, alpha, beta);
    }
  }

  function computeNodeLayers({ nodes }) {
    const x = d3.max(nodes, d => d.depth) + 1;
    const kx = (x1 - x0 - dx) / (x - 1);
    const columns = new Array(x);
    for (const node of nodes) {
      const i = Math.max(0, Math.min(x - 1, Math.floor(align.call(null, node, x))));
      node.layer = i;
      node.x0 = x0 + i * kx;
      node.x1 = node.x0 + dx;
      if (columns[i]) columns[i].push(node);
      else columns[i] = [node];
    }
    if (sort) for (const column of columns) column.sort(sort);
    return columns;
  }

  function initializeNodeBreadths(columns) {
    const ky = d3.min(columns, c => (y1 - y0 - (c.length - 1) * py) / d3.sum(c, d => d.value));
    for (const nodes of columns) {
      let y = y0;
      for (const node of nodes) {
        node.y0 = y;
        node.y1 = y + node.value * ky;
        y = node.y1 + py;
        for (const link of node.sourceLinks) {
          link.width = link.value * ky;
        }
      }
      y = (y1 - y + py) / (nodes.length + 1);
      for (let i = 0; i < nodes.length; ++i) {
        const node = nodes[i];
        node.y0 += y * (i + 1);
        node.y1 += y * (i + 1);
      }
    }
  }

  function relaxRightToLeft(columns, alpha, beta) {
    for (let i = columns.length - 2; i >= 0; --i) {
      const column = columns[i];
      for (const source of column) {
        let y = 0;
        let w = 0;
        for (const { target, value } of source.sourceLinks) {
          let v = value * (target.layer - source.layer);
          y += sourceTop(source, target) * v;
          w += v;
        }
        if (!(w > 0)) continue;
        let dy = (y / w - source.y0) * alpha;
        source.y0 += dy;
        source.y1 += dy;
      }
      if (sort === null) column.sort((a, b) => a.y0 - b.y0);
    }
  }

  function relaxLeftToRight(columns, alpha, beta) {
    for (let i = 1; i < columns.length; ++i) {
      const column = columns[i];
      for (const target of column) {
        let y = 0;
        let w = 0;
        for (const { source, value } of target.targetLinks) {
          let v = value * (target.layer - source.layer);
          y += targetTop(source, target) * v;
          w += v;
        }
        if (!(w > 0)) continue;
        let dy = (y / w - target.y0) * alpha;
        target.y0 += dy;
        target.y1 += dy;
      }
      if (sort === null) column.sort((a, b) => a.y0 - b.y0);
    }
  }

  function targetTop(source, target) {
    let y = source.y0 - (source.sourceLinks.length - 1) * py / 2;
    for (const { target: node, width } of source.sourceLinks) {
      if (node === target) break;
      y += width + py;
    }
    for (const { source: node, width } of target.targetLinks) {
      if (node === source) break;
      y -= width;
    }
    return y;
  }

  function sourceTop(source, target) {
    let y = target.y0 - (target.targetLinks.length - 1) * py / 2;
    for (const { source: node, width } of target.targetLinks) {
      if (node === source) break;
      y += width + py;
    }
    for (const { target: node, width } of source.sourceLinks) {
      if (node === target) break;
      y -= width;
    }
    return y;
  }

  function computeLinkBreadths({ nodes }) {
    for (const node of nodes) {
      let y0 = node.y0;
      let y1 = y0;
      for (const link of node.sourceLinks) {
        link.y0 = y0 + link.width / 2;
        y0 += link.width;
      }
      for (const link of node.targetLinks) {
        link.y1 = y1 + link.width / 2;
        y1 += link.width;
      }
    }
  }

  function find(nodeById, id) {
    const node = nodeById.get(id);
    if (!node) throw new Error("missing: " + id);
    return node;
  }

  
  sankey.nodeId = function(_) {
    return arguments.length ? (id = typeof _ === "function" ? _ : () => _, sankey) : id;
  };

  sankey.nodeWidth = function(_) {
    return arguments.length ? (dx = +_, sankey) : dx;
  };

  sankey.nodePadding = function(_) {
    return arguments.length ? (dy = py = +_, sankey) : dy;
  };

  sankey.nodeSort = function(_) {
    return arguments.length ? (sort = _, sankey) : sort;
  };

  sankey.extent = function(_) {
    return arguments.length ? (x0 = +_[0][0], x1 = +_[1][0], y0 = +_[0][1], y1 = +_[1][1], sankey) : [[x0, y0], [x1, y1]];
  };

  sankey.iterations = function(_) {
    return arguments.length ? (iterations = +_, sankey) : iterations;
  };

  return sankey;
}









const selectedNodeInfo = ref(null);
const allSecondCodes = computed(() => {
  const codes = new Set();
  Object.values(passageDatabase).forEach(passage => {
    passage.secondOrderCodes.forEach(code => code && codes.add(code));
  });
  return Array.from(codes);
});


const closeCodeBubble = () => {
  selectedNodeInfo.value = null;
};




const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};


const updateNodeClassification = (newCode) => {
  if (!selectedNodeInfo.value) return;

  
  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    passage.firstOrderCodes.forEach((code, index) => {
      if (code === selectedNodeInfo.value.label && 
          passage.stages[index] === selectedNodeInfo.value.stage) {
        passage.secondOrderCodes[index] = newCode;
      }
    });
  });

  selectedNodeInfo.value = null;
  updateSankey(); 
  updateConfView(); 
};



const updateSankey = async () => {
  await buildPathLibrary(); 
  drawSankey(); 
  drawBundledSankey();

  if (isCombined.value) {
    drawSecondSankey();
  }
};

watch(threshold, async () => {
  if (!isCombined.value) {
    await buildPathLibrary();
    drawSankey();
    drawBundledSankey();

  }
});


function horizontalSource(d) {
  return [d.source.x1, d.y0];
}

function horizontalTarget(d) {
  return [d.target.x0, d.y1];
}

function sankeyLinkHorizontal() {
  return d3.linkHorizontal()
    .source(horizontalSource)
    .target(horizontalTarget);
}


function justify(node, n) {
  return node.sourceLinks.length ? node.depth : n - 1;
}


const startResize = (e) => {
  isDraggingPanel.value = true;
  lastMouseY.value = e.clientY;
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
};

const handleResize = (e) => {
  if (!isDraggingPanel.value) return;
  const dy = lastMouseY.value - e.clientY;
  lastMouseY.value = e.clientY;
  
  let nextHeight = panelHeight.value + dy;
  const viewportHeight = window.innerHeight;
  
  
  if (nextHeight > viewportHeight) nextHeight = viewportHeight;
  if (nextHeight < 0) nextHeight = 0;
  
  panelHeight.value = nextHeight;
};

const stopResize = () => {
  isDraggingPanel.value = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  const viewportHeight = window.innerHeight;
  
  
  if (panelHeight.value < viewportHeight * 0.2) {
    panelHeight.value = 0;
    showSankeyDiagram.value = false;
  } else if (panelHeight.value > viewportHeight * 0.9) {
    panelHeight.value = viewportHeight;
  }
  
  updateSankey(); 
};


const showSankey = async () => {
  showSankeyDiagram.value = !showSankeyDiagram.value;
  if (showSankeyDiagram.value) {
    if (panelHeight.value < 100) panelHeight.value = 700; 
    nextTick(() => {
      updateSankey();
    });
  }
};













watch([includeUnclassified, isCombined], async () => {
  await updateSankey();
});

const combineStages = () => {
  isCombined.value = true; 
  buildCombinedData();
};

const undoCombine = () => {
  isUndoing.value = true
  isCombined.value = false; 
  isUndoing.value = false; 
};


const exportCSV = () => {
  const csvContent = [];
  
  
  csvContent.push([
    "Source FirstOrderCode",
    "Source SecondOrderCode",
    "Source Passage Count",
    "Source Passages",
    "Link Value",
    "Target FirstOrderCode",
    "Target SecondOrderCode",
    "Target Passage Count",
    "Target Passages"
  ].join(","));

  
  const visiblePaths = Object.entries(pathLibrary).filter(([pathKey, value]) => {
    const [sourceId, targetId] = pathKey.split("|");
    const [sourceCode, sourceStage] = sourceId.split("#");
    const [targetCode, targetStage] = targetId.split("#");

    const sourceSecondCode = getSecondOrderCode(sourceCode, sourceStage) || "unclassified";
    const targetSecondCode = getSecondOrderCode(targetCode, targetStage) || "unclassified";

    
    if (value < threshold.value) return false;

    
    if (!includeUnclassified.value && (sourceSecondCode === "unclassified" || targetSecondCode === "unclassified")) {
      return false;
    }

    return true;
  });

  
  visiblePaths.forEach(([pathKey, value]) => {
    const [sourceId, targetId] = pathKey.split("|");
    const [sourceCode, sourceStage] = sourceId.split("#");
    const [targetCode, targetStage] = targetId.split("#");

    
    const sourcePassages = getPassagesForCode(sourceCode, sourceStage);
    const sourceSecondCode = getSecondOrderCode(sourceCode, sourceStage) || "unclassified";
    
    
    const targetPassages = getPassagesForCode(targetCode, targetStage);
    const targetSecondCode = getSecondOrderCode(targetCode, targetStage) || "unclassified";

    
    csvContent.push([
      `"${sourceCode}"`,
      `"${sourceSecondCode}"`,
      sourcePassages.size, 
      `"${Array.from(sourcePassages).join(';')}"`, 
      value, 
      `"${targetCode}"`,
      `"${targetSecondCode}"`,
      targetPassages.size, 
      `"${Array.from(targetPassages).join(';')}"` 
    ].join(","));
  });

  
  const blob = new Blob([csvContent.join("\n")], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `sankey_export_${new Date().toISOString()}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
};


const getPassagesForCode = (code, stage) => {
  const passages = new Set();
  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    passage.firstOrderCodes.forEach((fc, idx) => {
      if (fc === code && passage.stages[idx] === stage) {
        passages.add(passageName);
      }
    });
  });
  return passages;
};

const exportSvg = () => {
  const chartConfigs = [];
  if (isCombined.value) {
    chartConfigs.push({
      selector: '#sankey-chart svg',
      filename: 'combined_linkage_diagram'
    });
  } else {
    chartConfigs.push({
      selector: '#sankey-chart svg',
      filename: 'standard_linkage_diagram'
    });
    chartConfigs.push({
      selector: '#bundled-sankey-chart svg',
      filename: 'bundled_linkage_diagram'
    });
  }

  let exportedCount = 0;
  const timestamp = new Date().toISOString();

  chartConfigs.forEach(config => {
    const svgElement = document.querySelector(config.selector);
    
    if (svgElement && (config.condition === undefined || config.condition)) {
      
      const svgClone = svgElement.cloneNode(true);
      const serializer = new XMLSerializer();
      let svgString = serializer.serializeToString(svgClone);
      
      
      svgString = '<?xml version="1.0" standalone="no"?>\n' +
                 '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n' +
                 svgString;

      
      const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${config.filename}_${timestamp}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      exportedCount++;
    }
  });

  if (exportedCount === 0) {
    alert('No SVG content available to export');
  } else {
    console.log(`Exported ${exportedCount} SVG files`);
  }
};


const showDeleteConfirm = (pocketName, passageName) => {
  deleteTarget.value = { pocketName, passageName };
  deleteScope.value = 'single';
  showDeleteModal.value = true;
};

const cancelDelete = () => {
  showDeleteModal.value = false;
  deleteTarget.value = { pocketName: '', passageName: '' };
};

const confirmDelete = () => {
  const { pocketName, passageName } = deleteTarget.value;
  
  if (deleteScope.value === 'single') {
    
    const passage = passageDatabase[passageName];
    passage.secondOrderCodes = passage.secondOrderCodes.map(code => 
      code === pocketName ? null : code
    );
  } else {
    
    Object.values(passageDatabase).forEach(passage => {
      passage.secondOrderCodes = passage.secondOrderCodes.map(code => 
        code === pocketName ? null : code
      );
    });
  }
  
  showDeleteModal.value = false;
  deleteTarget.value = { pocketName: '', passageName: '' };
  updateConfView(); 
};







const uniqueSecondCodes = (passage) => {
  const codes = passage.secondOrderCodes.filter(code => code && code !== null);
  
  const counts = {};
  codes.forEach(code => {
    counts[code] = (counts[code] || 0) + 1;
  });
  
  return [...new Set(codes)].sort((a, b) => (counts[b] || 0) - (counts[a] || 0));
};

const originalApplyAll = () => {
  showApplyAllModal.value = !showApplyAllModal.value;
};





const updateConfView = () => {
  const point = usePoint();
  
  point.value.groups = Object.entries(passageDatabase).map(([passage, data]) => {
    const coordinates = data.firstOrderCodes.map(() => Math.random() * 100);
    const ids = data.firstOrderCodes.map((_, idx) => Date.now() + idx);

    return {
      title: passage,
      firstOrderCodes: data.firstOrderCodes,
      secondOrderCodes: data.secondOrderCodes,
      explanations: data.explanations,
      sentences: data.sentences,
      stages: data.stages,
      x: coordinates,
      y: coordinates.map(v => v * 0.8),
      count: data.firstOrderCodes.map(() => 1),
      id: ids
    };
  });
};


watch(passageDatabase, () => {
  if (!isEditing.value) {
    updateConfView();
  }
}, { deep: true });


const showDeletedKeywords = () => {
  showDeletedKeywordsAlert.value = true;
};

const restoreKeyword = (text, count, explanation, sentence, stage) => {
  deletedKeywords.value = deletedKeywords.value.filter(k => k.text !== text);
  processedDataRef.value.push({
    type: 'keyword',
    stage: stage,
    explanation: explanation,
    sentence: sentence,
    x: 0,
    y: 0,
    text: text,
    pocketId: null,
    count: count,
    selected: false,
  });
  reDraw();
};

const closeDeletedKeywordsAlert = () => {
  showDeletedKeywordsAlert.value = false;
};

const addPocketFromGroup = (group) => {
  const date = Date.now();
  const nodes = group.text.map((text, index) => ({
    type: 'keyword',
    stage: group.stage[index] || '',
    explanation: group.explanation[index] || '',
    sentence: group.sentence[index] || '',
    x: 0,
    y: 0,
    text: text,
    count: group.count[index] || 0,
    selected: false,
    pocketId: date,
  }));

  const newPocket = {
    type: 'pocket',
    id: date,
    x: Math.random() * 300,
    y: Math.random() * 300,
    width: 500,
    height: 300,
    title: group.title || `Pocket ${Date.now()}`,
    editing: false,
    keywords: nodes,
    showing: true,
    selected: false,
  };

  pockets.value.push(newPocket);
  pocketKeywords[newPocket.id] = newPocket.keywords;
  reDraw();
};

const addNewPocket = () => {
  
  const existingCount = pockets.value.length;
  const cols = Math.ceil(Math.sqrt(existingCount + 1));
  const col = existingCount % cols;
  const row = Math.floor(existingCount / cols);
  const cellWidth = POCKET_WIDTH + 60;
  const cellHeight = POCKET_HEIGHT + 60;
  const gridWidth = cols * cellWidth;
  const gridHeight = Math.ceil((existingCount + 1) / cols) * cellHeight;

  const newPocket = {
    type: 'pocket',
    id: Date.now(),
    x: -gridWidth / 2 + col * cellWidth + cellWidth / 2,
    y: -gridHeight / 2 + row * cellHeight + cellHeight / 2,
    width: 500,
    height: 300,
    title: `Card ${Date.now()}`,
    editing: false,
    keywords: [],
    showing: true,
    selected: false,
    explanation: ''
  };
  pockets.value.push(newPocket);
  reDraw();
};

const MergePockets = () => {
  const selectedPockets = pockets.value.filter(p => p.selected);
  if (selectedPockets.length < 2) {
    alert("Select at least two Pockets with Shift+left-click to merge!");
    return;
  }

  const newPocket = {
    type: 'pocket',
    id: Date.now(),
    x: 0,
    y: 0,
    width: 500,
    height: 300,
    title: `Merged Pocket ${Date.now()}`,
    editing: false,
    keywords: [],
    showing: true,
    selected: false,
  };

  selectedPockets.forEach(pocket => {
    if (pocketKeywords[pocket.id]) {
      newPocket.keywords.push(...pocketKeywords[pocket.id]);
    }
  });

  pockets.value.push(newPocket);
  pocketKeywords[newPocket.id] = newPocket.keywords;
  pockets.value = pockets.value.filter(p => !p.selected);
  reDraw();
};

const multiAbsorb = async () => {
  const selectedPockets = pockets.value.filter(p => p.selected);
  if (selectedPockets.length === 0) {
    alert("Select at least one Pocket first!");
    return;
  }

  showLoading.value = true;
  try {
    const allSimilarities = await Promise.all(
      selectedPockets.map(async (pocket) => {
        const response = await sendBatchData(pocket.title, processedDataRef.value.map(d => d.text));
        return { 
          pocketId: pocket.id,
          similarities: response.similarities 
        };
      })
    );

    
    const keywordsToMove = [];
    processedDataRef.value.forEach(keyword => {
      let maxSimilarity = 0;
      let targetPocketId = null;

      allSimilarities.forEach(({ pocketId, similarities }) => {
        const similarity = similarities[keyword.text] || 0;
        if (similarity > maxSimilarity && similarity > 0.30) {
          maxSimilarity = similarity;
          targetPocketId = pocketId;
        }
      });

      if (targetPocketId) {
        keywordsToMove.push({ keyword, targetPocketId });
      }
    });

    if (keywordsToMove.length > 0) {
      
      const movedTexts = new Set();
      keywordsToMove.forEach(({ keyword, targetPocketId }) => {
        if (!pocketKeywords[targetPocketId]) pocketKeywords[targetPocketId] = [];
        keyword.pocketId = targetPocketId;
        pocketKeywords[targetPocketId].push(keyword);
        movedTexts.add(keyword.text);
      });
      processedDataRef.value = processedDataRef.value.filter(k => !movedTexts.has(k.text));

      
      let animationsCompleted = 0;
      keywordsToMove.forEach(({ keyword }) => {
        fadeOutKeyword(keyword, () => {
          animationsCompleted++;
          if (animationsCompleted >= keywordsToMove.length) {
            reDraw();
          }
        });
      });
    }
  } finally {
    showLoading.value = false;
  }
};

const sendBatchData = async (pocketName, keywords) => {
  const payload = { pocketName, updatedData: keywords };
  const response = await fetch('http://127.0.0.1:5003/api/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return response.json();
};

const moveToPocket = (keyword, pocketId) => {
  processedDataRef.value = processedDataRef.value.filter(k => k.text !== keyword.text);
  if (!pocketKeywords[pocketId]) pocketKeywords[pocketId] = [];
  keyword.pocketId = pocketId;
  pocketKeywords[pocketId].push(keyword);
  reDraw();
};

const fadeOutKeyword = (keyword, callback) => {
  const textElements = d3.selectAll("text").nodes();
  const targetElement = textElements.find(node => node.textContent === keyword.text);

  if (targetElement) {
    d3.select(targetElement)
      .transition()
      .duration(800)
      .style("opacity", 0)
      .on("end", callback);
  } else {
    callback();
  }
};

watch(
  () => props.releaseCount,
  () => {
    const point = usePoint();
    const groups = point.value.groups;
    const releaseGroup = groups[props.releaseIndex];
    if (releaseGroup) {
      addPocketFromGroup(releaseGroup);
      removeGroup(props.releaseIndex);
      thumbnails.value = thumbnails.value.filter(t => t.pocketId !== releaseGroup.id);
      reDraw();
    }
  }
);

const removeGroup = (index) => {
  const point = usePoint();
  point.value.groups.splice(index, 1);
};

const POCKET_WIDTH = 330;  
const POCKET_HEIGHT = 200;

const enterEditMode = (passageName) => {
  currentPassage.value = passageName;
  isEditing.value = true;

  const currentPassageData = passageDatabase[passageName];
  processedDataRef.value = [];
  pockets.value = [];
  pocketKeywords = reactive({});

  
  const keywordCounts = {};
  Object.values(passageDatabase).forEach(passage => {
    passage.firstOrderCodes.forEach(code => {
      keywordCounts[code] = (keywordCounts[code] || 0) + 1;
    });
  });

  let mincntValue = Infinity;
  for (let keyword in keywordCounts) {
    if (keywordCounts[keyword] < mincntValue) {
      mincntValue = keywordCounts[keyword];
    }
  }
  let maxcntValue = 0;
  for (let keyword in keywordCounts) {
    if (keywordCounts[keyword] > mincntValue) {
      maxcntValue = keywordCounts[keyword];
    }
  }

  mincnt = mincntValue;
  maxcnt = maxcntValue;

  
  fontSizeScale = d3.scaleLog()  
    .domain([mincnt, maxcnt])
    .range([16, 20]);  

  const codeMap = new Map();
  currentPassageData.firstOrderCodes.forEach((code, index) => {
    const secondCode = currentPassageData.secondOrderCodes[index];
    if (secondCode) {
      if (!codeMap.has(secondCode)) {
        codeMap.set(secondCode, []);
      }
      codeMap.get(secondCode).push({
        type: 'keyword',
        text: code,
        explanation: currentPassageData.explanations[index],
        sentence: currentPassageData.sentences[index],
        stage: currentPassageData.stages[index],
        selected: false,
        pocketId: secondCode,
        count: keywordCounts[code]
      });
    } else {
      processedDataRef.value.push({
        type: 'keyword',
        text: code,
        explanation: currentPassageData.explanations[index],
        sentence: currentPassageData.sentences[index],
        stage: currentPassageData.stages[index],
        selected: false,
        pocketId: null,
        count: keywordCounts[code]
      });
    }
  });

  
  if (processedDataRef.value.length > 0) {
    const layout = cloud()
      .size([1100, 1100])
      .words(processedDataRef.value.map(d => ({
        text: d.text,
        size: 24,
        data: d
      })))
      .padding(5)
      .rotate(0)
      .fontSize(d => d.size)
      .on("end", (words) => {
        words.forEach((word, i) => {
          processedDataRef.value[i].x = word.x;
          processedDataRef.value[i].y = word.y;
        });
        nextTick(() => {
          reDraw();
        });
      });

    layout.start();
  }

  
  
  const pocketCount = codeMap.size;
  const cols = Math.ceil(Math.sqrt(pocketCount)); 
  const rows = Math.ceil(pocketCount / cols);      
  const cellWidth = POCKET_WIDTH + 60;   
  const cellHeight = POCKET_HEIGHT + 60; 
  const gridWidth = cols * cellWidth;
  const gridHeight = rows * cellHeight;
  let pocketIdx = 0;

  codeMap.forEach((keywords, secondCode) => {
    const col = pocketIdx % cols;
    const row = Math.floor(pocketIdx / cols);
    
    const px = -gridWidth / 2 + col * cellWidth + cellWidth / 2;
    const py = -gridHeight / 2 + row * cellHeight + cellHeight / 2;

    const newPocket = {
      type: 'pocket',
      id: Date.now() + Math.random(),
      x: px,
      y: py,
      width: POCKET_WIDTH,  
      height: POCKET_HEIGHT, 
      title: secondCode,
      editing: false,
      keywords: [],
      showing: true,
      selected: false,
      explanation: codeExplanations[secondCode] || '' 
    };
    pockets.value.push(newPocket);
    pocketKeywords[newPocket.id] = keywords;
    keywords.forEach(k => (k.pocketId = newPocket.id));

    
    keywords.forEach((keyword, idx) => {
      keyword.x = (Math.random() - 0.5) * (POCKET_WIDTH - 50);
      keyword.y = (Math.random() - 0.5) * (POCKET_HEIGHT - 100);
    });

    pocketIdx++;
  });

  
  if (processedDataRef.value.length === 0) {
    nextTick(() => {
      reDraw();
    });
  }
};

const reDraw = () => {
  
  if (currentSimulation) {
    currentSimulation.stop();
    currentSimulation = null;
  }

  const chartElement = d3.select("#chart");
  if (!chartElement.node()) {
    console.error('#chart element not found');
    return;
  }
  chartElement.select("*").remove();
  const updatedData = processedDataRef.value;
  const updatedPockets = pockets.value.filter(pocket => pocket.showing);
  const allData = [...updatedData, ...updatedPockets, ...thumbnails.value];

  const svg = chartElement.append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .attr("style", "max-width: 100%; height: auto;");

  const defs = svg.append("defs");
  const blurFilter = defs.append("filter")
    .attr("id", "cloudBlur")
    .append("feGaussianBlur")
    .attr("in", "SourceGraphic")
    .attr("stdDeviation", 5);

  
  defs.append("clipPath")
    .attr("id", "top-rounded-clip")
    .append("rect")
    .attr("x", -POCKET_WIDTH / 2)
    .attr("y", -POCKET_HEIGHT / 2)
    .attr("width", POCKET_WIDTH)
    .attr("height", 40)
    .attr("rx", 12)
    .attr("ry", 12);

  const g = svg.append("g");
  g.attr("transform", currentTransform);

  fontSizeScale = d3.scaleLog()
    .domain([mincnt, maxcnt])
    .range([16, 20]);  

  
  const node = g.append("g")
    .selectAll("g")
    .data(updatedData)
    .join("g")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", function (event, d) {
      if (event.shiftKey) {
        d.selected = !d.selected;
        if (d.selected) {
          d3.select(this).select("text").attr("fill", "#66BB6A");
        } else {
          d3.select(this).select("text").attr("fill", "black");
        }
      }
    });


  const text = node.append("text")
    .attr("dy", "0.35em")
    .attr("text-anchor", "middle")
    .text(d => d.text)
    .style("font-size", d => fontSizeScale(d.count) + "px")
    .style("pointer-events", "none")
    .style("cursor", "pointer")
    .style("user-select", "none")
    .attr("fill", d => d.selected ? "yellow" : "black")
    .each(function (d) {
      d.textBBox = this.getBBox();
    });

  node.append("rect")
    .attr("width", d => d.textBBox.width + 10)
    .attr("height", d => d.textBBox.height + 10)
    .attr("x", d => -d.textBBox.width / 2 - 5)
    .attr("y", d => -d.textBBox.height / 2 - 5)
    .attr("fill", "transparent")
    .style("pointer-events", "all")
    .on("mouseover", function (event, d) {
      d3.select(this.parentNode).select(".delete-cross").style("visibility", "visible");
    })
    .on("mouseout", function (event, d) {
      if (!event.relatedTarget || !d3.select(event.relatedTarget).classed("delete-cross")) {
        d3.select(this.parentNode).select(".delete-cross").style("visibility", "hidden");
      }
    });

  node.append("rect")
  .attr("class", "background-rect") 
  .attr("width", d => d.textBBox.width + 10) 
  .attr("height", d => d.textBBox.height + 10) 
  .attr("x", d => -d.textBBox.width / 2 - 5) 
  .attr("y", d => -d.textBBox.height / 2 - 5) 
  .attr("fill", "#e8f5e9") 
  .style("pointer-events", "none") 
  .lower(); 

  node.append("text")
    .attr("class", "delete-cross")
    .attr("x", d => d.textBBox.width / 2 + 5)
    .attr("y", 0)
    .text("×")
    .style("font-size", d => fontSizeScale(d.count) + "px")
    .style("fill", "red")
    .style("cursor", "pointer")
    .style("visibility", "hidden")
    .on("click", function (event, d) {
      deletedKeywords.value.push(d);
      processedDataRef.value = processedDataRef.value.filter(node => node.text !== d.text);
      reDraw();
    });

  
  const pocket = g.append("g")
    .selectAll("g")
    .data(updatedPockets)
    .join("g")
    .call(d3.drag()
      .on("start", pocketDragstarted)
      .on("drag", pocketDragged)
      .on("end", pocketDragended))
    .on("click", function (event, d) {
      if (event.shiftKey) {
        d.selected = !d.selected;
        const highlightRect = d3.select(this).select("rect.highlight-rect");
        if (d.selected) {
          highlightRect.attr("stroke", "#66BB6A")
            .attr("stroke-width", 15)
            .attr("stroke-dasharray", "")
            .attr("filter", "url(#cloudBlur)");
        } else {
          highlightRect.attr("stroke", "none")
            .attr("filter", "none");
        }
      }
    });

  pocket.append("rect")
    .attr("x", d => -POCKET_WIDTH / 2)
    .attr("y", d => -POCKET_HEIGHT / 2)
    .attr("width", POCKET_WIDTH)
    .attr("height", POCKET_HEIGHT)
    .attr("fill", "#F5FAF0")
    .attr("stroke", "none")
    .each(function (d) {
      d.rectBBox = this.getBBox();
    });

    const pocketTitle = pocket.append("path")
  .attr("d", d => {
    const x = -POCKET_WIDTH / 2;
    const y = -POCKET_HEIGHT / 2;
    const width = POCKET_WIDTH;
    const height = 40;
    const radius = 12; 
    
    
    return `
      M ${x + radius},${y}
      L ${x + width - radius},${y}
      Q ${x + width},${y} ${x + width},${y + radius}
      L ${x + width},${y + height}
      L ${x},${y + height}
      L ${x},${y + radius}
      Q ${x},${y} ${x + radius},${y}
      Z
    `;
  })
  .attr("fill", d => colorLibrary[d.title] || "#A0BF7C")
  .attr("stroke", "none")
  .on("click", function (event, d) {
    if (d.editing) return;
    d.editing = true;
    d3.select(this.parentNode).select("text").remove();

    const foreignObject = d3.select(this.parentNode)
      .append("foreignObject")
      .attr("x", -POCKET_WIDTH / 2)
      .attr("y", -POCKET_HEIGHT / 2)
      .attr("width", POCKET_WIDTH)
      .attr("height", 40);

    const input = foreignObject.append("xhtml:input")
      .attr("type", "text")
      .attr("value", d.title)
      .style("font-size", "16px")
      .style("width", "100%")
      .style("height", "100%")
      .style("border", "none")
      .style("padding", "5px 10px")
      .style("background", d.title && colorLibrary[d.title] ? colorLibrary[d.title] : "#A0BF7C")
      .style("color", "white")
      .style("font-weight", "600")
      .node();

    input.focus();
    input.select();

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        d.title = input.value;
        foreignObject.remove();
        d.editing = false;
        reDraw();
      }
    });

    input.addEventListener("blur", () => {
      d.title = input.value;
      foreignObject.remove();
      d.editing = false;
      reDraw();
    });
  });

  const highlightRect = pocket.append("rect")
    .attr("class", "highlight-rect")
    .attr("x", d => -POCKET_WIDTH / 2)
    .attr("y", d => -POCKET_HEIGHT / 2)
    .attr("width", POCKET_WIDTH)
    .attr("height", POCKET_HEIGHT)
    .attr("fill", "none")
    .attr("stroke", "none")
    .attr("stroke-dasharray", "5,5")
    .attr("rx", 12)  
    .attr("ry", 12);

  const pocketText = pocket.append("text")
    .attr("x", 0)
    .attr("y", d => -POCKET_HEIGHT / 2 + 25)
    .attr("text-anchor", "middle")
    .text(d => d.title)
    .style("font-size", "20px")
    .style("font-weight", "600")
    .style("fill", "white")
    .style("pointer-events", "none");

  const pocketIcon = pocket.append("foreignObject")
    .attr("x", d => POCKET_WIDTH / 2 - 30)
    .attr("y", d => -POCKET_HEIGHT / 2 + 5)
    .attr("width", 30)
    .attr("height", 30)
    .html(`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" style="cursor: pointer;">
             <circle cx="12" cy="12" r="8" fill="#E8F5E9" stroke="#407434" stroke-width="1"/>
             <text x="12" y="16" text-anchor="middle" font-size="10" fill="#407434">i</text>
           </svg>`)
    .on("click", function (event, d) {
      event.stopPropagation();
      toggleExplanationBubble(d);
    });

  const bubbleContainer = pocket.append("foreignObject")
    .attr("x", d => POCKET_WIDTH / 2 + 10)
    .attr("y", d => -POCKET_HEIGHT / 2 + 40)
    .attr("width", 200)
    .attr("height", 100)
    .attr("data-id", d => d.id)
    .style("visibility", "hidden")
    .html(d => `
      <div class="explanation-bubble">
        <textarea class="explanation-textarea" style="width: 100%; height: 80px; resize: none;">${
          d.explanation || ''
        }</textarea>
        <button class="save-explanation" style="margin-top: 5px;">Save</button>
      </div>
    `);

  bubbleContainer.select('.save-explanation')
    .on('click', function(event, d) {
      const textarea = d3.select(this.parentNode).select('.explanation-textarea').node();
      d.explanation = textarea.value;
      const bubble = d3.select(this.parentNode.parentNode);
      bubble.style('visibility', 'hidden');
    });

  
  if (bubbleClickHandler) {
    document.removeEventListener('click', bubbleClickHandler);
  }
  bubbleClickHandler = function(event) {
    const bubbles = d3.selectAll('foreignObject[data-id]');
    bubbles.each(function() {
      const bubble = d3.select(this);
      const rect = this.getBoundingClientRect();
      const isInside = event.clientX >= rect.left && 
                      event.clientX <= rect.right && 
                      event.clientY >= rect.top && 
                      event.clientY <= rect.bottom;
      if (!isInside) {
        const pocketId = bubble.attr('data-id');
        const textareaNode = bubble.select('.explanation-textarea').node();
        if (textareaNode) {
          const explanationText = textareaNode.value;
          const pocket = pockets.value.find(p => p.id == pocketId);
          if (pocket) {
            pocket.explanation = explanationText;
          }
        }
        bubble.style('visibility', 'hidden');
      }
    });
  };
  document.addEventListener('click', bubbleClickHandler);

  
  if (!styleInjected) {
    d3.select("head").append("style")
      .text(`
        .explanation-bubble {
          background: #E8F5E9;
          border: 1px solid #ccc;
          border-radius: 5px;
          padding: 10px;
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        .explanation-bubble textarea {
          background: #E8F5E9;
          width: 100%;
          height: 80px;
          resize: none;
        }
        .explanation-bubble button {
          margin-top: 5px;
        }
      `);
    styleInjected = true;
  }

  const toggleExplanationBubble = (d) => {
    const bubble = d3.select(`foreignObject[data-id="${d.id}"]`);
    if (!bubble.empty()) {
      if (bubble.style("visibility") === "hidden") {
        bubble.style("visibility", "visible");
      } else {
        bubble.style("visibility", "hidden");
      }
    } else {
      console.error(`Bubble for pocket ID ${d.id} not found!`);
    }
  };

  const buttons = pocket.append("g");

  buttons.append("foreignObject")
    .attr("x", d => POCKET_WIDTH / 2 - 50)
    .attr("y", d => -POCKET_HEIGHT / 2 + 7)
    .attr("width", 30)
    .attr("height", 30)
    .html(`<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
             <path fill="#E8F5E9" stroke="#407434" stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="m10.5 16l4-4l-4-4M5.4 3h13.2A2.4 2.4 0 0 1 21 5.4v13.2a2.4 2.4 0 0 1-2.4 2.4H5.4A2.4 2.4 0 0 1 3 18.6V5.4A2.4 2.4 0 0 1 5.4 3"/>
           </svg>`)
    .on("click", function (event, d) {
      const pocketName = d.title;
      const updatedNode = processedDataRef.value.map(d => d.text);
      const temppocketname = globalPocketName;
      sendData(pocketName, updatedNode);
      if (globalPocketName === temppocketname) {
        attractcondition = !attractcondition;
      } else {
        attractcondition = true;
      }
      reDraw();
    });

  
  pocket.each(function (d) {
    const keywords = pocketKeywords[d.id] || [];
    const keywordContainer = d3.select(this).append("foreignObject")
      .attr("x", -POCKET_WIDTH / 2)
      .attr("y", -POCKET_HEIGHT / 2 + 40)
      .attr("width", POCKET_WIDTH)
      .attr("height", POCKET_HEIGHT - 40)
      .append("xhtml:div")
      .style("width", "100%")
      .style("height", "100%")
      .style("overflow-y", "auto")
      .style("padding", "8px")
      .style("box-sizing", "border-box")
      .style("background", "#fff")
      .style("border-radius", "0 0 12px 12px")  
      .style("border", "2px solid gray")  
      .style("display", "flex")
      .style("flex-wrap", "wrap")
      .style("align-content", "flex-start")
      .style("gap", "4px");

    keywords.forEach(keyword => {
      const tag = keywordContainer.append("span")
        .attr("class", "code-tag")
        .style("position", "relative")
        .style("display", "inline-block")
        .style("padding", "4px 20px 4px 8px")
        .style("background", "#E8F5E9")
        .style("border-radius", "12px")
        .style("margin", "2px")
        .style("font-size", "14px")
        .style("color", "#333");

      tag.append("span")
        .text(keyword.text)
        .style("white-space", "nowrap");

      const deleteCross = tag.append("span")
        .text("×")
        .style("position", "absolute")
        .style("top", "2px")
        .style("right", "4px")
        .style("color", "red")
        .style("cursor", "pointer")
        .style("font-size", "12px")
        .on("click", () => {
          const pocketId = keyword.pocketId;
          if (pocketKeywords[pocketId]) {
            const index = pocketKeywords[pocketId].findIndex(k => k.text === keyword.text);
            if (index !== -1) {
              pocketKeywords[pocketId].splice(index, 1);
            }
          }
          processedDataRef.value.push({
            type: 'keyword',
            stage: keyword.stage,
            explanation: keyword.explanation,
            sentence: keyword.sentence,
            x: 0,
            y: 0,
            text: keyword.text,
            selected: false,
            pocketId: null,
            count: keyword.count,
            isDragging: false
          });
          reDraw();
        });
    });
  });

  
  if (attractcondition && globalSimilarities) {
    const pocketName = globalPocketName;
    const similarities = globalSimilarities;
    const pocketNode = updatedPockets.find(p => p.title === pocketName);
    if (pocketNode) {
      
      const matchedNodes = updatedData.filter(tempnode => {
        const similarity = similarities[tempnode.text];
        return similarity > 0.30;
      });

      if (matchedNodes.length > 0) {
        
        if (!pocketKeywords[pocketNode.id]) {
          pocketKeywords[pocketNode.id] = [];
        }
        matchedNodes.forEach(tempnode => {
          tempnode.pocketId = pocketNode.id;
          pocketKeywords[pocketNode.id].push(tempnode);
        });
        
        const matchedTexts = new Set(matchedNodes.map(n => n.text));
        processedDataRef.value = processedDataRef.value.filter(node => !matchedTexts.has(node.text));
        attractcondition = false;

        
        let animationsCompleted = 0;
        matchedNodes.forEach(tempnode => {
          fadeOutKeyword(tempnode, () => {
            animationsCompleted++;
            if (animationsCompleted >= matchedNodes.length) {
              reDraw(); 
            }
          });
        });
      }
    }
  }

  const thumbnail = g.append("g")
    .selectAll("g")
    .data(thumbnails.value)
    .join("g")
    .call(d3.drag()
      .on("start", thumbdragstarted)
      .on("drag", thumbdragged)
      .on("end", thumbdragended));

  thumbnail.append("rect")
    .attr("x", d => -d.width / 2)
    .attr("y", d => -d.height / 2)
    .attr("width", d => d.width)
    .attr("height", d => d.height)
    .attr("rx", 5)
    .attr("ry", 5)
    .attr("fill", "#f0f0f0")
    .attr("stroke", "#999")
    .attr("stroke-width", 2)
    .each(function (d) {
      d.rectBBox = this.getBBox();
    });

  thumbnail.append("text")
    .attr("x", 0)
    .attr("y", 5)
    .attr("text-anchor", "middle")
    .style("font-size", "12px")
    .style("fill", "#333")
    .text(d => d.title);

  thumbnail.append("circle")
    .attr("cx", d => d.width / 2 - 10)
    .attr("cy", d => d.height / 2 - 10)
    .attr("r", 10)
    .attr("fill", "orange")
    .attr("stroke", "#000")
    .style("cursor", "pointer")
    .on("click", function (event, d) {
      thumbButtonClicked(d);
    });

  const thumbButtonClicked = (thumbnail) => {
    const pocket = pockets.value.find(p => p.id === thumbnail.pocketId);
    if (pocket) {
      pocket.showing = true;
      pocket.x = thumbnail.x;
      pocket.y = thumbnail.y;
      thumbnails.value = thumbnails.value.filter(t => t.pocketId !== thumbnail.pocketId);
      const groupIndex = point.value.groups.findIndex(group => group.title === thumbnail.title);
      if (groupIndex !== -1) {
        removeGroup(groupIndex);
      }
      reDraw();
    }
  };

  function thumbdragstarted(event, d) {
    if (!event.active) simulationForce.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function thumbdragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function thumbdragended(event, d) {
    if (!event.active) simulationForce.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  
  const simulationForce = d3.forceSimulation(allData)
    .force("rectCollision", rectCollision)
    .velocityDecay(0.8)
    .alphaDecay(0.01)
    .alphaMin(0.005);
  currentSimulation = simulationForce;

  function rectCollision() {
    let nodes = simulationForce.nodes();
    for (let i = 0; i < nodes.length; i++) {
      if (nodes[i].isDragging) continue;
      
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[j].isDragging) continue;
        
        const a = nodes[i];
        const b = nodes[j];
        const aBBox = a.type === 'pocket' || a.type === 'thumbnail' ? a.rectBBox : a.textBBox;
        const bBBox = b.type === 'pocket' || b.type === 'thumbnail' ? b.rectBBox : b.textBBox;

        if (aBBox && bBBox) {
          const buffer = 0;
          const aLeft = a.x + aBBox.x;
          const aRight = aLeft + aBBox.width;
          const aTop = a.y + aBBox.y;
          const aBottom = aTop + aBBox.height;

          const bLeft = b.x + bBBox.x;
          const bRight = bLeft + bBBox.width;
          const bTop = b.y + bBBox.y;
          const bBottom = bTop + bBBox.height;

          const overlapX = (aRight + buffer > bLeft) && (aLeft - buffer < bRight);
          const overlapY = (aBottom + buffer > bTop) && (aTop - buffer < bBottom);

          if (overlapX && overlapY) {
            const dx = a.x - b.x || 1e-6;
            const dy = a.y - b.y || 1e-6;
            const overlapXDist = Math.min(aRight - bLeft, bRight - aLeft);
            const overlapYDist = Math.min(aBottom - bTop, bBottom - aTop);

            const shiftX = overlapXDist / 2 * Math.sign(dx);
            const shiftY = overlapYDist / 2 * Math.sign(dy);

            if (overlapXDist < overlapYDist) {
              a.x += shiftX;
              b.x -= shiftX;
            } else {
              a.y += shiftY;
              b.y -= shiftY;
            }
          }
        }
      }
    }
  }

  simulationForce.on("tick", () => {
    node.attr("transform", d => `translate(${d.x},${d.y})`);
    pocket.attr("transform", d => `translate(${d.x},${d.y})`);
    thumbnail.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  function dragstarted(event) {
    simulationForce.alphaTarget(0.3).restart();
    event.subject.isDragging = true;
  }

  function dragged(event, d) {
    d.x = event.x;
    d.y = event.y;
    d.isDragging = true;
    
    const targetPocket = updatedPockets.find(p => isPointInsidePocket(p, d));
    let previewTag = d3.select("#preview-tag");
    
    if (targetPocket && !previewTag.node()) {
      const g = d3.select("svg g");
      previewTag = g.append("g")
        .attr("id", "preview-tag")
        .attr("transform", `translate(${d.x},${d.y})`)
        .attr("opacity", 0.7);
        
      previewTag.append("rect")
        .attr("width", d.textBBox.width + 10)
        .attr("height", d.textBBox.height + 10)
        .attr("x", -d.textBBox.width / 2 - 5)
        .attr("y", -d.textBBox.height / 2 - 5)
        .attr("fill", "#E8F5E9")
        .attr("rx", 5);
        
      previewTag.append("text")
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(d.text)
        .style("font-size", fontSizeScale(d.count) + "px")
        .style("fill", "#333");
    } else if (targetPocket) {
      previewTag.attr("transform", `translate(${d.x},${d.y})`);
    } else if (previewTag.node()) {
      previewTag.remove();
    }
  }

  function dragended(event, d) {
    d3.select("#preview-tag").remove();
    d.isDragging = false;
    
    const draggedNode = event.subject || d;
    if (!draggedNode) return;

    const targetPocket = updatedPockets.find(p => isPointInsidePocket(p, draggedNode));
    if (targetPocket) {
      if (draggedNode.selected) {
        const selectedNodes = processedDataRef.value.filter(node => node.selected);
        selectedNodes.forEach(node => {
          if (!pocketKeywords[targetPocket.id]) {
            pocketKeywords[targetPocket.id] = [];
          }
          const existingNodeIndex = pocketKeywords[targetPocket.id].findIndex(k => k.text === node.text);
          if (existingNodeIndex === -1) {
            node.pocketId = targetPocket.id;
            pocketKeywords[targetPocket.id].push(node);
            processedDataRef.value = processedDataRef.value.filter(n => n.text !== node.text);
          }
        });
      } else {
        if (!pocketKeywords[targetPocket.id]) {
          pocketKeywords[targetPocket.id] = [];
        }
        const existingNodeIndex = pocketKeywords[targetPocket.id].findIndex(k => k.text === draggedNode.text);
        if (existingNodeIndex === -1) {
          draggedNode.pocketId = targetPocket.id;
          pocketKeywords[targetPocket.id].push(draggedNode);
          processedDataRef.value = processedDataRef.value.filter(n => n.text !== draggedNode.text);
        }
      }
      reDraw();
    }
  }

  function pocketDragstarted(event, d) {
    simulationForce.alphaTarget(0.04).restart();
  }

  function pocketDragged(event, d) {
    simulationForce.alphaTarget(0.04).restart();
    d.x = event.x;
    d.y = event.y;
  }

  function pocketDragended(event, d) {
    d.vx = 0;
    d.vy = 0;
  }

  function isPointInsidePocket(pocket, point) {
    const pointWidth = point.textBBox ? point.textBBox.width : 0;
    const pointHeight = point.textBBox ? point.textBBox.height : 0;
    
    const pointLeft = point.x - pointWidth / 2;
    const pointRight = point.x + pointWidth / 2;
    const pointTop = point.y - pointHeight / 2;
    const pointBottom = point.y + pointHeight / 2;
    
    const pocketLeft = pocket.x - POCKET_WIDTH / 2;
    const pocketRight = pocket.x + POCKET_WIDTH / 2;
    const pocketTop = pocket.y - POCKET_HEIGHT / 2;
    const pocketBottom = pocket.y + POCKET_HEIGHT / 2;

    return (
      pointRight > pocketLeft &&
      pointLeft < pocketRight &&
      pointBottom > pocketTop &&
      pointTop < pocketBottom
    );
  }

  const zoomBehavior = d3.zoom()
    .scaleExtent([6, 6])
    .on("zoom", (event) => {
      currentTransform = event.transform;
      g.attr("transform", currentTransform);
    });

  svg.call(zoomBehavior)
    .call(zoomBehavior.transform, currentTransform)
    .on("dblclick.zoom", null);
};

const exitEditMode = () => {
  const currentData = passageDatabase[currentPassage.value];

  
  const deletedTexts = new Set(deletedKeywords.value.map(d => d.text));
  const filteredIndices = currentData.firstOrderCodes
    .map((code, index) => (deletedTexts.has(code) ? null : index))
    .filter(index => index !== null);

  currentData.firstOrderCodes = filteredIndices.map(index => currentData.firstOrderCodes[index]);
  currentData.secondOrderCodes = filteredIndices.map(index => currentData.secondOrderCodes[index]);
  currentData.explanations = filteredIndices.map(index => currentData.explanations[index]);
  currentData.sentences = filteredIndices.map(index => currentData.sentences[index]);
  currentData.stages = filteredIndices.map(index => currentData.stages[index]);

  
  currentData.secondOrderCodes = new Array(currentData.firstOrderCodes.length).fill(null);

  pockets.value.forEach(pocket => {
    const keywords = pocketKeywords[pocket.id] || [];
    keywords.forEach(keyword => {
      const index = currentData.firstOrderCodes.indexOf(keyword.text);
      if (index !== -1) {
        currentData.secondOrderCodes[index] = pocket.title;
      }
    });
    
    if (pocket.title && pocket.explanation) {
      codeExplanations[pocket.title] = pocket.explanation;
    }
  });

  
  deletedKeywords.value = [];

  isEditing.value = false;
  updateConfView();
};

const sendData = async (pocketName, updatedData) => {
  if (isSending.value) return;

  try {
    isSending.value = true;
    showLoading.value = true;

    const payload = {
      pocketName,
      updatedData,
    };

    const response = await fetch('http://127.0.0.1:5003/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('Request failed');
    }

    const data = await response.json();
    globalPocketName = data.pocketName;
    globalSimilarities = data.similarities;

    attractcondition = true;
    reDraw();
  } catch (error) {
    console.error('Request error:', error);
    alert('Request failed. Please try again later.');
  } finally {
    isSending.value = false;
    showLoading.value = false;
  }
};




const showEditPocketModal = ref(false);


const editPocketData = reactive({
  originalName: '',
  name: '',
  explanation: '',
  passageName: ''
});


const showEditModal = (secondCode, passageName) => {
  const passage = passageDatabase[passageName];
  const explanation = codeExplanations[secondCode] || '';
  
  editPocketData.originalName = secondCode;
  editPocketData.name = secondCode;
  editPocketData.explanation = explanation;
  editPocketData.passageName = passageName;
  showEditPocketModal.value = true;
};


const validateName = () => {
  if (!editPocketData.name.trim()) {
    editPocketData.name = editPocketData.originalName;
  }
};


const savePocketEdit = () => {
  const { originalName, name, explanation, passageName } = editPocketData;
  
  if (editScope.value === 'single') {
    
    const passage = passageDatabase[passageName];
    const indices = passage.secondOrderCodes
      .map((code, idx) => code === originalName ? idx : -1)
      .filter(idx => idx !== -1);
    
    indices.forEach(idx => {
      passage.secondOrderCodes[idx] = name;
    });
    
    
    codeExplanations[name] = explanation;
    if (name !== originalName && codeExplanations[originalName]) {
      delete codeExplanations[originalName];
    }
  } else {
    
    Object.entries(passageDatabase).forEach(([pName, passage]) => {
      passage.secondOrderCodes = passage.secondOrderCodes.map(code => 
        code === originalName ? name : code
      );
    });
    
    
    codeExplanations[name] = explanation;
    if (name !== originalName && codeExplanations[originalName]) {
      delete codeExplanations[originalName];
    }
  }
  
  showEditPocketModal.value = false;
};


const cancelEdit = () => {
  showEditPocketModal.value = false;
};














const dragState = reactive({
  isDragging: false,
  sourcePassage: '',
  sourcePocket: '',
  code: '',
  scrollInterval: null,
  mouseX: 0,           
  mouseY: 0,           
  hoverPocket: null    
})

const handleDragStart = (event, passageName, pocketName, code) => {
  dragState.isDragging = true
  dragState.sourcePassage = passageName
  dragState.sourcePocket = pocketName
  dragState.code = code
  dragState.mouseX = event.clientX
  dragState.mouseY = event.clientY
  event.dataTransfer.setData('text/plain', code)
}

const handleDragOver = (event, passageName, pocketName) => {
  event.preventDefault();
  dragState.mouseX = event.pageX; 
  dragState.mouseY = event.pageY;

  const container = event.currentTarget.closest('.pockets-wrapper');
  if (!container) {
    console.warn('No .pockets-wrapper found');
    return;
  }

  const rect = container.getBoundingClientRect();
  const containerLeft = rect.left + window.scrollX; 
  const containerWidth = rect.width; 
  const threshold = containerWidth * 0.3; 
  const leftEdge = containerLeft; 
  const rightEdge = containerLeft + containerWidth; 
  const x = event.pageX; 

  
  console.log('Mouse X:', x, 'Left Edge:', leftEdge, 'Left Threshold:', leftEdge + threshold, 'Right Threshold:', rightEdge - threshold, 'Right Edge:', rightEdge);

  if (x < leftEdge + threshold) {
    requestAnimationFrame(() => container.scrollLeft -= 15);
  } else if (x > rightEdge - threshold) {
    requestAnimationFrame(() => container.scrollLeft += 15);
  }

  dragState.hoverPocket = pocketName;
  updateHoverFeedback(container.querySelectorAll('.pocket-card'));
};


const handleDrop = (event, targetPassage, targetPocket) => {
  event.preventDefault()
  dragState.isDragging = false

  const finalTargetPocket = dragState.hoverPocket || targetPocket
  dragState.hoverPocket = null

  
  const sourceIndex = passageDatabase[targetPassage].firstOrderCodes.indexOf(dragState.code)
  if (sourceIndex > -1) {
    if (finalTargetPocket === 'unclassified') {
      
      passageDatabase[targetPassage].secondOrderCodes[sourceIndex] = null
    } else {
      
      passageDatabase[targetPassage].secondOrderCodes[sourceIndex] = finalTargetPocket
    }
  }

  
  const container = event.currentTarget.closest('.pockets-wrapper')
  if (container) {
    const pockets = container.querySelectorAll('.pocket-card')
    pockets.forEach(pocket => pocket.classList.remove('hover-highlight'))
  }
}

const updateHoverFeedback = (pockets) => {
  pockets.forEach(pocket => {
    const title = pocket.querySelector('.pocket-title-text')?.textContent.trim() || 'unclassified'
    if (title === dragState.hoverPocket) {
      pocket.classList.add('hover-highlight') 
    } else {
      pocket.classList.remove('hover-highlight')
    }
  })
}




















const selectedNewStage = ref('');
const editScope = ref('single');


const handleNodeDoubleClick = (d) => {
  const event = d3.event || window.event;
  const { clientX: x, clientY: y } = event;
  
  selectedNodeInfo.value = {
    label: d.label,
    x: x + 10,
    y: y -10,
    stage: d.stage,
    secondCode: getSecondOrderCode(d.label, d.stage) 
  };
  
  
  selectedNewStage.value = d.stage;
};


const confirmStageChange = async () => {
  if (!selectedNodeInfo.value || !selectedNewStage.value) return;

  const updateNodes = [];
  
  if (editScope.value === 'single') {
    
    updateNodes.push({
      code: selectedNodeInfo.value.label,
      originalStage: selectedNodeInfo.value.stage
    });
  } else {
    
    const hullNodes = findNodesInHull(
      selectedNodeInfo.value.secondCode,
      selectedNodeInfo.value.stage
    );
    updateNodes.push(...hullNodes);
  }

  
  updateNodes.forEach(({ code, originalStage }) => {
    Object.entries(passageDatabase).forEach(([passageName, passage]) => {
      passage.firstOrderCodes.forEach((c, idx) => {
        if (c === code && passage.stages[idx] === originalStage) {
          passage.stages[idx] = selectedNewStage.value;
        }
      });
    });
  });

  
  updateStageOrder();
  await updateSankey();
  updateConfView();
  selectedNodeInfo.value = null;
};


const findNodesInHull = (secondCode, stage) => {
  const nodes = [];
  Object.entries(passageDatabase).forEach(([passageName, passage]) => {
    
    passage.firstOrderCodes.forEach((code, idx) => {
      if (passage.secondOrderCodes[idx] === secondCode && 
          passage.stages[idx] === stage) {
        nodes.push({
          code,
          originalStage: stage
        });
      }
    });
  });
  console.log(nodes)
  return nodes;
};













const isCompressed = ref(false);
const currentSortMode = ref('total');
const colorScale = d3.scaleOrdinal()
  .domain(["community", "education", "family"]) 
  .range(d3.schemeCategory10)
  .unknown('#CCCCCC'); 

const isCompressing = ref(false);
const selectedTopic = ref('');
const sortByTopic = {}; 


const compressData = async () => {
  isCompressing.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  isCompressed.value = true;
  isCompressing.value = false;
  nextTick(() => {
    drawBarChart();
  });
};


const exitCompressedView = () => {
  isCompressed.value = false;
};


const chartData = computed(() => {
  return Object.entries(passageDatabase).map(([passage, data]) => {
    const counts = d3.rollup(
      data.firstOrderCodes.map((code, i) => ({
        code,
        secondCode: data.secondOrderCodes[i] || 'unclassified'
      })),
      v => v.length,
      d => d.secondCode
    );
    
    
    const topics = Array.from(counts, ([key, value]) => ({
      topic: key, 
      value,
      topCodes: getTopCodes(passage, key)
    }));
    
    return {
      passage,
      total: data.firstOrderCodes.length,
      classified: data.secondOrderCodes.filter(Boolean).length,
      ratio: data.secondOrderCodes.filter(Boolean).length / data.firstOrderCodes.length,
      topics
    };
  });
});

const globalCodeCounts = computed(() => {
  const counts = {};
  Object.values(passageDatabase).forEach(data => {
    data.firstOrderCodes.forEach(code => {
      counts[code] = (counts[code] || 0) + 1;
    });
  });
  return counts;
});



const sortModes = {
  total: (a, b) => b.total - a.total,
  classified: (a, b) => b.classified - a.classified,
  ratio: (a, b) => b.ratio - a.ratio,
  byTopic: topic => (a, b) => {
    const aVal = a.topics.find(t => t.topic === topic)?.value || 0;
    const bVal = b.topics.find(t => t.topic === topic)?.value || 0;
    return bVal - aVal;
  }
};


const getSorter = () => {
  if (currentSortMode.value === 'byTopic' && selectedTopic.value) {
    return sortModes.byTopic(selectedTopic.value);
  }
  return sortModes[currentSortMode.value];
};

const drawBarChart = () => {
  
  d3.select('#compressed-view').selectAll('*').remove();

  
  const margin = { top: 300, right: 150, bottom: 40, left: 150 }; 
  const width = 800 ; 
  const height = Math.max(500, chartData.value.length * 30) ;

  
  const svg = d3.select('#compressed-view')
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  
  const sortedData = [...chartData.value].sort(getSorter());

  
  const x = d3.scaleLinear()
    .domain([0, d3.max(sortedData, d => d.total)])
    .range([0, width-100]);

  const y = d3.scaleBand()
    .domain(sortedData.map(d => d.passage))
    .range([0, height])
    .padding(0.1);

  
  const allTopics = availableTopics.value;
  const colorScale = d3.scaleOrdinal()
    .domain(allTopics)
    .range([
      '#4E79A7', 
      '#F28E2B', 
      '#E15759', 
      '#76B7B2', 
      '#59A14F', 
      '#EDC948', 
      '#B07AA1', 
      '#FF9DA7', 
      '#9C755F', 
      '#BAB0AC'  
    ])
    .unknown('#D3D3D3'); 

  
  svg.selectAll('.bar')
    .data(sortedData)
    .join('g')
    .attr('class', 'bar')
    .attr('transform', d => `translate(0,${y(d.passage)})`)

    
    .each(function(d) {
      const barGroup = d3.select(this);

      
      const sortedTopics = [...d.topics].sort((a, b) => {
        if (currentSortMode.value === 'byTopic' && selectedTopic.value) {
          if (a.topic === selectedTopic.value) return -1;
          if (b.topic === selectedTopic.value) return 1;
        }
        if (a.topic === 'unclassified') return 1;
        if (b.topic === 'unclassified') return -1;
        return a.topic.localeCompare(b.topic);
      });

      
      let cumulative = 0;
      const topicsWithStart = sortedTopics.map(topic => {
        const start = cumulative;
        cumulative += topic.value;
        return { ...topic, start };
      });

      
      barGroup.selectAll('rect')
        .data(topicsWithStart)
        .join('rect')
        .attr('class', 'segment')
        .attr('x', topic => x(topic.start))  
        .attr('y', 0)
        .attr('width', topic => x(topic.value))  
        .attr('height', y.bandwidth())
        .attr('fill', topic => colorScale(topic.topic))
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip);
    });

  
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '12px');

  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x));

  
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 50},${0})`);

  const legendTopics = currentSortMode.value === 'byTopic' && selectedTopic.value
    ? [selectedTopic.value, ...allTopics.filter(t => t !== selectedTopic.value), 'unclassified']
    : [...allTopics, 'unclassified'];

  legend.selectAll('rect')
    .data(legendTopics)
    .join('rect')
    .attr('x', 0)
    .attr('y', (_, i) => i * 20)
    .attr('width', 15)
    .attr('height', 15)
    .attr('fill', d => colorScale(d));

  legend.selectAll('text')
    .data(legendTopics)
    .join('text')
    .attr('x', 20)
    .attr('y', (_, i) => i * 20 + 12)
    .text(d => d)
    .style('font-size', '12px');
};

const getTopCodes = (passage, topic) => {
  const codesInTopic = passageDatabase[passage].firstOrderCodes
    .filter((_, i) => {
      const secondCode = passageDatabase[passage].secondOrderCodes[i];
      return (topic === 'unclassified' && !secondCode) || secondCode === topic;
    })
    .reduce((acc, code) => {
      acc[code] = (acc[code] || 0) + 1;
      return acc;
    }, {});
  console.log(`Initial unclassified codes count: ${Object.keys(codesInTopic).length}`);

  const sortedCodes = Object.entries(codesInTopic)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  console.log(`Sorted codes length: ${sortedCodes.length}`);

  if (topic === 'unclassified' && sortedCodes.length < 10) {
    const existingCodes = new Set(sortedCodes.map(([code]) => code));
    const additionalCodes = passageDatabase[passage].firstOrderCodes
      .filter((code, i) => !passageDatabase[passage].secondOrderCodes[i] && !existingCodes.has(code))
      .reduce((acc, code) => {
        acc[code] = (acc[code] || 0) + 1;
        return acc;
      }, {});
    console.log(`Additional codes count: ${Object.keys(additionalCodes).length}`);
    
    const extraCodes = Object.entries(additionalCodes)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10 - sortedCodes.length);
    sortedCodes.push(...extraCodes);
    console.log(`Final codes length: ${sortedCodes.length}`);
  }

  return sortedCodes.reduce((acc, [code]) => {
    acc[code] = globalCodeCounts.value[code] || 0;
    return acc;
  }, {});
};

const showTooltip = (event, d) => {
  
  const tooltip = d3.select('#compressed-tooltip')
    .style('opacity', 1)
    .style('width', '320px')
    .style('height', '220px')
    .style('left', `${event.pageX + 15}px`)
    .style('top', `${event.pageY - 220}px`);

  
  tooltip.html('');

  
  const cloudContainer = tooltip.append('svg')
    .attr('class', 'word-cloud-container')
    .attr('width', 300)
    .attr('height', 200);

  
  const allTopics = availableTopics.value;
  const colorScale = d3.scaleOrdinal()
    .domain(allTopics)
    .range([
      '#4E79A7', 
      '#F28E2B', 
      '#E15759', 
      '#76B7B2', 
      '#59A14F', 
      '#EDC948', 
      '#B07AA1', 
      '#FF9DA7', 
      '#9C755F', 
      '#BAB0AC'  
    ])
    .unknown('#D3D3D3'); 

  
  const topCodes = d.topCodes;
  const words = Object.entries(topCodes).map(([text, size]) => ({
    text,
    size,
    topic: d.topic || 'unclassified' 
  }));

  
  const minSize = 10;
  const maxSize = 20;
  const maxCount = Math.max(...words.map(w => w.size), 1);
  const fontSizeScale = d3.scaleLinear()
    .domain([0, maxCount])
    .range([minSize, maxSize]);

  
  const cloudWords = words.map(word => ({
    text: word.text,
    size: fontSizeScale(word.size),
    topic: word.topic
  }));

  
  const layout = cloud()
    .size([300, 200]) 
    .words(cloudWords)
    .padding(5) 
    .rotate(0) 
    .font("Impact") 
    .fontSize(d => d.size) 
    .on("end", drawCloud); 

  
  layout.start();

  
  function drawCloud(words) {
    const group = cloudContainer.append('g')
      .attr('transform', `translate(150, 100)`); 

    group.selectAll("text")
      .data(words)
      .enter().append("text")
      .style("font-size", d => `${d.size}px`)
      .style("font-family", "Impact")
      .style("fill", d => colorScale(d.topic)) 
      .attr("text-anchor", "middle")
      .attr("transform", d => `translate(${d.x}, ${d.y})rotate(${d.rotate})`)
      .text(d => d.text);
  }
};

const hideTooltip = () => {
  d3.select('#compressed-tooltip')
    .style('opacity', 0)
    .html(''); 
};

const availableTopics = computed(() => {
  const topics = new Set();
  chartData.value.forEach(item => {
    item.topics.forEach(t => {
      if (t.topic !== 'unclassified') {
        topics.add(t.topic);
      }
    });
  });
  return Array.from(topics).sort();
});

const handleSortModeChange = () => {
  if (currentSortMode.value !== 'byTopic') {
    selectedTopic.value = '';
  }
  drawBarChart();
};










const chartRefs = ref(new Map());
const setChartRef = (name, el) => {
  if (el) {
    chartRefs.value.set(name, el);
  }
};


onBeforeUpdate(() => {
  chartRefs.value.clear();
});

const drawAllPassageCharts = () => {
  
  if (isCompressed.value || isEditing.value || umapActive.value) {
    return;
  }

  
  const allChartData = {};
  for (const passageName in passageDatabase) {
    const passage = passageDatabase[passageName];
    if (!passage || !passage.secondOrderCodes) {
      allChartData[passageName] = [];
      continue;
    }
    const counts = {};
    passage.secondOrderCodes.forEach(code => {
      const key = code || 'unclassified';
      counts[key] = (counts[key] || 0) + 1;
    });
    
    const sortedCodes = Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count); 

    allChartData[passageName] = sortedCodes;
  }
  
  
  const getColor = (secondCode) => {
    if (!secondCode || secondCode === 'unclassified') {
      return "#CCCCCC";
    }
    return colorLibrary[secondCode] || "#808080";
  };


  
  if (sortstate.value) {
    
    
    
    console.log('[LOG] Drawing with sortstate = true (standard stacked bar)');
    for (const passageName of chartRefs.value.keys()) {
      const container = chartRefs.value.get(passageName);
      const data = allChartData[passageName]; 

      if (container && data && data.length > 0) {
        d3.select(container).selectAll('*').remove();
        
        const containerHeight = 20;
        const svg = d3.select(container)
          .append('svg')
          .attr('width', container.offsetWidth) 
          .attr('height', containerHeight);

        let currentX = 0;
        data.forEach(d => {
          const barWidth = d.count * 3;
          const color = getColor(d.name);

          svg.append('rect')
            .attr('x', currentX)
            .attr('y', 0)
            .attr('width', barWidth)
            .attr('height', containerHeight)
            .attr('fill', color)
            .append('title')
            .text(`${d.name}: ${d.count}`);
          
          currentX += barWidth;
        });
        
        svg.attr('width', currentX);

      } else if (container) {
        d3.select(container).selectAll('*').remove();
      }
    }

  } else {
    
    
    
    console.log('[LOG] Drawing with sortstate = false (aligned stacked bar)');

    
    const themePassageCounts = {};
    for (const passageName in passageDatabase) {
        const passage = passageDatabase[passageName];
        if (passage && passage.secondOrderCodes) {
            const uniqueCodes = new Set(passage.secondOrderCodes.filter(c => c)); 
            uniqueCodes.forEach(code => {
                themePassageCounts[code] = (themePassageCounts[code] || 0) + 1;
            });
        }
    }
    const sortedGlobalThemes = Object.keys(themePassageCounts).sort((a, b) => themePassageCounts[b] - themePassageCounts[a]);

    
    const themeXOffsets = {};
    let currentGlobalX = 0;
    
    
    const allChartDataMaps = {};
    for(const passageName in allChartData) {
        allChartDataMaps[passageName] = new Map(allChartData[passageName].map(item => [item.name, item.count]));
    }

    sortedGlobalThemes.forEach(themeName => {
        themeXOffsets[themeName] = currentGlobalX; 

        let maxThemeWidth = 0;
        
        for (const passageName in allChartDataMaps) {
            const count = allChartDataMaps[passageName].get(themeName) || 0;
            const barWidth = count * 3;
            if (barWidth > maxThemeWidth) {
                maxThemeWidth = barWidth;
            }
        }
        currentGlobalX += maxThemeWidth; 
    });

    
    for (const passageName of chartRefs.value.keys()) {
      const container = chartRefs.value.get(passageName);
      const data = allChartData[passageName];

      if (container && data && data.length > 0) {
        d3.select(container).selectAll('*').remove();

        const containerHeight = 20;
        const svg = d3.select(container)
          .append('svg')
          .attr('width', Math.max(container.offsetWidth, currentGlobalX)) 
          .attr('height', containerHeight);

        data.forEach(d => {
          const barWidth = d.count * 3;
          const color = getColor(d.name);
          const xPos = themeXOffsets[d.name]; 

          if (xPos !== undefined) { 
            svg.append('rect')
              .attr('x', xPos)
              .attr('y', 0)
              .attr('width', barWidth)
              .attr('height', containerHeight)
              .attr('fill', color)
              .append('title')
              .text(`${d.name}: ${d.count}`);
          }
        });
      } else if (container) {
        d3.select(container).selectAll('*').remove();
      }
    }
  }
};


watch(
  [() => passageDatabase, sortstate], 
  () => {
    nextTick(drawAllPassageCharts);
  },
  { deep: true }
);


















const titleRefs = ref(new Map());
const setTitleRef = (name, el) => {
  if (el) {
    titleRefs.value.set(name, el);
  }
};


const maxTitleWidth = ref(0);


onBeforeUpdate(() => {
  titleRefs.value.clear();
});


const titleStyle = computed(() => {
  
  if (maxTitleWidth.value > 0) {
    
    return { minWidth: `${maxTitleWidth.value}px` };
  }
  return {};
});


const calculateLayout = () => {
  let maxWidth = 0;
  
  for (const titleEl of titleRefs.value.values()) {
    if (titleEl.offsetWidth > maxWidth) {
      maxWidth = titleEl.offsetWidth;
    }
  }
  
  console.log(`[Layout Calc] Found max title width: ${maxWidth}px`);
  
  
  maxTitleWidth.value = maxWidth;
};


watch(
  () => passageDatabase,
  () => {
  maxTitleWidth.value = 0;
    
    nextTick(() => {
      
      calculateLayout();
    });
  },
  { deep: true, immediate: true } 
);
















const hidepocket = () => {
  arePocketsVisible.value = !arePocketsVisible.value;
};

const changesort = () => {
  sortstate.value = !sortstate.value;
};
</script>




<style scoped>
#chart-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border: none;
  position: relative;
}

#tooltip {
  text-align: center;
  pointer-events: none;
}

.pocket-rect {
  fill: #A0BF7C;
  stroke: black;
  stroke-width: 2;
}

.pocket-title {
  fill: #A0BF7C;
  stroke: black;
  stroke-width: 1;
}

.pocket-text {
  font-size: 14px;
  pointer-events: none;
}

.keyword-container {
  display: flex;
  flex-wrap: wrap;
}

.keyword-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 30%;
  margin: 5px;
  box-sizing: border-box;
}

.toolbar-container {
  padding: 10px;
  background: #ffffff;
  border-bottom: 2px solid #000000;
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
  margin-top: 0px;
}

button {
  background: #ffffff;
  font-family: inherit;
  padding: 0.6em 1.3em;
  font-weight: 900;
  font-size: 18px;
  color: #407434;
  border: 3px solid #407434;
  border-radius: 0.4em;
  box-shadow: 0.1em 0.1em;
  transition: all 0.1s ease;
}

button:hover {
  transform: translate(-0.05em, -0.05em);
  box-shadow: 0.15em 0.15em;
}

button:active {
  transform: translate(0.05em, 0.05em);
  box-shadow: 0.05em 0.05em;
}

.trash-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.trash-list {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 100%;
}

.trash-list h3 {
  margin-bottom: 10px;
  font-size: 18px;
  color: #333;
}

.restore-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.restore-item button {
  background: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.restore-item button:hover {
  background: #0056b3;
}

text {
  transition: opacity 0.8s ease;
}

.close-button {
  margin-top: 10px;
  background: #ff4d4d;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.close-button:hover {
  background: #cc0000;
}

.explanation-bubble {
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.explanation-bubble textarea {
  width: 100%;
  height: 80px;
  resize: none;
}

.explanation-bubble button {
  margin-top: 5px;
}

.loading-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 20px 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 1000;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #A0BF7C;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  color: #407434;
  font-weight: 500;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}



.cloud-word:hover {
  transform: scale(1.1);
  opacity: 1 !important;
}

button:disabled {
  background-color: #efeeee !important;
  border-color: #b0b0b0 !important;
  color: #808080 !important;
}




.edit-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #407434;
  padding: 5px;
}

.code-cloud {
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 8px;
}

.classified-section {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.pocket-section,
.unclassified-section {
  flex: 1;
}

.pocket-item {
  margin-bottom: 15px;
}

.pocket-title {
  font-weight: bold;
  color: #407434;
  margin-bottom: 10px;
  display: block;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.keyword-tag {
  background-color: #A0BF7C;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 12px;
}

.edit-mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f5f5f5;
  margin-bottom: 0px;
}

.exit-button {
  background: none;
  border: none;
  cursor: pointer;
  color: #ff4444;
  padding: 5px;
}

.debug-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.debug-info h4 {
  margin-bottom: 10px;
  color: #333;
}

.debug-info p {
  margin: 5px 0;
  color: #666;
}



.pocket-header {
  color: white;
  padding: 12px;
  font-weight: 600;
  font-size: 16px;
}

.pocket-content {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 4px;
  max-height: 150px !important;
  overflow-y: auto !important;
  padding: 8px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 8px;
}





.code-tag,
.cloud-word {
  font-size: 14px !important;
  padding: 6px 12px;
  background: #E8F5E9 !important;
  border-radius: 16px;
  display: inline-block;
  margin: 2px;
}
.classified-container {
  margin-top: 0px;
  padding-top: 0px;
  width: 100%;
  overflow-x: auto; 
}

.pockets-wrapper {
  display: flex;
  gap: 20px;
  padding-bottom: 10px;
}

.pocket-list {
  display: flex;
  gap: 15px;
  flex-shrink: 0;
}

.cloud-wrapper {
  flex-shrink: 0;
  width: 300px;
  height: 200px;
  background: #F8FFF5;
  border-radius: 12px;
  padding: 15px;
  margin-right: 20px;
}

.word-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 10px;
}

.cloud-word {
  padding: 4px 12px;
  transition: all 0.3s;
  cursor: pointer;
  display: inline-block;
  font-size: 14px !important;
  transform: none !important;
  opacity: 1 !important;
  background: #E8F5E9;
  border-radius: 12px;
  margin: 2px;
}

.cloud-word:hover {
  transform: scale(1.1);
  opacity: 1 !important;
}


.classified-container::-webkit-scrollbar {
  height: 6px;
}

.classified-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.classified-container::-webkit-scrollbar-thumb {
  background: #A0BF7C;
  border-radius: 4px;
}

.passage-row {
  margin-bottom: -2px;
  border-top: 2px solid #c7c7c7;
  border-bottom: 2px solid #c7c7c7;
  padding: 15px;
  position: relative;
  transition: all 0.5s ease; 
}


.edit-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #407434;
  padding: 5px;
}

.pocket-card {
  width: 300px !important;
  height: 200px !important;
  background: #F5FAF0;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.pocket-header {
  background: #A0BF7C;
  color: white;
  padding: 5px 10px; 
  font-weight: 600;
  font-size: 16px;
  position: relative; 
  display: flex;
  align-items: center;
  justify-content: center; 
}

.pocket-content {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 4px;
  max-height: 150px !important;
  overflow-y: auto !important;
  padding: 8px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 8px;
}

.code-tag {
  font-size: 14px !important;
  transform: none !important;
  white-space: nowrap;
  padding: 4px 8px;
  background: #E8F5E9;
  border-radius: 12px;
}


.main-view-wrapper {
  height: calc(100% - 40px); 
}

.passage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.passage-title {
  position: relative;
  display: inline-block;
}


.underline {
  display: block;
  width: 100%;
  height: 2px;
  background-color: #A0BF7C;
  margin-top: 5px; 
}
.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 55px; 
  padding: 0.50rem; 
  width: 100%; 
  border-bottom: 1px solid #c7c7c7; 
}

.header-title {
  flex-grow: 1;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start; 
  margin-top: 0px; 
}

.btn {
  padding: 0.3rem 1rem;
  border-radius: 2px;
  cursor: pointer;
}

.btn-primary {
  background-color: #7bf479;
  color: white;
}

.btn-secondary {
  background-color: #4cae4c;
  color: white;
}

.btn-action {
  background-color: #28a745;
  color: white;
}


.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  width: 600px;
  max-height: 80vh;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.mode-toggle button {
  padding: 8px 16px;
  margin-right: 10px;
  border: 1px solid #407434;
  background: white;
  color: #407434;
}

.mode-toggle button.active {
  background: #407434;
  color: white;
}

.start-button {
  background: #A0BF7C;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
}

.passage-tree {
  overflow-y: auto;
}

.passage-node {
  font-size: 18px;
  margin-bottom: 7px;
  padding-left: -100px; 
}

.passage-checkbox {
  font-weight: bold;
  display: block;
  margin-bottom: 7px;
  margin-left: 30%; 
  text-align: left; 
}

.code-list {
  font-size: 15px;
  text-align: left;
  margin-left: 30%;
  padding-left: 50px; 
}

.processing-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255,255,255,0.9);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  z-index: 1001;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}

.sankey-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.sankey-modal-container {
  background: white;
  width: 100%;
  height:100%;
  position: relative;
  overflow: auto;
}


#sankey-chart {
  width: 100%;
  height: 600px;
}

.close-button {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0 8px;
}

.close-button:hover {
  color: #333;
}

.stage-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
}

.stage-modal-container {
  background: white;
  width: 400px;
  padding: 20px;
  border-radius: 8px;
}

.stage-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stage-list {
  max-height: 400px;
  overflow-y: auto;
}

.stage-item {
  padding: 10px;
  margin: 5px 0;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: move;
  user-select: none;
}

.stage-item:hover {
  background: #e0e0e0;
}

.btn-stage {
  background-color: #407434;
  color: white;
}

.btn-action:hover {
  background-color: #218838;
}

.slider-container {
  margin-top: 20px;
  text-align: center;
  padding: 10px;
  background:#ffffff
}

.slider-container label {
  font-weight: bold;
  margin-right: 10px;
  color: #407434;
}

.slider-container input[type="range"] {
  width: 50%;
  margin: 0 10px;
}

.slider-container span {
  color: #666;
}



.sankey-header {
  display: block;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  position: sticky;
  top: -20px;  
  background: white;
  z-index: 1;
  padding-bottom: 10px;
  height: 160px; 
}

.sankey-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.sankey-chart-container {
  width: 100%;
  height: 800px; 
  overflow: auto;
}

.export-button {
  background: #407434;
  color: white;
  border: none;
  padding: 5px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
}

.export-button:hover {
  background: #305628;
}

.checkbox-container {
  margin-top: 10px;
  text-align: center;
  background: #ffffff;
}

.checkbox-container label {
  color: #407434;
  font-weight: 500;
}

.checkbox-container input[type="checkbox"] {
  margin-right: 8px;
  vertical-align: middle;
}
.custom-input-section {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.custom-input-container {
  margin-top: 10px;

}

.custom-input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #407434;
  border-radius: 4px;
  font-size: 14px;
}
.custom-input-section {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.custom-input-container {
  margin-top: 10px;
}

.input-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.custom-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #407434;
  border-radius: 4px;
  font-size: 14px;
}

.remove-button {
  width: 24px;
  height: 24px;
  padding: 0;
  background: #008000; 
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-button:hover {
  background: #004d00; 
}

.add-button {
  background: #A0BF7C;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 8px;
}

.add-button:hover {
  background: #8aa66a;
}

.combine-button {
  background: #407434;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.combine-button:hover {
  background: #305628;
}

.undo-button {
  background: #407434;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.undo-button:hover {
  background: #305628;
}

.undo-button:disabled {
  background: #cccccc;
  color: #666666;
  cursor: not-allowed;
}


.pocket-header {
  position: relative;
  display: flex;
  justify-content: center; 
  align-items: center;
}

.pocket-title-text {
  text-align: center; 
  flex-grow: 1; 
}

.delete-pocket-btn {
  position: absolute; 
  right: 5px; 
  top: 50%; 
  transform: translateY(-50%); 
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  transition: transform 0.2s;
}

.delete-pocket-btn:hover {
  transform: translateY(-50%) scale(1.1); 
}

.edit-pocket-btn {
  position: absolute; 
  left: 5px; 
  top: 50%; 
  transform: translateY(-50%); 
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  transition: transform 0.2s;
}

.edit-pocket-btn:hover {
  transform: translateY(-50%) scale(1.1); 
}

.delete-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.delete-modal-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.delete-modal-container h3 {
  margin-bottom: 15px;
  color: #407434;
}

.delete-options {
  margin: 15px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.delete-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.confirm-btn {
  background: #ff4d4d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn:hover {
  background: #cc0000;
}

.cancel-btn {
  background: #A0BF7C;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #8aa66a;
}
.code-tag {
  cursor: pointer;
}


.code-tag {
  font-size: 14px !important;
  transform: none !important;
  white-space: nowrap;
  padding: 4px 8px;
  background: #E8F5E9;
  border-radius: 12px;
  cursor: pointer; 
}


.code-tag:hover {
  background: #D0E8D2;
}

#sankey-chart {
  width: 100%;
  height: 600px;
  overflow: hidden;
}



.node rect {
  stroke: #000;
  stroke-width: 1px;
}

.link {
  fill: none;
  stroke-opacity: 0.2;
}

.link:hover {
  stroke-opacity: 0.5;
}

.sankey-header {
  display: flex;
  flex-direction: column; 
  align-items: stretch; 
  margin-bottom: 10px;
  padding-top:20px;
  position: sticky;
  top: -20px; 
  background: white;
  z-index: 1;
  padding-bottom: 5px;
}


.sankey-header-top {
  display: flex;
  justify-content: space-between; 
  align-items: center; 
  width: 100%;
}


.sankey-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}


.slider-container {
  display: flex;
  align-items: center; 
  justify-content: center; 
  margin-top: 10px; 
  padding: 10px;
  background: #ffffff;
}


.checkbox-container {
  display: flex;
  justify-content: center; 
  margin-top: 10px; 
  padding: 10px;
  background: #ffffff;
}

.btn-icon-text {
  background: none !important;
  border: none !important;
  box-shadow: none !important;
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  color: #6c757d; 
  transition: color 0.2s;
}

.btn-icon-text:hover {
  color: #007bff; 
}

.btn-icon-text svg {
  margin-right: 8px; 
}

.btn-label {
  font-size: 0.875rem; 
  font-weight: 500;
  line-height: 1;
}


.btn-icon-text:focus {
  outline: none;
  box-shadow: none;
}

.small-gray-text {
  font-size: 0.6em; 
  color: #888; 
}


.controls-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px; 
  margin-top: 0px;
  padding: 0px;
  background: #ffffff;
}


.checkbox-container {
  text-align: center;
}


.input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 11px;
}


.green-text {
  color: #407434; 
  font-weight: 500;
}


.checkbox-container label,
.input-container label {
  margin: 0;
}


.input-container input[type="number"] {
  width: 60px;
  padding: 4px;
  border: 1px solid #407434;
  border-radius: 4px;
}


.sankey-chart-group {
  margin: 10px 0;
  padding: 20px;
  border: 2px solid #A0BF7C;
  border-radius: 12px;
  background: #F8FFF5;
  margin-top: 0px
}

.sankey-chart-group.no-border {
  border: none;
  background: transparent;
}

.sankey-chart-group.no-border .sankey-chart-container {
  border: none;
  box-shadow: none;
}

.chart-title {
  color: #407434;
  margin-bottom: 10px;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-description {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
}

.sankey-chart-container {
  width: 100%;
  height: 800px; 
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  margin-top: 10px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden; 
}



.large-text {
  font-size: 24px;
}


.merged-content {
  display: grid;
  gap: 2rem;
  padding: 1rem;
  overflow:scroll
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.code-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.8rem;
}

.code-item {
  padding: 0.6rem 1rem;
  border-radius: 4px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #ccc; 
  margin: 4px 0;
}

.code-item label {
  display: flex;         
  align-items: center;   
  gap: 8px;              
  width: 100%;           
}

.custom-input-section {
  border-top: 2px solid #eee;
  padding-top: 1.5rem;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.custom-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.add-btn {
  background: white;
  color: #407434;
  padding: 0.1rem 0.1rem; 
  font-size: 0.8rem; 
  border-radius: 2px; 
  width: 1.5rem; 
  height: 1.5rem; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: 1px solid #ccc; 
}

.remove-btn {
  padding: 0.1rem 0.1rem; 
  font-size: 0.8rem; 
  border-radius: 2px; 
  width: 1.5rem; 
  height: 1.5rem; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: 1px solid #ccc; 
  color: #666;
  &:hover {
    color: #407434;
  }
}

.select-all-btn {
  background: white;
  color: #407434;
  padding: 0.1rem 0.1rem; 
  font-size: 0.8rem; 
  border-radius: 2px; 
  width: 1.5rem; 
  height: 1.5rem; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: 1px solid #ccc; 
}



.input-tips {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  color: #666;
  font-size: 0.9em;
}

.input-group {
  display: flex;
  gap: 8px;
  flex-grow: 1;
}

.code-input {
  width: 120px;
}

.explanation-input {
  flex-grow: 1;
}

.info-icon {
  cursor: pointer;
  margin-left: 8px;
  color: #666;
  transition: color 0.2s;
}

.info-icon:hover {
  color: #407434;
}

.semantic-option {
  margin-top: 12px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}



.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
}
.input-tips {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  font-size: 0.9em;
  color: #666;
}

.input-group {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-input {
  flex: 1;
  min-width: 120px;
}

.explanation-input {
  flex: 2;
  min-width: 200px;
}

.info-icon {
  cursor: pointer;
  margin-left: 8px;
  transition: color 0.3s;
}

.info-icon:hover {
  color: #407434;
}

.explanation-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  z-index: 2000;
  max-width: 400px;
}

.modal-content h4 {
  color: #407434;
  margin-bottom: 10px;
}

.semantic-option {
  margin-top: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.semantic-option label {
  color: #407434;
  font-size: 0.9em;
}


.explanation-tooltip {
  position: fixed;
  background: white;
  color: black;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
  z-index: 9999;
  max-width: 300px;
  white-space: pre-wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: opacity 0.2s;
}

.info-icon {
  cursor: help;
  margin-left: 8px;
  display: inline-flex;
  align-items: center;
}




.dbl-code-bubble {
  position: fixed;
  background: #F5FAF0;
  border: 1px solid #A0BF7C;
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 2000;
  width: 180px;
  cursor: move;
  user-select: none;
}

.dbl-bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0px;
  padding-bottom: 0px;
  margin-top: -2px;
  padding-top: -2px;
  border-bottom: 1px solid #D0E0C0;
}

.dbl-title-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.edit-icon {
  flex-shrink: 0;
}

.dbl-title {
  font-weight: 600;
  color: #407434;
  font-size: 12px;
}

.dbl-close-btn {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  margin-left: 8px;
}

.dbl-code-options {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.dbl-code-btn {
  text-align: left;
  padding: 4px 8px;
  background: #E8F5E9;
  border: 1px solid #C0D8B0;
  border-radius: 3px;
  color: #407434;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.dbl-code-btn:hover {
  background: #D0E8D0;
}

.dbl-remove-btn {
  margin-top: 6px;
  padding: 4px 8px;
  background: #FFEBEE;
  border: 1px solid #FFCDD2;
  color: #C62828;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.dbl-remove-btn:hover {
  background: #FFCDD2;
}



.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-modal-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.edit-form label {
  display: block;
  margin: 10px 0;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
  padding: 8px;
  margin-top: 4px;
}

.edit-options {
  margin: 15px 0;
}

.edit-options label {
  display: flex;
  align-items: center;
  margin: 8px 0;
}

.edit-options input {
  width: auto;
  margin-right: 8px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.confirm2-btn {
  background: #407434;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel2-btn {
  background: #ccc;
  color: black;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.code-tag {
  cursor: grab;
  transition: transform 0.2s;
}

.code-tag:active {
  cursor: grabbing;
  transform: scale(1.1);
  z-index: 10;
}

.pocket-card.hover-highlight {
  border: 2px solid #407434; 
  background-color: rgba(64, 116, 52, 0.1); 
  transition: all 0.2s ease; 
}



.dbl-code-bubble {
  
  width: 320px;
}

.stage-edit-section {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.stage-select select {
  width: 100%;
  padding: 5px;
  margin: 5px 0;
}

.scope-options {
  margin: 10px 0;
}

.scope-options label {
  display: block;
  margin: 5px 0;
}

.dbl-confirm-btn {
  background: #407434;
  color: white;
  margin-top: 10px;
  width: 100%;
}


.fw-dbl-code-bubble {
  position: fixed;
  background: #F5FAF0;
  border: 1px solid #A0BF7C;
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 2000;
  width: 320px; 
  cursor: move;
  user-select: none;
  display: flex; 
  flex-direction: column; 
}

.fw-dbl-bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0px;
  padding-bottom: 0px;
  margin-top: -2px;
  padding-top: -2px;
  border-bottom: 1px solid #D0E0C0;
}

.fw-dbl-title-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fw-edit-icon {
  flex-shrink: 0;
}

.fw-dbl-title {
  font-weight: 600;
  color: #407434;
  font-size: 12px;
}

.fw-dbl-close-btn {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  margin-left: 8px;
}

.fw-edit-container {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.fw-edit-section {
  flex: 1;
}

.fw-left-section {
  border-right: 1px solid #D0E0C0;
  padding-right: 10px;
}

.fw-right-section {
  padding-left: 10px;
}

.fw-dbl-code-options {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.fw-dbl-code-btn {
  text-align: left;
  padding: 4px 8px;
  background: #E8F5E9;
  border: 1px solid #C0D8B0;
  border-radius: 3px;
  color: #407434;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.fw-dbl-code-btn:hover {
  background: #D0E8D0;
}

.fw-dbl-remove-btn {
  margin-top: 6px;
  padding: 4px 8px;
  background: #FFEBEE;
  border: 1px solid #FFCDD2;
  color: #C62828;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.fw-dbl-remove-btn:hover {
  background: #FFCDD2;
}

.fw-stage-select select {
  width: 100%;
  padding: 5px;
  margin: 5px 0;
}

.fw-scope-options {
  margin: 10px 0;
}

.fw-scope-options label {
  display: block;
  margin: 5px 0;
}

.fw-dbl-confirm-btn {
  background: #407434;
  color: white;
  margin-top: 10px;
  width: 100%;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px
}

.fw-dbl-confirm-btn:hover {
  background: #305628;
}


.section-title {
  font-size: 14px; 
}

.scrollable-container {
  width: 100%;
  height: 80vh; 
  overflow: auto;
}


.compress-button {
  padding: 6px;
  border-radius: 4px;
  color: #888; 

  border: none; 
  cursor: pointer;
  transition: all 0.2s ease;
}

.compress-button:hover {
  background: #ccc; 
  color: #555; 
}

.compress-button svg {
  display: block;
}

.chart-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  padding: 10px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}


.overview-container.compressing .pocket-card {
  transform: translateY(-100%) scaleY(0.5);
  opacity: 0;
  transition: all 0.5s ease-out;
}

.overview-container.compressing .passage-header,
.overview-container.compressing .passage-title {
  transform: translateY(-50px);
  opacity: 0;
  transition: all 0.5s ease-out;
}


.compressed-view-container {
  padding: 20px;
  height: 100%;
}

.compressed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  padding: 10px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  z-index: 100;
}


.compressed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}


.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.sort-controls label {
  font-weight: 500;
  color: #555;
}

.sort-controls select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.topic-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 120px;
  transition: width 0.2s;
}

.topic-input:focus {
  width: 150px;
  outline: none;
  border-color: #A0BF7C;
}


.exit-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: background 0.2s;
}

.exit-button:hover {
  background: #f0f0f0;
}

.exit-button svg {
  display: block;
}

.word-cloud-container {
  overflow: hidden;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.word-cloud-container span {
  white-space: nowrap;
  color: #333;
  font-family: 'Impact', sans-serif; 
}

.passage-header {
  display: flex;
  align-items: center;
  width: 100%;
}

.passage-chart-container {
  
  

  
  flex-grow: 1;
  
  
  min-width: 0px;

  
  height: 20px;
  margin: 0 16px; 
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  flex-shrink: 1; 
}

.passage-header .edit-icon {
  flex-shrink: 0; 
}


.compress-button svg {
  transition: transform 0.3s ease; 
}

.rotate-180 {
  transform: rotate(180deg);
}


.compact-view {
  margin-bottom: -2px;
  border-top: 2px solid #c7c7c7;
  border-bottom: 2px solid #c7c7c7;
  padding-top: 5px;
  padding-bottom: 5px;
  position: relative;
}













.mode-toggle-container {
  display: inline-flex;
  align-items: center;
  gap: 12px; 
  margin-left: 16px; 
  border: 2px solid #A0BF7C ;
  padding: 4px;
  border-radius: 4px;
}



.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 28px;
  background-color: #ccc;
  cursor: pointer;
  transition: background-color 0.4s;
  vertical-align: middle; 
  border: 0; 
  outline: none; 
  box-shadow: none;
  padding: 0;
  border-radius: 28px;
}

.switch:hover {
  transform: none;
  border: 0;
  outline: none;
  box-shadow: none;
}



.thumb {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.4s;
}



.switch.active {
  background-color: #407434; 
}


.switch.active .thumb {
  transform: translateX(22px);
}


.sankey-floating-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  box-shadow: 0 -5px 25px rgba(0, 0, 0, 0.15);
  z-index: 2000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-top: 1px solid #e0e0e0;
}

.sankey-floating-panel.dragging {
  transition: none !important;
}


.panel-resize-handle {
  height: 8px;
  width: 100%;
  cursor: ns-resize;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
  transition: background 0.2s;
}

.panel-resize-handle:hover {
  background: #e9ecef;
}

.handle-bar {
  width: 40px;
  height: 4px;
  background: #dee2e6;
  border-radius: 2px;
}

.sankey-panel-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
}


.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s linear;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}





.code-name-label {
  font-size: 14px; 
}


.code-item {
  position: relative; 
  display: flex;
  align-items: center;
  padding: 8px 12px; 
  border-bottom: 1px solid #eee;
}

.info-icon {
  position: absolute; 
  top: 8px;         
  right: 12px;        
  z-index: 2;         
  cursor: pointer;
  color: #999; 
}
.info-icon:hover {
  color: #333; 
}

.code-item > label {
  display: flex;
  align-items: center;
  width: 100%; 
  padding-right: 28px; 
}

.code-name-label {
  flex-grow: 1; 
  text-align: center; 
  padding: 0 10px; 
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ratio-label {
  flex-shrink: 0; 
  color: #6c757d;
  font-size: 0.9em;
}

input[type="checkbox"] {
  flex-shrink: 0; 
  margin-right: 0px;
}
.context-menu-bubble {
  position: fixed;
  z-index: 9999;
  padding: 0;
  background: #ffffff; 
  border-radius: 4px;
  animation: contextMenuFadeIn 0.1s ease-out;
}

@keyframes contextMenuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.context-menu-btn {
  display: flex;
  align-items: center;
  background: transparent;
  border: none;
  color: #888; 
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: color 0.1s ease;
  white-space: nowrap;
  padding: 4px 8px;
}


.context-menu-btn:hover {
  background: transparent;
  color: #407434;
}



.combined-view-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  background-color: rgba(255, 255, 255, 0.95);
  border: 1px solid #A0BF7C;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  width: 220px;
  backdrop-filter: blur(4px);
  transition: opacity 0.3s;
}

.combined-view-controls:hover {
  background-color: #ffffff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.control-header {
  font-size: 0.85rem;
  font-weight: 700;
  color: #407434;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}

.control-item {
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
}

.checkbox-item {
  flex-direction: row;
  align-items: center;
}

.control-label {
  font-size: 0.8rem;
  color: #555;
  margin-bottom: 4px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-slider {
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  outline: none;
}

.mini-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #407434;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}


.umap-overlay-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

.umap-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 12px;
}

.umap-chart-area {
  flex: 1;
  position: relative;
  min-height: 400px;
}

.umap-chart-wrapper {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  padding: 8px;
}

.umap-chart-wrapper :deep(svg) {
  width: 100%;
  height: 100%;
  background: #fafdf8;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}


.final-view-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fdfdfd;
}

.final-charts-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 20px;
  background-color: #f9f9f9;
}

.final-chart-section {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.final-spacing-control input[type=range] {
  accent-color: #407434;
}

.btn.active {
  background-color: #407434;
  color: white;
  border-color: #407434;
}
.btn.active svg {
  fill: white;
}

:deep(.umap-tooltip) {
  position: absolute;
  background: rgba(46, 125, 50, 0.92);
  color: #fff;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  z-index: 100;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}


.umap-overview-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f5f9f3;
  border-bottom: 1px solid #dcedc8;
  flex-wrap: wrap;
}

.umap-overview-codes {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.umap-overview-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}

.umap-overview-item:hover {
  background: rgba(64, 116, 52, 0.08);
}

.umap-overview-item input[type="checkbox"] {
  accent-color: #407434;
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.umap-overview-swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.umap-overview-name {
  color: #333;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.umap-draw-btn {
  flex-shrink: 0;
  background: #407434 !important;
  color: #fff !important;
  border-radius: 6px;
  padding: 6px 12px !important;
  font-size: 12px;
}

.umap-draw-btn:hover {
  background: #305828 !important;
}


.umap-selection-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 280px;
  background: white;
  border: 2px solid #407434;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: visible;
}
.umap-selection-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #f0f7ec;
  border-bottom: 1px solid #d4e6cb;
  border-radius: 8px 8px 0 0;
}
.umap-selection-panel .panel-header h4 {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #407434;
}
.umap-selection-panel .close-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #407434;
  padding: 3px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}
.umap-selection-panel .close-btn:hover {
  background: #e5e7eb;
}
.umap-selection-panel .panel-body {
  padding: 8px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.umap-selection-panel .action-btn {
  padding: 7px 10px;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.action-btn.cluster-btn {
  background: #e8f3e4;
  color: #2f5d2a;
  width: 100%;
  border: 1px solid #d4e6cb;
}
.action-btn.cluster-btn:hover { background: #dcf0d4; }
.action-btn.save-btn {
  background: #407434;
  color: white;
}
.action-btn.save-btn:hover { background: #305828; }
.reclassify-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px dashed #d4e6cb;
  padding-top: 8px;
  position: relative;
}
.reclassify-section label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.umap-soc-selector {
  width: 100%;
  min-height: 30px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  box-sizing: border-box;
  cursor: pointer;
  background: white;
}
.umap-soc-selector:hover {
  border-color: #9ca3af;
}
.umap-soc-value {
  font-size: 13px;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.umap-soc-chevron {
  transition: transform 0.15s;
}
.umap-soc-chevron.rotate {
  transform: rotate(180deg);
}
.umap-soc-dropdown {
  position: absolute;
  top: calc(100% - 38px);
  left: 12px;
  right: 12px;
  max-height: 170px;
  overflow-y: auto;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  z-index: 1100;
}
.umap-soc-option {
  padding: 7px 10px;
  font-size: 13px;
  cursor: pointer;
}
.umap-soc-option:hover {
  background: #f3f4f6;
}
.umap-soc-option.active {
  background: #dcfce7;
  color: #166534;
  font-weight: 600;
}
.umap-soc-option.disabled {
  color: #9ca3af;
  cursor: default;
}
.umap-soc-input {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #d1d5db;
  border-radius: 5px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}
.umap-soc-input:focus {
  border-color: #407434;
  box-shadow: 0 0 0 2px rgba(64, 116, 52, 0.15);
}
</style>

