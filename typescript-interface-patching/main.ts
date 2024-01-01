type MyRegExpMatchArray = Omit<RegExpMatchArray, 'index'|'indices'> & {
  index: number;
  indices?: Array<[number, number]|undefined>;
};

interface String {
  matchAll(re: RegExp): IterableIterator<MyRegExpMatchArray>;
}

let re = /foo/g;
let s = 'foobar';

let matches = s.matchAll(re);
for(let m of matches) {
  let index: number = m.index;
  let indices = m.indices!;
  let pair: [number, number]|undefined = indices[0];
  if(pair != null) {
    let [s, e] = pair;
    console.log(s, e);
  }
  console.log(index + 1);
}
