const assert=require('node:assert/strict');
const puzzle=require('../prototype/logic.js').BayPuzzle;
let state=puzzle.initial();
for(const target of ['door','valve','console']) {
  const r=puzzle.interact(state,target); assert.deepEqual(r.state,state,'Locked controls must not advance progression');
}
for(const target of ['lens','console','valve','door'])state=puzzle.interact(state,target).state;
assert.equal(state.complete,true);
assert.deepEqual(puzzle.initial(),{aligned:false,calibrated:false,pressure:false,complete:false});
// Exhaustively traverse every reachable state: no interaction order may bypass prerequisites.
let queue=[puzzle.initial()],seen=new Set();
while(queue.length){const s=queue.shift(),key=JSON.stringify(s);if(seen.has(key))continue;seen.add(key);
 assert.ok(!s.complete||s.pressure);assert.ok(!s.pressure||s.calibrated);assert.ok(!s.calibrated||s.aligned);
 for(const t of ['lens','console','valve','door'])queue.push(puzzle.interact(s,t).state);
}
assert.equal(seen.size,5);console.log('Passed: locked controls, complete solution, reset, and all reachable interaction states.');
