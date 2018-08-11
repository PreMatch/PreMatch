let list = [];

for (let i of document.querySelectorAll('table a'))
	if (!i.href.startsWith('mailto:'))
		list.push(i.innerText);

console.log(JSON.stringify(list));