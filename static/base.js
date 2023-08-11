/* Shivving (IE8 is not supported, but at least it won't look as awful)
/* ========================================================================== */

(function (document) {
	var
	head = document.head = document.getElementsByTagName('head')[0] || document.documentElement,
	elements = 'article aside audio bdi canvas data datalist details figcaption figure footer header hgroup mark meter nav output picture progress section summary time video x'.split(' '),
	elementsLength = elements.length,
	elementsIndex = 0,
	element;

	while (elementsIndex < elementsLength) {
		element = document.createElement(elements[++elementsIndex]);
	}

	element.innerHTML = 'x<style>' +
		'article,aside,details,figcaption,figure,footer,header,hgroup,nav,section{display:block}' +
		'audio[controls],canvas,video{display:inline-block}' +
		'[hidden],audio{display:none}' +
		'mark{background:#FF0;color:#000}' +
	'</style>';

	return head.insertBefore(element.lastChild, head.firstChild);
})(document);

/* Prototyping
/* ========================================================================== */

(function (window, ElementPrototype, ArrayPrototype, polyfill) {
	function NodeList() { [polyfill] }
	NodeList.prototype.length = ArrayPrototype.length;

	ElementPrototype.matchesSelector = ElementPrototype.matchesSelector ||
	ElementPrototype.mozMatchesSelector ||
	ElementPrototype.msMatchesSelector ||
	ElementPrototype.oMatchesSelector ||
	ElementPrototype.webkitMatchesSelector ||
	function matchesSelector(selector) {
		return ArrayPrototype.indexOf.call(this.parentNode.querySelectorAll(selector), this) > -1;
	};

	ElementPrototype.ancestorQuerySelectorAll = ElementPrototype.ancestorQuerySelectorAll ||
	ElementPrototype.mozAncestorQuerySelectorAll ||
	ElementPrototype.msAncestorQuerySelectorAll ||
	ElementPrototype.oAncestorQuerySelectorAll ||
	ElementPrototype.webkitAncestorQuerySelectorAll ||
	function ancestorQuerySelectorAll(selector) {
		for (var cite = this, newNodeList = new NodeList; cite = cite.parentElement;) {
			if (cite.matchesSelector(selector)) ArrayPrototype.push.call(newNodeList, cite);
		}

		return newNodeList;
	};

	ElementPrototype.ancestorQuerySelector = ElementPrototype.ancestorQuerySelector ||
	ElementPrototype.mozAncestorQuerySelector ||
	ElementPrototype.msAncestorQuerySelector ||
	ElementPrototype.oAncestorQuerySelector ||
	ElementPrototype.webkitAncestorQuerySelector ||
	function ancestorQuerySelector(selector) {
		return this.ancestorQuerySelectorAll(selector)[0] || null;
	};
})(this, Element.prototype, Array.prototype);

/* Helper Functions
/* ========================================================================== */

function generateTableRow() {
	var emptyColumn = document.createElement('tr');
	emptyColumn.style.height = '18px';

	emptyColumn.innerHTML = '<td style="width: 4%;"><a class="cut">-</a>1</td>' +
		'<td colspan="6"><span contenteditable>{{ form.products }}</span></td>' +
		'<td colspan="2"><span name="hsn" contenteditable>6815</span></td>' +
		'<td colspan="2"><span>{{itemform.quantity}}</span></td>' +
		'<td colspan="2"><span name="unit" contenteditable>Pcs.</span></td>' +
		'<td colspan="2"><span data-prefix>&#8377; </span><span name="rate" contenteditable>2.8</span></td>' +
		'<td colspan="2"><span name="cgst" contenteditable>6.00</span> %</td>' +
		'<td colspan="2"><span data-prefix>&#8377; </span><span contenteditable>150.00</span></td>' +
		'<td colspan="2"><span name="sgst" contenteditable>6.00</span> %</td>' +
		'<td colspan="2"><span data-prefix>&#8377; </span><span contenteditable>150.00</span></td>' +
		'<td colspan="3"><span data-prefix>&#8377; </span><span>{{itemform.total}}</span></td>';
	return emptyColumn;
}

