document.addEventListener('DOMContentLoaded', () => {

  // ===== ROLE & DOCUMENT LOGIC =====
  const roleSelect = document.getElementById('role-select');
  const employerTypeWrap = document.getElementById('employer-type-wrap');
  const employerTypeSelect = document.getElementById('employer-type-select');
  const jobseekerDocs = document.getElementById('jobseeker-docs');
  const employerDocs = document.getElementById('employer-docs');
  const companyDocs = document.getElementById('company-docs');
  const personalDocs = document.getElementById('personal-docs');

  function hideAllSections() {
    [jobseekerDocs, employerDocs, employerTypeWrap, companyDocs, personalDocs].forEach(el => {
      el?.classList.add('hidden');
      el?.classList.remove('show');
    });
  }

  roleSelect?.addEventListener('change', () => {
    hideAllSections();
    const role = roleSelect.value;

    if (role === 'JobSeeker') {
      jobseekerDocs.classList.remove('hidden');
      jobseekerDocs.classList.add('show');
    } else if (role === 'Employer') {
      employerTypeWrap.classList.remove('hidden');
      employerTypeWrap.classList.add('show');
      employerDocs.classList.remove('hidden');
      employerDocs.classList.add('show');
      employerTypeSelect.value = '';
      [companyDocs, personalDocs].forEach(el => el?.classList.add('hidden'));
    }
  });

  employerTypeSelect?.addEventListener('change', () => {
    [companyDocs, personalDocs].forEach(el => {
      el?.classList.add('hidden');
      el?.classList.remove('show');
    });

    if (employerTypeSelect.value === 'Company') {
      companyDocs.classList.remove('hidden');
      companyDocs.classList.add('show');
    } else if (employerTypeSelect.value === 'Personal') {
      personalDocs.classList.remove('hidden');
      personalDocs.classList.add('show');
    }
  });

  // ===== ACCORDION TOGGLES =====
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      header.parentElement.classList.toggle('open');
    });
  });

  // ===== OTP LOGIC =====
  const sendOtpBtn = document.getElementById('sendOtpBtn');
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  const otpGroup = document.querySelector('.otp-group');

  sendOtpBtn?.addEventListener('click', () => {
    const phone = document.getElementById('phone_number').value.trim();
    if (!phone) return alert('Enter phone number first');
    fetch(`/accounts/send_otp/?phone_number=${phone}`)
      .then(r => r.json())
      .then(data => {
        alert(data.message);
        if (data.status === 'ok') otpGroup.classList.remove('hidden');
      })
      .catch(() => alert('Error sending OTP'));
  });

  verifyOtpBtn?.addEventListener('click', () => {
    const phone = document.getElementById('phone_number').value.trim();
    const otp = document.getElementById('otpInput').value.trim();
    if (!otp) return alert('Enter OTP first');
    fetch(`/accounts/verify_otp/?phone_number=${phone}&otp=${otp}`)
      .then(r => r.json())
      .then(data => alert(data.status === 'ok' ? 'Phone verified!' : 'Invalid OTP'))
      .catch(() => alert('Verification failed'));
  });

  // ===== SOCIAL LOGIN PLACEHOLDERS =====
  document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const platform = btn.classList.contains('google') ? 'Google' : 'Facebook';
      alert(`Sign in with ${platform} coming soon!`);
    });
  });

  // ===== TAB SWITCH (Sign In / Register) =====
  const signinTab = document.getElementById('signin-tab');
  const registerTab = document.getElementById('register-tab');
  const signinForm = document.getElementById('signin-form');
  const registerForm = document.getElementById('register-form');

  function showSignIn() {
    signinTab.classList.add('active');
    registerTab.classList.remove('active');
    signinForm.classList.add('active');
    registerForm.classList.remove('active');
  }

  function showRegister() {
    registerTab.classList.add('active');
    signinTab.classList.remove('active');
    registerForm.classList.add('active');
    signinForm.classList.remove('active');
  }

  signinTab?.addEventListener('click', showSignIn);
  registerTab?.addEventListener('click', showRegister);
  document.getElementById('go-register')?.addEventListener('click', e => { e.preventDefault(); showRegister(); });
  document.getElementById('go-signin')?.addEventListener('click', e => { e.preventDefault(); showSignIn(); });

  // ===== URL PARAM HANDLER (?show=register) =====
  const params = new URLSearchParams(window.location.search);
  if (params.get('show') === 'register') {
    showRegister();
  }
});
