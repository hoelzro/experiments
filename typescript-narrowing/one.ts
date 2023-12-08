function doStuffOne(value: StringOrNumber): string {
  if(typeof(value) == 'string') {
    return value;
  } else {
    return '0' + value;
  }
}

console.log(doStuffOne('foo'));
console.log(doStuffOne(17));
console.log(doStuffOne('17'));