function parseFloatHTML(element) {
	return parseFloat(element.innerHTML.replace(/[^\d\.\-]+/g, '')) || 0;
}

function parsePrice(number) {
	return number.toFixed(2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1,');
}

/* Update Number
/* ========================================================================== */

function updateNumber(e) {
	var
	activeElement = document.activeElement,
	value = parseFloat(activeElement.innerHTML),
	wasPrice = activeElement.innerHTML == parsePrice(parseFloatHTML(activeElement));

	if (!isNaN(value) && (e.keyCode == 38 || e.keyCode == 40 || e.wheelDeltaY)) {
		e.preventDefault();

		value += e.keyCode == 38 ? 1 : e.keyCode == 40 ? -1 : Math.round(e.wheelDelta * 0.025);
		value = Math.max(value, 0);

		activeElement.innerHTML = wasPrice ? parsePrice(value) : value;
	}

	updateInvoice();
}

function convertAmountToWords(amount) {
    const ones = [
      '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
      'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'
    ];
  
    const tens = [
      '', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'
    ];
  
    const rupees = 'Rupees';
    const paise = 'Paise';
  
    const amountArr = amount.split('.');
    const rupeeAmount = parseInt(amountArr[0]);
    const paiseAmount = parseInt(amountArr[1] || 0);
  
    function convertToWords(number) {
        if (number < 20) {
          return ones[number];
        } else if (number < 100) {
          return tens[Math.floor(number / 10)] + ' ' + ones[number % 10];
        } else if (number < 1000) {
          return ones[Math.floor(number / 100)] + ' Hundred ' + convertToWords(number % 100);
        } else if (number < 100000){
          return convertToWords(Math.floor(number / 1000)) + ' Thousand ' + convertToWords(number % 1000);
        } else if (number < 200000){
          return convertToWords(Math.floor(number / 100000)) + ' Lakh ' + convertToWords(number % 100000);
        } else if (number < 10000000){
          return convertToWords(Math.floor(number / 100000)) + ' Lakhs ' + convertToWords(number % 100000);
        } else if (number < 20000000){
          return convertToWords(Math.floor(number / 10000000)) + ' Crore ' + convertToWords(number % 10000000);
        } else {
          return convertToWords(Math.floor(number / 10000000)) + ' Crores ' + convertToWords(number % 10000000);
        }
      }

    const rupeeWords = rupeeAmount === 0 ? 'Zero' : convertToWords(rupeeAmount);
    const paiseWords = convertToWords(paiseAmount).trim();
  
    let result = rupeeWords + ' ' + rupees;
    if (paiseAmount > 0) {
      result += ' and ' + paiseWords + ' ' + paise;
    }
  
    return result;
  }
  

/* Update Invoice
/* ========================================================================== */

function updateInvoice() {
	var currentDate = new Date();
	var formattedDate = currentDate.toLocaleDateString() + " (" + currentDate.toLocaleTimeString() + ")";
	// Update the value of the element with id "id_date"
	if(document.getElementById("id_date")) document.getElementById("id_date").value = formattedDate;


	var total = 0, taxable = 0, tot_cgst = 0, tot_sgst = 0;
	var cells, a, i;
	var extra = parseFloat(document.getElementById('extra').firstChild.value);
	// update inventory cells
	// ======================

	for (var a = document.querySelectorAll('tbody.inventory tr'), i = 0; a[i]; ++i) {
		// get inventory row cells
		cells = a[i].querySelectorAll('span:last-child');
		// set price as cell[2] * cell[4]
		var qt = cells[2].firstChild.value;
		var price = qt * (cells[4].firstChild.value);
		price = parseFloat(price).toFixed(2);
        // taxable += price - ((100*12)/(100+12)*price)/100;
        // console.log(taxable);

		// set CGST
		var cgst = parseFloatHTML(cells[5]) * price /100;
        cells[6].innerHTML = cgst.toFixed(2);
		cgst = parseFloat(cgst).toFixed(2);
		tot_cgst += parseFloat(cgst);

		// set SGST
		var sgst = parseFloatHTML(cells[7]) * price /100;
        cells[8].innerHTML = sgst.toFixed(2);
		sgst = parseFloat(sgst).toFixed(2);
		tot_sgst += parseFloat(sgst);
		
		// add price to total
		total += parseFloat(parseFloat(price)+parseFloat(cgst)+parseFloat(sgst));
		taxable += parseFloat(price);

		// set row total
		cells[9].firstChild.value = parseFloat(parseFloat(price)+parseFloat(cgst)+parseFloat(sgst));
	}

	// update balance cells
	// ====================

	// get balance cells
	cells = document.querySelectorAll('tbody.balance td:last-child span:last-child');

	// set total
	if(!total){
		total=0;
	}
	if(!extra){
		extra=0;
	}
	total=total+extra;
	var tot_tax = parseFloat(tot_cgst)+parseFloat(tot_sgst);
    var total2 = total.toFixed(2);
	cells[0].firstChild.value = total.toFixed(2);
    var amountInWords = convertAmountToWords(total2);
    document.getElementById('total-desc').innerHTML = convertAmountToWords(total2);
	document.getElementById('taxable').innerHTML = parseFloat(taxable).toFixed(2);
	document.getElementById('tot_cgst').innerHTML = parseFloat(tot_cgst).toFixed(2);
	document.getElementById('tot_sgst').innerHTML = parseFloat(tot_sgst).toFixed(2);
	document.getElementById('tot_tax').innerHTML = tot_tax.toFixed(2);

	// update price formatting
	// =======================

	for (a = document.querySelectorAll('span[data-prefix] + span'), i = 0; a[i]; ++i) 
		if (document.activeElement != a[i]) 
			a[i].firstChild.value = parseFloat(a[i].firstChild.value).toFixed(2);
			// a[i].firstChild.value = parsePrice(a[i].firstChild.value);
}

/* On Content Load
/* ========================================================================== */

function onContentLoad() {
	updateInvoice();
	var currentDate = new Date();
	var formattedDate = currentDate.toLocaleDateString() + " (" + currentDate.toLocaleTimeString() + ")";
	// Update the value of the element with id "id_date"
	document.getElementById("id_date").value = formattedDate;

	var
	input = document.querySelector('input'),
	image = document.querySelector('img');

	function onClick(e) {
		var element = e.target.querySelector('[contenteditable]'), row;

		element && e.target != document.documentElement && e.target != document.body && element.focus();

		if (e.target.matchesSelector('.add')) {
			var tbody = document.querySelector('tbody.inventory'); // Get the tbody element with class "inventory"
			var firstRow = tbody.querySelector('tr:first-child'); // Get the first child <tr> element

			var newRow = firstRow.cloneNode(true); // Clone the firstRow with all its children
  			tbody.appendChild(newRow); // Append the newRow to the tbody
			// document.querySelector('tbody.inventory').appendChild(generateTableRow());
		}
		else if (e.target.className == 'cut') {
			row = e.target.ancestorQuerySelector('tr');
			if(row.parentNode.childElementCount>1){
				row.parentNode.removeChild(row);
			}
		}

		updateInvoice();
	}

	function onEnterCancel(e) {
		e.preventDefault();

		image.classList.add('hover');
	}

	function onLeaveCancel(e) {
		e.preventDefault();

		image.classList.remove('hover');
	}

	function onFileInput(e) {
		image.classList.remove('hover');

		var
		reader = new FileReader(),
		files = e.dataTransfer ? e.dataTransfer.files : e.target.files,
		i = 0;

		reader.onload = onFileLoad;

		while (files[i]) reader.readAsDataURL(files[i++]);
	}

	function onFileLoad(e) {
		var data = e.target.result;

		image.src = data;
	}

	if (window.addEventListener) {
		document.addEventListener('click', onClick);

		document.addEventListener('mousewheel', updateNumber);
		document.addEventListener('keydown', updateNumber);

		document.addEventListener('keydown', updateInvoice);
		document.addEventListener('keyup', updateInvoice);
	}
}

window.addEventListener && document.addEventListener('DOMContentLoaded', onContentLoad);

