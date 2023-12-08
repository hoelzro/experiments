import assert from 'node:assert';

function isStringy(value: any): value is string {
  return typeof(value) == 'string';
}

function doStuffThree(value: StringOrNumber): string {
  assert(isStringy(value));

  return value;
}

console.log(doStuffThree('foo'));
console.log(doStuffThree('17'));
