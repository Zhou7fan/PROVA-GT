<template>
  <div class="main-view-wrapper" :class="attrs.class">
    
    <div class="toolbar-container">
  
  <button 
    class="btn btn-icon-text"
    @click="addNewPocket"
    v-b-tooltip.hover 
    title="Add a new pocket to organize codes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
    </svg>
    <span class="btn-label">Add Pocket</span>
  </button>

  
  <button 
    class="btn btn-icon-text"
    @click="MergePockets"
    v-b-tooltip.hover 
    title="Merge selected pockets into one"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
      <path fill="currentColor" d="M16 17v-2h-4v-2h4v-2l4 4-4 4zm-8-4v2H4v2h4v2l-4-4 4-4zM18 5H6v14h12V5zm0-2c1.1 0 2 .9 2 2v14c0 1.1-.9 2-2 2H6c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2h12z"/>
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
      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5zm4 4h-2v-2h2v2zm0-4h-2V7h2v5z"/>
    </svg>
    <span class="btn-label">Absorb</span>
  </button>
</div>
    <div id="chart-container" class="scrollable-container">
      <div id="chart"></div>
    </div>

    
    <div v-if="showLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">Computing similarity...</div>
    </div>

    
    <DeletedKeywordsAlert 
      v-if="showDeletedKeywordsAlert" 
      :deletedKeywords="deletedKeywords" 
      @restore-keyword="restoreKeyword"
      @close="closeDeletedKeywordsAlert"
    />
  </div>
</template>

 

<script setup>
import { onMounted, ref, watch, reactive, nextTick } from 'vue';
import * as d3 from 'd3';
import {usePointall } from '@/composables/state_2.ts';
import { defineProps, useAttrs } from 'vue';
import DeletedKeywordsAlert from '@/components/DeletedKeywordsAlert.vue';
import cloud from 'd3-cloud';

const attrs = useAttrs();
const processedDataRef = ref([]);
const pockets = ref([]);
const thumbnails = ref([]);
let pocketKeywords = reactive({});
let currentTransform = d3.zoomIdentity;
let attractcondition = false;
let globalPocketName = null;
let globalSimilarities = null;
const deletedKeywords = ref([]);
const point = usePointall();
const showDeletedKeywordsAlert = ref(false);
const isSending = ref(false);
const showLoading = ref(false);
let mincnt = 0;
let maxcnt = 0;

const width = 8000;
const height = 8000;
const svgWidth = width;
const svgHeight = height;

const props = defineProps({
  releaseIndex: { type: Number, default: null },
  releaseCount: { type: Number, default: 0 }
});

const color = d3.scaleOrdinal(d3.schemeCategory10);
let fontSizeScale = null;
let PocketwordfontSizeScale = null;

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

const latestCsv = ref(null);

const checkForNewCsv = () => {
  fetch('http://localhost:8000/latest-csv')
    .then(res => res.json())
    .then(data => {
      if (data.filename && data.filename !== latestCsv.value) {
        latestCsv.value = data.filename;
        loadCsvData(`/${data.filename}`);
      }
    });
};

