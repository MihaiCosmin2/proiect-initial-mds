const signInForm = document.getElementById('sign-in-form');
  const signUpForm = document.getElementById('sign-up-form');

  const btnSignIn = document.getElementById('sign-in-button');
  const btnSignUp = document.getElementById('sign-up-button');

  btnSignIn.addEventListener('click', () => {
    signInForm.style.display = 'block';
    signUpForm.style.display = 'none';
  });

  btnSignUp.addEventListener('click', () => {
    signInForm.style.display = 'none';
    signUpForm.style.display = 'block';
  });


  btnSignIn.classList.add('btn-selected');

  btnSignIn.addEventListener('click', () => {
    btnSignIn.classList.add('btn-selected');
    btnSignUp.classList.remove('btn-selected');
  });

  btnSignUp.addEventListener('click', () => {
    btnSignUp.classList.add('btn-selected');
    btnSignIn.classList.remove('btn-selected');
  });