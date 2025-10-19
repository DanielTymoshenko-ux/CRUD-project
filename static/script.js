const API = 'http://127.0.0.1:5000/api';
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
document.getElementById('author').value = b.author;
document.getElementById('published_date').value = b.published_date || '';
document.getElementById('pages').value = b.pages;
document.getElementById('genre').value = b.genre || '';
document.getElementById('rating').value = b.rating != null ? b.rating : '';
}


function clearForm(){
document.getElementById('bookId').value = '';
document.getElementById('title').value = '';
document.getElementById('author').value = '';
document.getElementById('published_date').value = '';
document.getElementById('pages').value = '';
document.getElementById('genre').value = '';
document.getElementById('rating').value = '';
}


document.getElementById('saveBtn').addEventListener('click', saveBook);
document.getElementById('clearBtn').addEventListener('click', clearForm);
window.addEventListener('load', loadBooks);
