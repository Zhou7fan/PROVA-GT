import { ref } from 'vue';

export interface FinalLinkageItem {
  id: string;
  sourceCode: string;
  sourceStage: string;
  sourceSecondCode: string;
  targetCode: string;
  targetStage: string;
  targetSecondCode: string;
  value: number;
  passages: string[];
  createdAt: number;
}

const normalizeLinkKey = (
  sourceCode: string,
  sourceStage: string,
  targetCode: string,
  targetStage: string
) => `${sourceCode}#${sourceStage}|${targetCode}#${targetStage}`;

export const useFinalLinkage = () => {
  const links = ref<FinalLinkageItem[]>([]);

  const fetchFinalLinkage = async () => {
    try {
      const res = await fetch('http://localhost:5002/api/final-linkage');
      if (res.ok) {
        const data = await res.json();
        links.value = Array.isArray(data) ? data : [];
      }
    } catch (e) {
      console.error('Failed to fetch final linkage:', e);
    }
  };

  const saveFinalLinkage = async () => {
    try {
      await fetch('http://localhost:5002/api/final-linkage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(links.value)
      });
    } catch (e) {
      console.error('Failed to save final linkage:', e);
    }
  };

  const hasLink = (item: Pick<FinalLinkageItem, 'sourceCode' | 'sourceStage' | 'targetCode' | 'targetStage'>) => {
    const key = normalizeLinkKey(item.sourceCode, item.sourceStage, item.targetCode, item.targetStage);
    return links.value.some(
      l => normalizeLinkKey(l.sourceCode, l.sourceStage, l.targetCode, l.targetStage) === key
    );
  };

  const addLinks = async (incoming: FinalLinkageItem[]) => {
    let changed = false;
    incoming.forEach(item => {
      const key = normalizeLinkKey(item.sourceCode, item.sourceStage, item.targetCode, item.targetStage);
      const existingIndex = links.value.findIndex(
        l => normalizeLinkKey(l.sourceCode, l.sourceStage, l.targetCode, l.targetStage) === key
      );

      const incomingPassages = Array.isArray(item.passages)
        ? Array.from(new Set(item.passages.filter(Boolean)))
        : [];

      if (existingIndex === -1) {
        links.value.push({
          ...item,
          passages: incomingPassages,
          value: Math.max(Number(item.value || incomingPassages.length || 1), 1)
        });
        changed = true;
      } else {
        const existing = links.value[existingIndex];
        const mergedPassagesSet = new Set(existing.passages || []);
        const beforePassageCount = mergedPassagesSet.size;
        incomingPassages.forEach(p => mergedPassagesSet.add(p));
        const mergedPassages = Array.from(mergedPassagesSet);
        const addedPassageCount = mergedPassages.length - beforePassageCount;

        let mergedValue = Number(existing.value || 0);
        if (addedPassageCount > 0) {
          mergedValue += addedPassageCount;
        }
        mergedValue = Math.max(
          mergedValue,
          Number(item.value || 0),
          mergedPassages.length,
          1
        );

        const mergedSourceSecondCode =
          existing.sourceSecondCode && existing.sourceSecondCode !== 'unclassified'
            ? existing.sourceSecondCode
            : (item.sourceSecondCode || existing.sourceSecondCode || 'unclassified');

        const mergedTargetSecondCode =
          existing.targetSecondCode && existing.targetSecondCode !== 'unclassified'
            ? existing.targetSecondCode
            : (item.targetSecondCode || existing.targetSecondCode || 'unclassified');

        const hasFieldChange =
          mergedValue !== existing.value ||
          mergedPassages.length !== (existing.passages || []).length ||
          mergedSourceSecondCode !== existing.sourceSecondCode ||
          mergedTargetSecondCode !== existing.targetSecondCode;

        if (hasFieldChange) {
          links.value[existingIndex] = {
            ...existing,
            passages: mergedPassages,
            value: mergedValue,
            sourceSecondCode: mergedSourceSecondCode,
            targetSecondCode: mergedTargetSecondCode
          };
          changed = true;
        }
      }
    });
    if (changed) {
      await saveFinalLinkage();
    }
    return changed;
  };

  const clearAll = async () => {
    links.value = [];
    await saveFinalLinkage();
  };

  const deleteByLink = async (sourceCode: string, sourceStage: string, targetCode: string, targetStage: string) => {
    const targetKey = normalizeLinkKey(sourceCode, sourceStage, targetCode, targetStage);
    const before = links.value.length;
    links.value = links.value.filter(
      l => normalizeLinkKey(l.sourceCode, l.sourceStage, l.targetCode, l.targetStage) !== targetKey
    );
    if (links.value.length !== before) {
      await saveFinalLinkage();
      return true;
    }
    return false;
  };

  const deleteByFirstOrderNode = async (code: string, stage: string) => {
    const before = links.value.length;
    links.value = links.value.filter(
      l =>
        !((l.sourceCode === code && l.sourceStage === stage) ||
          (l.targetCode === code && l.targetStage === stage))
    );
    if (links.value.length !== before) {
      await saveFinalLinkage();
      return true;
    }
    return false;
  };

  const deleteBySecondOrderNode = async (secondCode: string, stage: string) => {
    const before = links.value.length;
    links.value = links.value.filter(
      l =>
        !((l.sourceSecondCode === secondCode && l.sourceStage === stage) ||
          (l.targetSecondCode === secondCode && l.targetStage === stage))
    );
    if (links.value.length !== before) {
      await saveFinalLinkage();
      return true;
    }
    return false;
  };

  const deleteBySecondOrderLink = async (
    sourceSecondCode: string,
    sourceStage: string,
    targetSecondCode: string,
    targetStage: string
  ) => {
    const before = links.value.length;
    links.value = links.value.filter(
      l =>
        !(
          l.sourceSecondCode === sourceSecondCode &&
          l.sourceStage === sourceStage &&
          l.targetSecondCode === targetSecondCode &&
          l.targetStage === targetStage
        )
    );
    if (links.value.length !== before) {
      await saveFinalLinkage();
      return true;
    }
    return false;
  };

  return {
    links,
    fetchFinalLinkage,
    saveFinalLinkage,
    addLinks,
    clearAll,
    deleteByLink,
    deleteByFirstOrderNode,
    deleteBySecondOrderNode,
    deleteBySecondOrderLink
  };
};