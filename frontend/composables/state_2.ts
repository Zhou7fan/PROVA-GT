interface Group {
    title: string;
    x: number[];
    y: number[];
    text: string[];
    stage: string[];
    explanation: string[];
    sentence: string[];
    count: number[];
    id: number[];
  }
  
  interface Test {
    groups: Group[];
  }
  
  export const usePointall = () => useState<Test>('people', () => ({
    groups: []
  }));