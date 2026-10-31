import { defineStore } from 'pinia';
import { ref } from 'vue';

export const usePointsStore = defineStore('points', {
    state: () => ({
        
        

        
        point: ref({
            x: [],
            y: [],
            text: []
        })
    }),
    
});











