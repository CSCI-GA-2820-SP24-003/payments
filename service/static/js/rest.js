const BASE_URL = "/api/payments";

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

function getFieldsForType(type) {
  return type === PAYMENT_METHOD_TYPE.PAYPAL
    ? PAYPAL_FIELDS
    : CREDIT_CARD_FIELDS;
}

const NOTIFICATION_CLOSE_DELAY = 10000; // 10 seconds for notifications to close

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
  const dialogFormSubmitButton = document.getElementById("dialog-form-submit");

  const dialogFormPayPalFields = document.getElementById(
    "dialog-form-paypal-fields"
  );

  const dialogFormCreditCardFields = document.getElementById(
    "dialog-form-credit-card-fields"
  );

  // need to keep track of all intermediate event listener functions
  // so that we can remove them when we close the modal
  //
  // otherwise it can, for example, trigger multiple submits as there will be
  // multiple event listeners for click
  const eventListeners = {};

  function open({ title, submitButtonText, onSubmit, formBody }) {
    document.getElementById("dialog-title").textContent = title;

    eventListeners["dialogFormSubmitButton"] = { handleClick };

    dialogFormSubmitButton.textContent = submitButtonText;
    dialogFormSubmitButton.addEventListener("click", handleClick);

    dialogBackdrop.style.display = "block";
    dialog.show();
    dialog.style.visibility = "visible";

    if (formBody) {
      prefillFormBody(formBody);
    }

    async function handleClick(event) {
      event.preventDefault();
      const payload = handleFormSubmit();

      if (formBody) {
        payload.id = formBody.id;
      }

      await onSubmit(payload);
    }
  }

  function close() {
    dialogForm.reset();
    dialog.style.visibility = "hidden";
    dialog.close();
    dialogFormSubmitButton.removeEventListener(
      "click",
      eventListeners["dialogFormSubmitButton"].handleClick
    );
    dialogBackdrop.style.display = NONE;
    showFieldsFor(PAYMENT_METHOD_TYPE.PAYPAL);
  }

  function handleFormSubmit() {
    const type = document.getElementById("type").value;
    // map form values to an object
    return getFieldsForType(type).reduce((acc, curr) => {
      const { value } = document.getElementById(curr.name);
      acc[curr.name] = curr.type === "int" ? Number(value) : value;

      return acc;
    }, {});
  }

  function showFieldsFor(type) {
    const isPayPalTypeSelected = type === PAYMENT_METHOD_TYPE.PAYPAL;

    dialogFormPayPalFields.style.display = isPayPalTypeSelected ? FLEX : NONE;
    dialogFormCreditCardFields.style.display = isPayPalTypeSelected
      ? NONE
      : FLEX;
  }

  function prefillFormBody(formBody) {
    const { type } = formBody;
    showFieldsFor(type);
    getFieldsForType(type).forEach(
      ({ name }) => (document.getElementById(name).value = formBody[name])
    );
  }

  // force reset the form so that the information is not persisted after reload
  window.addEventListener("beforeunload", () => dialogForm.reset());

  document
    .getElementById("type")
    .addEventListener("change", (event) => showFieldsFor(event.target.value));

  closeDialogButton.addEventListener("click", () => close());

  return {
    open,
    close,
  };
}

const modal = setupModal();

