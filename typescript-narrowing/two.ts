function doStuffTwo(value: StringOrNumber): string {
  if(typeof(value) == 'string') {
    return value;
  }

  return '0' + value;
}

console.log(doStuffTwo('foo'));
console.log(doStuffTwo(17));
console.log(doStuffTwo('17'));
