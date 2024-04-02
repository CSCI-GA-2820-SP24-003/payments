const PAYMENT_METHOD_TYPE = {
  PAYPAL: "PAYPAL",
  CREDIT_CARD: "CREDIT_CARD",
};

const COMMON_FIELDS = [
  { name: "name" },
  { name: "type" },
  { name: "user_id", type: "int" },
];
const PAYPAL_FIELDS = [...COMMON_FIELDS, { name: "email" }];
const CREDIT_CARD_FIELDS = [
  ...COMMON_FIELDS,
  { name: "first_name" },
  { name: "last_name" },
  { name: "card_number" },
  { name: "expiry_month", type: "int" },
  { name: "expiry_year", type: "int" },
  { name: "security_code" },
  { name: "billing_address" },
  { name: "zip_code" },
];

const NOTIFICATION_CLOSE_DELAY = 5000; // 5 seconds for notifications to close

class Notifications {
  static counter = 0;

  static show({ type, message }) {
    if (type !== "error" && type !== "success") {
      throw new Error("Incorrect notification type passed");
    }

    const notificationContainer = document.getElementById(
      "notification-container"
    );

    const currentId = `${type}-notification-${++this.counter}`;

    notificationContainer.innerHTML += `<div class='notification ${type}' id='${currentId}'>${message}</div>`;

    setTimeout(() => {
      notificationContainer.removeChild(document.getElementById(currentId));
    }, NOTIFICATION_CLOSE_DELAY);
  }
}

function setupModal() {
  const NONE = "none";
  const FLEX = "flex";

  const dialog = document.querySelector("dialog");
  const dialogBackdrop = document.getElementById("dialog-backdrop");
  const closeDialogButton = document.getElementById("close-dialog");
  const dialogForm = document.getElementById("dialog-form");

  const dialogFormPayPalFields = document.getElementById(
    "dialog-form-paypal-fields"
  );

  const dialogFormCreditCardFields = document.getElementById(
    "dialog-form-credit-card-fields"
  );

  function open({ title, submitButtonText, onSubmit }) {
    document.getElementById("dialog-title").textContent = title;

    const submitButton = document.getElementById("dialog-form-submit");
    submitButton.textContent = submitButtonText;

    dialogForm.addEventListener("submit", async (event) => {
      const formBody = handleFormSubmit(event);

      await onSubmit(formBody);
    });

    dialogBackdrop.style.display = "block";
    dialog.show();
  }

  function close() {
    dialogForm.reset();
    dialog.close();
    dialogBackdrop.style.display = NONE;
    dialogFormPayPalFields.style.display = FLEX;
    dialogFormCreditCardFields.style.display = NONE;
  }

  function handlePaymentMethodTypeChange(event) {
    const isPayPalTypeSelected =
      event.target.value === PAYMENT_METHOD_TYPE.PAYPAL;

    dialogFormPayPalFields.style.display = isPayPalTypeSelected ? FLEX : NONE;
    dialogFormCreditCardFields.style.display = isPayPalTypeSelected
      ? NONE
      : FLEX;
  }

  function handleFormSubmit(event) {
    event.preventDefault();

    const fields =
      document.getElementById("type").value === PAYMENT_METHOD_TYPE.PAYPAL
        ? PAYPAL_FIELDS
        : CREDIT_CARD_FIELDS;

    // map form values to an object
    return fields.reduce((acc, curr) => {
      const { value } = document.getElementById(curr.name);
      acc[curr.name] = curr.type === "int" ? Number(value) : value;

      return acc;
    }, {});
  }

  // force reset the form so that the information is not persisted after reload
  window.addEventListener("beforeunload", () => dialogForm.reset());

  document
    .getElementById("type")
    .addEventListener("change", handlePaymentMethodTypeChange);

  closeDialogButton.addEventListener("click", () => close());

  return {
    open,
    close,
  };
}

const modal = setupModal();

async function onSubmitNewPayment(formBody) {
  const res = await fetch("/payments", {
    headers: { "Content-Type": "application/json" },
    method: "POST",
    body: JSON.stringify(formBody),
  });
  const data = await res.json();

  if (data.error) {
    return Notifications.show({ type: "error", message: data.error });
  }

  modal.close();
  Notifications.show({
    type: "success",
    message: `Added payment method with id: <span id="notification-payment-method-id">${data.id}</span>`,
  });
}

function openCreateNewPaymentMethodModal() {
  modal.open({
    title: "Create New Payment Method",
    submitButtonText: "Create",
    onSubmit: onSubmitNewPayment,
  });
}

function resetSearchResults() {
  document.getElementById("results-body").innerHTML = "";
}

// function removeSearchResult(elementId) {
//   document
//     .getElementById("results-body")
//     .removeChild(document.getElementById(elementId));
// }

function addSearchResult(payload) {
  const resultsBody = document.getElementById("results-body");
  const editButtonId = `edit-result-${payload.id}`;
  const deleteButtonId = `delete-result-${payload.id}`;

  const row = document.createElement("tr");

  row.id = `payment-method-${payload.id}`;
  row.innerHTML = `<td>${payload.id}</td>
    <td>${payload.type}</td>
    <td>${payload.name}</td>
    <td>${payload.user_id}</td>
    <td class="actions">
      <button id="${editButtonId}">Edit</button>
      <button id="${deleteButtonId}" class="delete">Delete</button>
    </td>`;

  resultsBody.appendChild(row);

  // handle edit payment method
  // document.getElementById(editButtonId).addEventListener("click", () => {
  //   openCreateNewPaymentMethodModal();
  // });

  // handle delete payment method
  // document.getElementById(deleteButtonId).addEventListener("click", () => {
  //   removeSearchResult(row.id);
  // });
}

document
  .getElementById("create-new-payment-method")
  .addEventListener("click", openCreateNewPaymentMethodModal);

document
  .getElementById("search-payment-methods")
  .addEventListener("click", async () => {
    // const type = document.getElementById("search-type");
    // const name = document.getElementById("search-name");
    // const userId = document.getElementById("search-user-id");

    const res = await fetch(`/payments`);
    const data = await res.json();

    if (data.error) {
      return Notifications.show({ type: "error", message: data.error });
    }

    resetSearchResults();
    data.forEach((paymentMethod) => addSearchResult(paymentMethod));
  });

document
  .getElementById("retrieve-payment-method")
  .addEventListener("click", async () => {
    const paymentMethodId = document.getElementById(
      "retrieve-payment-method-id"
    ).value;

    const res = await fetch(`/payments/${paymentMethodId}`);
    const data = await res.json();

    if (data.error) {
      return Notifications.show({ type: "error", message: data.error });
    }

    resetSearchResults();
    addSearchResult(data);
  });
