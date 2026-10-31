
interface PassageGroup {
  title: string;          
  firstOrderCodes: string[];      
  secondOrderCodes: (string|null)[]; 
  explanations: string[];         
  sentences: string[];            
  stages: string[];               
  x: number[];                    
  y: number[];                    
  count: number[];                
  id: number[];                   
}

interface Test {
  groups: PassageGroup[];
}

export const usePoint = () => useState<Test>('people', () => ({
  groups: []
}));