async function onSubmitNewPayment(formBody) {
  const res = await fetch(BASE_URL, {
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

function removeSearchResult(elementId) {
  document
    .getElementById("results-body")
    .removeChild(document.getElementById(elementId));
}

async function onSubmitEditPayment(payload) {
  const { id, ...formBody } = payload;
  const res = await fetch(`${BASE_URL}/${id}`, {
    headers: { "Content-Type": "application/json" },
    method: "PUT",
    body: JSON.stringify(formBody),
  });
  const data = await res.json();

  if (data.error) {
    return Notifications.show({ type: "error", message: data.error });
  }

  addSearchResult(data, true);
  modal.close();
  Notifications.show({
    type: "success",
    message: `Edited payment method with id: <span id="notification-payment-method-id">${data.id}</span>`,
  });
}

function openEditPaymentMethod(payload) {
  modal.open({
    title: `Edit payment method "${payload.name}"`,
    submitButtonText: "Save",
    onSubmit: onSubmitEditPayment,
    formBody: payload,
  });
}

function setDefaultPaymentMethod({ id, userId }) {
  const resultsBody = document.getElementById("results-body");

  if (resultsBody.children.length === 0) {
    return;
  }

  for (const row of Array.from(resultsBody.children)) {
    const currRowId = Number(row.firstChild.textContent);
    const currRowUserId = Number(row.children[3].textContent);

    if (currRowId === id && currRowUserId === userId) {
      row.children[4].textContent = "true";
      continue;
    }

    if (currRowUserId === userId) {
      row.children[4].textContent = "false";
    }
  }
}

function addSearchResult(payload, replace) {
  const resultsBody = document.getElementById("results-body");
  const editButtonId = `edit-result-${payload.id}`;
  const deleteButtonId = `delete-result-${payload.id}`;
  const setDefaultButtonId = `set-default-${payload.id}`;
  const paymentMethodName = payload.name.toLowerCase().replaceAll(" ", "-");

  const row = document.createElement("tr");

  row.id = `payment-method-${payload.id}`;
  row.innerHTML = `<td id="${paymentMethodName}-id">${payload.id}</td>
    <td>${payload.type}</td>
    <td>${payload.name}</td>
    <td>${payload.user_id}</td>
    <td id="${paymentMethodName}-is-default">${payload.is_default}</td>
    <td class="actions">
      <button id="${editButtonId}">Edit</button>
      <button id="${setDefaultButtonId}">Set default</button>
      <button id="${deleteButtonId}" class="delete">Delete</button>
    </td>`;

  if (replace) {
    resultsBody.replaceChild(row, document.getElementById(row.id));
  } else {
    resultsBody.appendChild(row);
  }

  // handle edit payment method
  document.getElementById(editButtonId).addEventListener("click", () => {
    openEditPaymentMethod(payload);
  });

  // handle set default payment method
  document
    .getElementById(setDefaultButtonId)
    .addEventListener("click", async () => {
      const res = await fetch(`${BASE_URL}/${payload.id}/set-default`, {
        method: "PUT",
      });
      const data = await res.json();

      if (data.error) {
        return Notifications.show({
          type: "error",
          message:
            "An error occurred when trying to set a default payment method",
        });
      }

      setDefaultPaymentMethod({ id: data.id, userId: data.user_id });
      Notifications.show({
        type: "success",
        message: `Successfully set payment method with id ${data.id} as default`,
      });
    });

  // handle delete payment method
  document
    .getElementById(deleteButtonId)
    .addEventListener("click", async () => {
      try {
        await fetch(`${BASE_URL}/${payload.id}`, { method: "DELETE" });
        removeSearchResult(row.id);
        Notifications.show({
          type: "success",
          message: `Successfully deleted a payment method`,
        });
      } catch (e) {
        return Notifications.show({
          type: "error",
          message: "An error occurred when trying to remove a payment method",
        });
      }
    });
}

document
  .getElementById("create-new-payment-method")
  .addEventListener("click", openCreateNewPaymentMethodModal);

document
  .getElementById("search-payment-methods")
  .addEventListener("click", async () => {
    const type = document.getElementById("search-type");
    const name = document.getElementById("search-name");
    const userId = document.getElementById("search-user-id");

    const searchParams = new URLSearchParams();

    if (type.value !== "ANY") {
      searchParams.set("type", type.value);
    }

    if (name.value) {
      searchParams.set("name", name.value);
    }

    if (userId.value) {
      searchParams.set("user_id", Number(userId.value));
    }

    const searchString = searchParams.toString();
    const res = await fetch(
      `${BASE_URL}${searchString ? "?" + searchString : ""}`
    );
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

    const res = await fetch(`${BASE_URL}/${paymentMethodId}`);
    const data = await res.json();

    if (data.error) {
      return Notifications.show({ type: "error", message: data.error });
    }

    resetSearchResults();
    addSearchResult(data);
  });
