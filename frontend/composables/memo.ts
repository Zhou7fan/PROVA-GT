import { ref, onMounted } from 'vue';

export interface Memo {
    id: string;
    title: string;
    type: 'First-Order Code Notes' | 'Second-Order Code Notes' | 'Theoretical Memos' | 'Analytical Memos' | 'Cluster Analysis Notes';
    content: string;
    timestamp: number;
    traceData?: any[];
    clusterData?: any[];
}

export const useMemos = () => {
    const memos = ref<Memo[]>([]);
    const isPanelOpen = ref(false);
    const isFullScreen = ref(false);

    const fetchMemos = async () => {
        try {
            const res = await fetch('http://localhost:5002/api/memos');
            if (res.ok) {
                memos.value = await res.json();
            }
        } catch (e) {
            console.error('Failed to fetch memos:', e);
        }
    };

    const saveMemos = async () => {
        try {
            await fetch('http://localhost:5002/api/memos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(memos.value)
            });
        } catch (e) {
            console.error('Failed to save memos:', e);
        }
    };

    const addMemo = (type: Memo['type']) => {
        const newMemo: Memo = {
            id: Date.now().toString(),
            title: 'New Memo',
            type,
            content: '',
            timestamp: Date.now()
        };
        memos.value.unshift(newMemo);
        saveMemos();
    };

    const deleteMemo = (id: string) => {
        memos.value = memos.value.filter(m => m.id !== id);
        saveMemos();
    };

    const sortMemos = () => {
        memos.value.sort((a, b) => {
            const typeOrder = {
                'First-Order Code Notes': 1,
                'Second-Order Code Notes': 2,
                'Theoretical Memos': 3,
                'Analytical Memos': 4,
                'Cluster Analysis Notes': 5
            };
            if (typeOrder[a.type] !== typeOrder[b.type]) {
                return typeOrder[a.type] - typeOrder[b.type];
            }
            return b.timestamp - a.timestamp;
        });
        saveMemos();
    };

    onMounted(() => {
        fetchMemos();
    });

    return {
        memos,
        isPanelOpen,
        isFullScreen,
        fetchMemos,
        saveMemos,
        addMemo,
        deleteMemo,
        sortMemos
    };
};
