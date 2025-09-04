document.addEventListener('DOMContentLoaded',()=>{
  const toasts=document.querySelectorAll('.toast');
  toasts.forEach(el=>new bootstrap.Toast(el));

  const range=document.querySelector('#priceRange');
  const out=document.querySelector('#priceOut');
  if(range&&out){
    const sync=()=>out.textContent=`₹${Number(range.value).toLocaleString()}`;
    range.addEventListener('input',sync);sync();
  }

  const forms=document.querySelectorAll('form.needs-validation');
  Array.from(forms).forEach(form=>{
    form.addEventListener('submit',e=>{
      if(!form.checkValidity()){
        e.preventDefault();e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });
});
