const API = 'http://127.0.0.1:5000/api';


async function loadBooks(){
const res = await fetch(`${API}/books`);
const books = await res.json();
const root = document.getElementById('books');
root.innerHTML = '';
books.forEach(b => {
const div = document.createElement('div');
div.className = 'book';
div.innerHTML = `
<b>${escapeHtml(b.title)}</b> — ${escapeHtml(b.author)}<br>
<small>Published: ${b.published_date || '-'} | ${b.pages} stron</small><br>
<small>Gatunek: ${escapeHtml(b.genre) || '-'} | Ocena: ${b.rating != null ? b.rating : '-'}</small><br>
<button onclick="editBook(${b.id})">Edytuj</button>
<button onclick="deleteBook(${b.id})">Usuń</button>`;
root.appendChild(div);
});
}


function escapeHtml(s){ if(s === null || s === undefined) return ''; return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }


async function saveBook(){
const id = document.getElementById('bookId').value;
const payload = {
title: document.getElementById('title').value,
author: document.getElementById('author').value,
published_date: document.getElementById('published_date').value || null,
pages: parseInt(document.getElementById('pages').value || 0),
genre: document.getElementById('genre').value || null,
rating: document.getElementById('rating').value ? parseFloat(document.getElementById('rating').value) : 0.0
};
if(!payload.title || !payload.author){alert('Wpisz tytuł i автора');return;}
if(payload.rating < 0 || payload.rating > 5){alert('Ocena musi być między 0 a 5');return;}
if(id){
const res = await fetch(`${API}/books/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
if(!res.ok) alert('Błąd aktualizacji');
} else {
const res = await fetch(`${API}/books`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
if(res.status !== 201) alert('Błąd tworzenia');
}
clearForm();
loadBooks();
}


async function deleteBook(id){
if(confirm('Usunąć książkę?')){
const res = await fetch(`${API}/books/${id}`,{method:'DELETE'});
if(res.status === 204) loadBooks(); else alert('Błąd usuwania');
}
}


async function editBook(id){
const res = await fetch(`${API}/books/${id}`);
if(!res.ok){ alert('Nie znaleziono'); return; }
const b = await res.json();
document.getElementById('bookId').value = b.id;
document.getElementById('title').value = b.title;
window.addEventListener('load', loadBooks);