const loadCsvData = (path) => {
  d3.csv(path).then(data => {
    const uniqueCodes = new Map();
    const pocketMap = new Map();

    data.forEach(d => {
      if (!uniqueCodes.has(d.code)) {
        uniqueCodes.set(d.code, {
          type: 'keyword',
          explanation: d.explanation || '',
          sentence: d.sentence || '',
          stage: d.stage || '',
          x: 0,
          y: 0,
          text: d.code,
          pocketId: null,
          count: +d.count || 1,
          selected: false,
          secondOrderCode: d.secondOrderCode || null
        });
      }
    });

    uniqueCodes.forEach((item, code) => {
      if (item.secondOrderCode) {
        if (!pocketMap.has(item.secondOrderCode)) {
          pocketMap.set(item.secondOrderCode, []);
        }
        pocketMap.get(item.secondOrderCode).push(item);
      } else {
        processedDataRef.value.push(item);
      }
    });

    const allCounts = [...uniqueCodes.values()].map(d => d.count);
    mincnt = d3.min(allCounts);
    maxcnt = d3.max(allCounts);

    fontSizeScale = d3.scaleLinear()
      .domain([mincnt, maxcnt])
      .range([12, 30]);
    PocketwordfontSizeScale = d3.scaleLinear()
      .domain([mincnt, maxcnt])
      .range([12, 30]);

    if (processedDataRef.value.length > 0) {
      const wordCount = processedDataRef.value.length;
      const cloudWidth = Math.min(8000, Math.max(400, Math.sqrt(wordCount) * 100));
      const cloudHeight = Math.min(6000, Math.max(300, Math.sqrt(wordCount) * 80));

      const layout = cloud()
        .size([cloudWidth, cloudHeight])
        .words(processedDataRef.value.map(d => ({
          text: d.text,
          size: fontSizeScale(d.count),
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
          initializePocketsAndDraw(pocketMap);
        });

      layout.start();
    } else {
      initializePocketsAndDraw(pocketMap);
    }
  });
};

const initializePocketsAndDraw = (pocketMap) => {
  pockets.value = [];
  pocketKeywords = reactive({});

  pocketMap.forEach((keywords, secondCode) => {
    const newPocket = {
      type: 'pocket',
      id: Date.now() + Math.random(),
      x: 0,
      y: 0,
      width: 500,
      height: 300,
      title: secondCode,
      editing: false,
      keywords: [],
      showing: true,
      selected: false,
      explanation: ''
    };
    pockets.value.push(newPocket);
    pocketKeywords[newPocket.id] = keywords;
    keywords.forEach(k => {
      k.pocketId = newPocket.id;
      k.x = (Math.random() - 0.5) * (newPocket.width - 50);
      k.y = (Math.random() - 0.5) * (newPocket.height - 100);
    });
  });

  nextTick(() => {
    reDraw();
  });
};

onMounted(() => {
  setInterval(checkForNewCsv, 3000);
});

const showDeletedKeywords = () => {
  showDeletedKeywordsAlert.value = true;
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
  const newPocket = {
    type: 'pocket',
    id: Date.now(),
    x: 0,
    y: 0,
    width: 500,
    height: 300,
    title: `Pocket ${Date.now()}`,
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
        fadeOutKeyword(keyword, () => {
          moveToPocket(keyword, targetPocketId);
        });
      }
    });
  } finally {
    showLoading.value = false;
  }
};

