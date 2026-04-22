export {};

const GOOGLE_FORM_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScGbvgjRJBzo9UjxF9YDJbIwv-aru2qy1QX3zPlSBLBIDf60w/formResponse';

const FIELD_MESSAGES: Record<string, { required: string; invalid?: string }> = {
  name: { required: 'Please fill out this field.' },
  email: {
    required: 'Please fill out this field.',
    invalid: 'Please enter a valid email address.',
  },
  subject: { required: 'Please select an item in the list.' },
  message: { required: 'Please fill out this field.' },
};

function ensureStatusElement(form: HTMLFormElement) {
  let statusDiv = form.querySelector('#form-status, [data-form-status]') as HTMLDivElement | null;
  if (statusDiv) return statusDiv;

  statusDiv = document.createElement('div');
  statusDiv.className = 'cf-status';
  statusDiv.dataset.formStatus = 'public';
  statusDiv.style.display = 'none';
  statusDiv.style.marginTop = '1rem';
  const submitBtn = form.querySelector('#submit-btn, button[type="submit"]');
  if (submitBtn?.parentElement === form) {
    form.insertBefore(statusDiv, submitBtn);
  } else {
    form.appendChild(statusDiv);
  }
  return statusDiv;
}

function getFieldContainer(field: HTMLElement) {
  return field.closest('.cf-field, .form-group') as HTMLElement | null;
}

function getFieldWarning(field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement) {
  const container = getFieldContainer(field) ?? field.parentElement;
  if (!container) return null;
  return container.querySelector('[data-field-warning]') as HTMLDivElement | null;
}

function setFieldError(
  field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement,
  message?: string,
) {
  const container = getFieldContainer(field);
  field.classList.add('field-invalid');
  field.setAttribute('aria-invalid', 'true');
  container?.classList.add('field-has-error');
  if (message) field.setCustomValidity(message);
}

function clearFieldError(field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement) {
  const warning = getFieldWarning(field);
  const container = getFieldContainer(field);
  field.classList.remove('field-invalid');
  field.removeAttribute('aria-invalid');
  field.setCustomValidity('');
  container?.classList.remove('field-has-error');
  if (warning) {
    warning.textContent = '';
    warning.style.display = 'none';
  }
}

function getValidationMessage(field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement) {
  const config = FIELD_MESSAGES[field.name] ?? { required: 'Required field.', invalid: 'Invalid value.' };
  if (field.validity.valueMissing) return config.required;
  if (field.validity.typeMismatch || field.validity.patternMismatch) {
    return config.invalid ?? 'Please enter a valid value.';
  }
  return 'Check this field.';
}

function syncNativeValidation(field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement) {
  clearFieldError(field);
  if (field.validity.valueMissing) {
    setFieldError(field, getValidationMessage(field));
    return false;
  }
  if (field.validity.typeMismatch || field.validity.patternMismatch) {
    setFieldError(field, getValidationMessage(field));
    return false;
  }
  return true;
}

function validateField(field: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement) {
  return syncNativeValidation(field);
}

function validateForm(form: HTMLFormElement): {
  valid: boolean;
  firstInvalidField: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null;
} {
  const fields = Array.from(
    form.querySelectorAll('input, select, textarea')
  ) as Array<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>;

  let firstInvalidField: HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null = null;
  fields.forEach(field => {
    if (!validateField(field) && !firstInvalidField) firstInvalidField = field;
  });
  return { valid: firstInvalidField === null, firstInvalidField };
}

function initContactForm(form: HTMLFormElement) {
  if (form.dataset.cfInit) return;
  form.dataset.cfInit = '1';

  const statusDiv = ensureStatusElement(form);
  const submitBtn = form.querySelector('#submit-btn, button[type="submit"]') as HTMLButtonElement | null;
  if (!submitBtn) return;

  const submitText = submitBtn.querySelector('.cf-submit-text') as HTMLElement | null;
  const defaultSubmitText = (submitText?.textContent ?? submitBtn.textContent ?? 'Send Message').trim();

  const fields = Array.from(
    form.querySelectorAll('input, select, textarea')
  ) as Array<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>;

  fields.forEach(field => {
    const eventName = field.tagName === 'SELECT' ? 'change' : 'input';
    field.addEventListener(eventName, () => validateField(field));
    field.addEventListener('blur', () => validateField(field));
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const { valid, firstInvalidField } = validateForm(form);
    if (!valid) {
      statusDiv.style.display = 'none';
      if (firstInvalidField) firstInvalidField.reportValidity();
      return;
    }

    submitBtn.disabled = true;
    if (submitText) submitText.textContent = 'Submitting...';
    else submitBtn.textContent = 'Submitting...';
    statusDiv.style.display = 'none';

    try {
      const fd = new FormData(form);
      const params = new URLSearchParams({
        'entry.285505795': (fd.get('name') as string) ?? '',
        'entry.283005138': (fd.get('email') as string) ?? '',
        'entry.154599738': (fd.get('subject') as string) ?? '',
        'entry.1712408064': (fd.get('message') as string) ?? '',
      });

      await fetch(GOOGLE_FORM_URL, { method: 'POST', mode: 'no-cors', body: params });

      form.reset();
      fields.forEach(field => clearFieldError(field));
      statusDiv.textContent = 'Your inquiry has been received. The Cyberfyx team will review it shortly.';
      statusDiv.style.backgroundColor = 'rgba(236, 240, 238, 0.95)';
      statusDiv.style.color = '#1f2933';
      statusDiv.style.border = '1px solid rgba(31, 41, 51, 0.05)';
      statusDiv.style.display = 'block';
    } catch (err) {
      console.error('Submission error:', err);
      statusDiv.innerHTML =
        'There was an error submitting your request. ' +
        'Please try again or <a href="mailto:sales@cyberfyx.net">email us directly</a>.';
      statusDiv.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';
      statusDiv.style.color = 'var(--accent-tertiary)';
      statusDiv.style.border = '1px solid rgba(255, 107, 53, 0.18)';
      statusDiv.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      if (submitText) submitText.textContent = defaultSubmitText;
      else submitBtn.textContent = defaultSubmitText;
    }
  });
}

function initContactForms() {
  const forms = Array.from(
    document.querySelectorAll('form[data-inquiry-form="public"], form#contact-form')
  ) as HTMLFormElement[];
  forms.forEach(form => initContactForm(form));
}

document.addEventListener('DOMContentLoaded', initContactForms);
document.addEventListener('astro:page-load', initContactForms);
