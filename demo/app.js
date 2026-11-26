'use strict';
const seed = [
  { id: 'ORD-104', customer: 'Ada Okafor', item: 'Everyday canvas tote', quantity: 2, payment: 'Unpaid', shipment: 'Ready' },
  { id: 'ORD-105', customer: 'Tomi Adebayo', item: 'Studio notebook set', quantity: 1, payment: 'Paid', shipment: 'Ready' },
  { id: 'ORD-106', customer: 'Ife Bello', item: 'Enamel field mug', quantity: 3, payment: 'Paid', shipment: 'Ready' },
];
const $ = id => document.getElementById(id);
const storageKey = 'skillforge-dispatch-v1';
let selected = null;
let orders = seed.map(order => ({ ...order, activity: [] }));
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
  if (Array.isArray(saved)) {
    orders = orders.map(order => {
      const previous = saved.find(row => row.id === order.id);
      return previous ? { ...order, payment: previous.payment === 'Paid' ? 'Paid' : order.payment,
        shipment: previous.shipment === 'Shipped' ? 'Shipped' : 'Ready',
        activity: Array.isArray(previous.activity) ? previous.activity.filter(a => typeof a === 'string').slice(-10) : [] } : order;
    });
  }
} catch { /* A fresh fixture is preferable to broken stored demo state. */ }
function save() { try { localStorage.setItem(storageKey, JSON.stringify(orders)); } catch { /* In-memory use remains available. */ } }
function pill(text) {
  const tag = document.createElement('span');
  tag.className = 'pill ' + text.toLowerCase();
  tag.textContent = text;
  return tag;
}
function render() {
  $('orders').replaceChildren();
  for (const order of orders) {
    const row = document.createElement('tr');
    if (order.id === selected) row.className = 'selected';
    const identity = document.createElement('td');
    for (const [className, text] of [['order-id', order.id], ['order-customer', order.customer]]) {
      const span = document.createElement('span'); span.className = className; span.textContent = text; identity.append(span);
    }
    row.append(identity);
    for (const value of [order.payment, order.shipment]) { const cell = document.createElement('td'); cell.append(pill(value)); row.append(cell); }
    const cell = document.createElement('td'); const open = document.createElement('button');
    open.className = 'open-order'; open.textContent = '↗'; open.setAttribute('aria-label', 'Open order ' + order.id);
    open.onclick = () => { selected = order.id; render(); };
    cell.append(open); row.append(cell); $('orders').append(row);
  }
  const order = orders.find(row => row.id === selected);
  $('details').hidden = !order; $('emptyDetails').hidden = !!order;
  if (!order) return;
  $('detailHeading').textContent = 'Order ' + order.id;
  $('customer').textContent = order.customer;
  $('item').textContent = order.item;
  $('quantity').textContent = 'Qty ' + order.quantity;
  $('paymentStatus').textContent = order.payment;
  $('shipmentStatus').textContent = order.shipment;
  $('markPaid').disabled = order.payment === 'Paid';
  $('markShipped').disabled = order.shipment === 'Shipped';
  $('activity').replaceChildren();
  for (const text of order.activity.length ? order.activity : ['No changes recorded.']) {
    const p = document.createElement('p'); p.textContent = text;
    if (!order.activity.length) p.className = 'no-activity';
    $('activity').append(p);
  }
}
$('markPaid').onclick = () => {
  const order = orders.find(row => row.id === selected);
  if (!order || order.payment === 'Paid') return;
  order.payment = 'Paid'; order.activity.push('Payment recorded for ' + order.id + '.'); save(); render();
};
$('markShipped').onclick = () => {
  $('confirmCopy').textContent = 'Confirm that the parcel for ' + selected + ' has left the fulfillment desk.';
  $('confirmDialog').showModal();
};
$('cancelShipment').onclick = () => $('confirmDialog').close();
$('confirmShipment').onclick = () => {
  const order = orders.find(row => row.id === selected);
  if (order && order.shipment !== 'Shipped') {
    order.shipment = 'Shipped'; order.activity.push('Shipment confirmed for ' + order.id + '.'); save();
  }
  $('confirmDialog').close(); render();
};
$('reset').onclick = () => $('resetDialog').showModal();
$('cancelReset').onclick = () => $('resetDialog').close();
$('confirmReset').onclick = () => {
  orders = seed.map(order => ({ ...order, activity: [] })); selected = null;
  save(); $('resetDialog').close(); render();
};
render();