const sendBatchData = async (pocketName, keywords) => {
  const payload = { pocketName, updatedData: keywords };
  const response = await fetch('http://127.0.0.1:5000/api/process', {
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
    const point = usePointall();
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
  const point = usePointall();
  point.value.groups.splice(index, 1);
};

const reDraw = () => {
  const chartElement = d3.select("#chart");
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
  defs.append("filter")
    .attr("id", "cloudBlur")
    .append("feGaussianBlur")
    .attr("in", "SourceGraphic")
    .attr("stdDeviation", 5);

  const g = svg.append("g");
  g.attr("transform", currentTransform);

  fontSizeScale = d3.scaleLinear()
    .domain([mincnt, maxcnt])
    .range([12, 30]);
  PocketwordfontSizeScale = d3.scaleLinear()
    .domain([mincnt, maxcnt])
    .range([12, 30]);

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

  const pocketRect = pocket.append("rect")
    .attr("x", d => -d.width / 2)
    .attr("y", d => -d.height / 2)
    .attr("width", d => d.width)
    .attr("height", d => d.height)
    .attr("fill", "white")
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .each(function (d) {
      d.rectBBox = this.getBBox();
    });

  const highlightRect = pocket.append("rect")
    .attr("class", "highlight-rect")
    .attr("x", d => -d.width / 2)
    .attr("y", d => -d.height / 2)
    .attr("width", d => d.width)
    .attr("height", d => d.height)
    .attr("fill", "none")
    .attr("stroke", "none")
    .attr("stroke-dasharray", "5,5");

  const pocketTitle = pocket.append("rect")
    .attr("x", d => -d.width / 2)
    .attr("y", d => -d.height / 2)
    .attr("width", d => d.width)
    .attr("height", 40)
    .attr("fill", "#A0BF7C")
    .attr("stroke", "black")
    .attr("stroke-width", 1)
    .on("click", function (event, d) {
      if (d.editing) return;
      d.editing = true;
      d3.select(this.parentNode).select("text").remove();

      const foreignObject = d3.select(this.parentNode)
        .append("foreignObject")
        .attr("x", -d.width / 2)
        .attr("y", -d.height / 2)
        .attr("width", d.width)
        .attr("height", 40);

      const input = foreignObject.append("xhtml:input")
        .attr("type", "text")
        .attr("value", d.title)
        .style("font-size", "30px")
        .style("width", "100%")
        .style("height", "100%")
        .style("border", "1px solid #ccc")
        .style("padding", "2px")
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

  const pocketText = pocket.append("text")
    .attr("x", -30)
    .attr("y", d => -d.height / 2 + 30)
    .attr("text-anchor", "middle")
    .text(d => d.title)
    .style("font-size", "30px")
    .style("pointer-events", "none");

  const pocketIcon = pocket.append("foreignObject")
    .attr("x", d => d.width / 2 - 90)
    .attr("y", d => -d.height / 2 + 5)
    .attr("width", 30)
    .attr("height", 30)
    .html(`<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" style="cursor: pointer;">
             <circle cx="12" cy="12" r="10" fill="none" stroke="#000" stroke-width="2"/>
             <text x="12" y="16" text-anchor="middle" font-size="12" fill="#000">i</text>
           </svg>`)
    .on("click", function (event, d) {
      event.stopPropagation();
      toggleExplanationBubble(d);
    });

  const bubbleContainer = pocket.append("foreignObject")
    .attr("x", d => d.width / 2 + 10)
    .attr("y", d => -d.height / 2 + 40)
    .attr("width", 200)
    .attr("height", 100)
    .attr("data-id", d => d.id)
    .style("visibility", "hidden")
    .html(d => `
      <div class="explanation-bubble">
        <textarea placeholder="Add explanation..." style="width: 100%; height: 80px;">${d.explanation}</textarea>
        <button style="margin-top: 5px;">Save</button>
      </div>
    `);

  document.addEventListener('click', function(event) {
    const bubbles = d3.selectAll('foreignObject[data-id]');
    bubbles.each(function() {
      const bubble = d3.select(this);
      const rect = this.getBoundingClientRect();
      const isInside = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
      if (!isInside) {
        const pocketId = bubble.attr('data-id');
        const explanationText = bubble.select('textarea').node().value;
        const pocket = pockets.value.find(p => p.id == pocketId);
        if (pocket) {
          pocket.explanation = explanationText;
        }
        bubble.style('visibility', 'hidden');
      }
    });
  });

  const bubbleStyle = d3.select("head").append("style")
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

  pocket.each(function (d) {
    const keywords = pocketKeywords[d.id] || [];
    const keywordContainer = d3.select(this).append("foreignObject")
      .attr("x", -d.width / 2 + 5)
      .attr("y", -d.height / 2 + 40)
      .attr("width", d.width - 10)
      .attr("height", d.height - 50)
      .append("xhtml:div")
      .style("display", "flex")
      .style("flex-wrap", "wrap")
      .style("font-size", "12px")
      .style("max-height", `${d.height - 30}px`)
      .style("overflow-y", "auto")
      .style("background-color", "#fff")
      .style("border", "1px solid #ccc")
      .style("border-radius", "5px")
      .style("padding", "5px")
      .style("box-sizing", "border-box");

    keywords.forEach(keyword => {
      const keywordItem = keywordContainer.append("div")
        .style("display", "flex")
        .style("justify-content", "space-between")
        .style("align-items", "center")
        .style("margin", "5px")
        .style("width", "100%")
        .style("box-sizing", "border-box");

      keywordItem.append("span")
        .text(keyword.text)
        .style("flex", "1")
        .style("font-size", PocketwordfontSizeScale(keyword.count) + "px")
        .style("color", "#333")
        .style("word-break", "break-word");

      keywordItem.append("button")
        .text("Back")
        .style("font-size", "10px")
        .style("padding", "2px 5px")
        .style("background-color", "#ff4d4d")
        .style("border", "none")
        .style("color", "#fff")
        .style("border-radius", "3px")
        .style("cursor", "pointer")
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
            count: keyword.count
          });
          reDraw();
        });
    });
  });

  const buttons = pocket.append("g");

  buttons.append("foreignObject")
    .attr("x", d => d.width / 2 - 30)
    .attr("y", d => -d.height / 2 + 5)
    .attr("width", 30)
    .attr("height", 30)
    .html(`<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24"><path fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round" stroke-miterlimit="10" stroke-width="1.5" d="M8 12h8M5.4 3h13.2A2.4 2.4 0 0 1 21 5.4v13.2a2.4 2.4 0 0 1-2.4 2.4H5.4A2.4 2.4 0 0 1 3 18.6V5.4A2.4 2.4 0 0 1 5.4 3"/></svg>`)
    .on("click", function (event, d) {
      d.showing = false;
      createThumbnail(d);
      const keywords = pocketKeywords[d.id];
      const newGroup = {
        title: d.title,
        stage: keywords.map(k => k.stage),
        explanation: keywords.map(k => k.explanation),
        sentence: keywords.map(k => k.sentence),
        x: keywords.map(k => k.x),
        y: keywords.map(k => k.y),
        text: keywords.map(k => k.text),
        count: keywords.map(k => k.count),
        id: d.id
      };
      const point = usePointall();
      point.value.groups.push(newGroup);
      reDraw();
    });

  const createThumbnail = (pocket) => {
    const thumbnail = {
      type: 'thumbnail',
      x: pocket.x,
      y: pocket.y,
      width: 100,
      height: 60,
      title: pocket.title,
      pocketId: pocket.id,
    };
    thumbnails.value.push(thumbnail);
    pocket.showing = false;
  };

  buttons.append("foreignObject")
    .attr("x", d => d.width / 2 - 60)
    .attr("y", d => -d.height / 2 + 5)
    .attr("width", 30)
    .attr("height", 30)
    .html(`<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24"><path fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m10.5 16l4-4l-4-4M5.4 3h13.2A2.4 2.4 0 0 1 21 5.4v13.2a2.4 2.4 0 0 1-2.4 2.4H5.4A2.4 2.4 0 0 1 3 18.6V5.4A2.4 2.4 0 0 1 5.4 3"/></svg>`)
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

  if (attractcondition && globalSimilarities) {
    const pocketName = globalPocketName;
    const similarities = globalSimilarities;
    const pocketNode = updatedPockets.find(p => p.title === pocketName);
    if (pocketNode) {
      updatedData.forEach(tempnode => {
        const similarity = similarities[tempnode.text];
        if (similarity && similarity > 0.30) {
          fadeOutKeyword(tempnode, () => {
            tempnode.pocketId = pocketNode.id;
            processedDataRef.value = processedDataRef.value.filter(node => node.text !== tempnode.text);
            if (!pocketKeywords[pocketNode.id]) {
              pocketKeywords[pocketNode.id] = [];
            }
            pocketKeywords[pocketNode.id].push(tempnode);
            attractcondition = false;
            reDraw();
          });
        }
      });
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
      const groupIndex = point.value.groups.findIndex(g => g.title === thumbnail.title);
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

  function rectCollision() {
    let nodes = simulationForce.nodes();
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const aBBox = a.type === 'pocket' || a.type === 'thumbnail' ? a.rectBBox : a.textBBox;
        const bBBox = b.type === 'pocket' || b.type === 'thumbnail' ? b.rectBBox : b.textBBox;

        if (aBBox && bBBox) {
          const buffer = 5;
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
            const dx = (a.x - b.x) || 1e-6;
            const dy = (a.y - b.y) || 1e-6;
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

    allData.forEach(d => {
      let bbox;
      if (d.type === 'pocket' || d.type === 'thumbnail') {
        bbox = { width: d.width, height: d.height };
      } else if (d.type === 'keyword') {
        bbox = d.textBBox;
      } else {
        return;
      }

      const halfWidth = bbox.width / 2;
      const halfHeight = bbox.height / 2;

      if (d.x - halfWidth < -svgWidth / 2) {
        d.x = -svgWidth / 2 + halfWidth;
        d.vx = -d.vx;
      }
      if (d.x + halfWidth > svgWidth / 2) {
        d.x = svgWidth / 2 - halfWidth;
        d.vx = -d.vx;
      }
      if (d.y - halfHeight < -svgHeight / 2) {
        d.y = -svgHeight / 2 + halfHeight;
        d.vy = -d.vy;
      }
      if (d.y + halfHeight > svgHeight / 2) {
        d.y = svgHeight / 2 - halfHeight;
        d.vy = -d.vy;
      }
    });
  });

  function dragstarted(event) {
    simulationForce.alphaTarget(0.3).restart();
  }

  function dragged(event, d) {
    d.x = event.x;
    d.y = event.y;
  }

  function dragended(event, d) {
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
    const toleranceX = Math.max(50, pointWidth / 2);
    const toleranceY = Math.max(50, pointHeight / 2);

    return (
      point.x >= pocket.x - pocket.width / 2 - toleranceX &&
      point.x <= pocket.x + pocket.width / 2 + toleranceX &&
      point.y >= pocket.y - pocket.height / 2 - toleranceY &&
      point.y <= pocket.y + pocket.height / 2 + toleranceY
    );
  }

  const zoomBehavior = d3.zoom()
    .scaleExtent([0.1, 10])
    .on("zoom", (event) => {
      currentTransform = event.transform;
      g.attr("transform", currentTransform);
    });
  svg.call(zoomBehavior).on("dblclick.zoom", null);
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

    const response = await fetch('http://127.0.0.1:5002/api/process', {
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
</script>

<style scoped>

#chart-container {
  width: 100%;
  height: 800px; 
  overflow: hidden;
  border: none;
  position: relative; 
}

#tooltip {
  text-align: center;
  pointer-events: none;
}


.move-button {
  position: absolute;
  bottom: 10px;
  left: 42%;
  transform: translateX(-50%);
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
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
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: center; 
  gap: 10px;
  margin-bottom: 15px;
}


button {
  background: #ffffff;
  font-family: inherit;
  padding: 0.6em 1.3em;
  font-weight: 900;
  font-size: 18px;
  color:#407434;
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
  to { transform: rotate(360deg); }
}


button:disabled {
  background-color: #e0e0e0 !important;
  border-color: #b0b0b0 !important;
  color: #808080 !important;
}

</style>
