"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { calculate, csv, fields } = require("../assets/quote.js");
const base = { quote:"500", percent:"10", fixed:"5", direct:"80",
  fx:"7", bank:"20", hours:"12", target:"150" };

test("all expected source fields retained", () => {
  assert.deepEqual(fields, ["quote","percent","fixed","direct","fx","bank","hours","target"]);
});
test("explicit teaching sample mathematics", () => {
  const d=calculate(base);
  assert.equal(d.platform, 50);
  assert.equal(d.netUSD,365);
  assert.equal(d.netCNY,2535);
  assert.equal(d.hourly,211.25);
  assert.equal(d.gap,61.25);
  assert.equal(d.clearsTarget,true);
});
test("never silently treat missing inputs as zero", () => {
  for (const k of fields) assert.throws(() => calculate({...base, [k]:""}),/不能为空/);
});
test("reject invalid amounts and rates", () => {
  for (const [key,value] of [["quote","0"],["hours","0"],["fx","0"],["percent","101"],["percent","-1"],["fixed","-1"],["bank","-1"],["direct","Infinity"],["target","NaN"]])
    assert.throws(()=>calculate({...base,[key]:value}),/范围/);
});
test("negative margin allowed and clearly represented", () => {
  const d=calculate({...base,quote:"1",direct:"200"});
  assert.ok(d.netUSD<0);
  assert.ok(d.netCNY<0);
  assert.equal(d.clearsTarget,false);
});
test("100 percent fee yields zero before fixed costs", () => {
  const d=calculate({...base,percent:"100",fixed:"0",direct:"0",bank:"0"});
  assert.equal(d.netUSD,0);
  assert.equal(d.netCNY,0);
});
test("numeric CSV roundtrip, header and UTF-8 BOM", () => {
  const data=csv(calculate(base));
  assert.ok(data.startsWith("\ufeffField,Value\r\n"));
  assert.match(data,/Net USD before tax,365\r\n/);
  assert.match(data,/Estimated CNY before tax,2535\r\n/);
  assert.match(data,/Teaching calculation only/);
  assert.ok(!data.includes("=HYPERLINK("));
});
test("rates are user-defined; no live FX API dependency", () => {
  const a=calculate(base), b=calculate({...base,fx:"8"});
  assert.equal(b.netUSD,a.netUSD);
  assert.equal(b.netCNY-a.netCNY,365);
});
